from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_student
from database.database import get_db
from database.models import StudentDocument
from api.documents.schemas import DocumentUploadResponse, UniversitySearchResponse
from rag.combined_rag import rag_system

router = APIRouter(tags=["Documents & University Search"])


# ---------------------------------------------------------------------------
# POST /api/documents/upload
# ---------------------------------------------------------------------------
@router.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    doc_name: str = Form(...),
    file: UploadFile = File(...),
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Upload a document to the student's PRIVATE Pinecone space.
    student_id from JWT is written into Pinecone metadata — never from the form body.
    Also creates a DB row so the student can list and delete their documents by ID.
    """
    content_bytes = await file.read()
    try:
        content = content_bytes.decode("utf-8", errors="replace")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not decode file content. Only text-based files are supported.",
        )

    # Upsert to Pinecone — student_id embedded in metadata by StudentDocumentRAG
    vector_id = rag_system.add_student_document(
        student_id=student_id,
        doc_name=doc_name,
        content=content,
    )

    # Persist DB record so the student can manage their documents
    db_doc = StudentDocument(
        student_id=student_id,
        doc_name=doc_name,
        vector_id=vector_id,
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    return db_doc


# ---------------------------------------------------------------------------
# GET /api/documents
# ---------------------------------------------------------------------------
@router.get("/documents", response_model=List[DocumentUploadResponse])
def list_documents(
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """List all documents uploaded by the authenticated student."""
    return (
        db.query(StudentDocument)
        .filter(StudentDocument.student_id == student_id)
        .order_by(StudentDocument.created_at.desc())
        .all()
    )


# ---------------------------------------------------------------------------
# DELETE /api/documents/{doc_id}
# ---------------------------------------------------------------------------
@router.delete("/documents/{doc_id}", response_model=dict)
def delete_document(
    doc_id: int,
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Delete a private document.
    Verifies DB ownership before deleting from Pinecone — prevents cross-student deletion.
    """
    db_doc = db.query(StudentDocument).filter(StudentDocument.id == doc_id).first()

    if not db_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if str(db_doc.student_id) != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to delete this document",
        )

    # Delete from Pinecone first
    rag_system.delete_student_document(db_doc.vector_id)

    # Then remove DB record
    db.delete(db_doc)
    db.commit()

    return {"message": f"Document '{db_doc.doc_name}' deleted successfully"}


# ---------------------------------------------------------------------------
# GET /api/universities/search
# ---------------------------------------------------------------------------
@router.get("/universities/search", response_model=List[UniversitySearchResponse])
def search_universities(
    q: str = Query(..., description="Search query, e.g. 'MIT computer science requirements'"),
    university: Optional[str] = Query(None, description="Filter results by university name"),
    student_id: str = Depends(get_current_student),   # auth required, but NOT used in query
    db: Session = Depends(get_db),
):
    """
    Search the shared university reference index.
    Any authenticated student can query — no student_id filtering applied to results.
    """
    results = rag_system.university_rag.query_university(
        query=q,
        university_filter=university,
    )
    return [
        UniversitySearchResponse(
            text=r["text"],
            university=r["university"],
            doc_type=r.get("doc_type"),
            score=r["score"],
        )
        for r in results
    ]
