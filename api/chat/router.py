from typing import List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from auth.dependencies import get_current_student
from auth.security import SECRET_KEY, ALGORITHM, is_token_blacklisted
from database.database import get_db
from database.models import ChatMessage
from api.chat.schemas import ChatMessageRequest, ChatMessageResponse, ChatResponse
from api.chat.context import build_student_context
from api.chat.agent import chat_with_ai, stream_chat_with_ai

router = APIRouter(tags=["Chat"])

HISTORY_LIMIT = 50


# ---------------------------------------------------------------------------
# POST /api/chat  — send a message and get an AI response
# ---------------------------------------------------------------------------
@router.post("/chat", response_model=ChatResponse)
def send_message(
    payload: ChatMessageRequest,
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    1. Persist the user message (tagged with the authenticated student_id).
    2. Build an isolated context package from the DB + Mem0.
    3. Call the AI agent — it only sees THIS student's data.
    4. Persist the AI response (also tagged with student_id).
    5. Return the AI answer.
    """
    # Save user message
    user_msg = ChatMessage(
        student_id=student_id,
        role="user",
        content=payload.content,
    )
    db.add(user_msg)
    db.commit()

    # Build isolated context and call AI
    try:
        context = build_student_context(student_id, payload.content, db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    ai_answer = chat_with_ai(context, payload.content)

    # Save AI response
    ai_msg = ChatMessage(
        student_id=student_id,
        role="assistant",
        content=ai_answer,
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return ChatResponse(answer=ai_answer, message_id=ai_msg.id)


# ---------------------------------------------------------------------------
# GET /api/chat/history  — fetch last 50 messages
# ---------------------------------------------------------------------------
@router.get("/chat/history", response_model=List[ChatMessageResponse])
def get_history(
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Return the last 50 chat messages for the authenticated student.
    Ordered chronologically (oldest first) so the client can render a thread.
    """
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.student_id == student_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
    # Reverse to chronological order for the client
    return list(reversed(messages))


# ---------------------------------------------------------------------------
# WS /ws/chat  — streaming WebSocket endpoint
# ---------------------------------------------------------------------------
async def _authenticate_ws(token: str, db: Session) -> str | None:
    """
    Validate the JWT passed as a query parameter on the WebSocket connection.
    Returns student_id string on success, None on failure.
    """
    if not token:
        return None
    if is_token_blacklisted(db, token):
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        student_id = payload.get("student_id")
        return str(student_id) if student_id else None
    except JWTError:
        return None


router_ws = APIRouter(tags=["Chat WebSocket"])


@router_ws.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: str | None = None,          # passed as ?token=<jwt> in the URL
    db: Session = Depends(get_db),
):
    """
    Streaming WebSocket chat endpoint.

    Connection: ws://host/ws/chat?token=<JWT>

    Protocol (JSON frames):
      Client → Server : {"content": "your question here"}
      Server → Client : {"type": "chunk",  "data": "<token>"}   (streaming)
      Server → Client : {"type": "done",   "data": ""}           (end of stream)
      Server → Client : {"type": "error",  "data": "<message>"}  (on failure)
      Server → Client : {"type": "saved",  "message_id": <int>}  (after persist)
    """
    await websocket.accept()

    # Authenticate
    student_id = await _authenticate_ws(token or "", db)
    if not student_id:
        await websocket.send_json({"type": "error", "data": "Unauthorized"})
        await websocket.close(code=4001)
        return

    try:
        while True:
            data = await websocket.receive_json()
            user_content: str = data.get("content", "").strip()

            if not user_content:
                await websocket.send_json({"type": "error", "data": "Empty message"})
                continue

            # Persist user message
            user_msg = ChatMessage(
                student_id=student_id,
                role="user",
                content=user_content,
            )
            db.add(user_msg)
            db.commit()

            # Build isolated context
            try:
                context = build_student_context(student_id, user_content, db)
            except ValueError as exc:
                await websocket.send_json({"type": "error", "data": str(exc)})
                continue

            # Stream AI response token by token
            full_response = ""
            async for chunk in stream_chat_with_ai(context, user_content):
                full_response += chunk
                await websocket.send_json({"type": "chunk", "data": chunk})

            await websocket.send_json({"type": "done", "data": ""})

            # Persist AI response
            ai_msg = ChatMessage(
                student_id=student_id,
                role="assistant",
                content=full_response,
            )
            db.add(ai_msg)
            db.commit()
            db.refresh(ai_msg)

            await websocket.send_json({"type": "saved", "message_id": ai_msg.id})

    except WebSocketDisconnect:
        pass  # clean disconnect
    except Exception as exc:
        try:
            await websocket.send_json({"type": "error", "data": str(exc)})
            await websocket.close()
        except Exception:
            pass
