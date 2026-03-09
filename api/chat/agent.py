"""
AI agent that processes a chat message and returns a response.
Keeps the LLM interaction isolated to the student's context package.

Swap `_call_openai_stub` for a real LangChain / LangGraph agent when ready.
"""
from __future__ import annotations

import json
import logging
import os
from openai import OpenAI, AsyncOpenAI
from typing import Any, AsyncGenerator

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are an expert college admissions advisor and strategic planner.
You are speaking with a specific student. You MUST only use the information provided below and
MUST NOT reference or infer data from any other student.

--- STUDENT PROFILE ---
{profile}

--- COURSES ---
{courses}

--- EXTRACURRICULARS ---
{activities}

--- STRATEGIC PLAN SUMMARY ---
{plan_summary}

--- RELEVANT MEMORIES ---
{memories}

Always give personalised, specific advice based solely on the above student data.
"""


def build_system_prompt(context: dict[str, Any]) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(
        profile=json.dumps(context["profile"], indent=2),
        courses=json.dumps(context["courses"], indent=2),
        activities=json.dumps(context["activities"], indent=2),
        plan_summary=json.dumps(context.get("plan_summary"), indent=2),
        memories="\n".join(context.get("relevant_memories", [])) or "None yet.",
    )


def chat_with_ai(context: dict[str, Any], user_message: str) -> str:
    """
    Call the AI model with the isolated student context.
    Returns the full assistant reply as a string.

    Production: replace the stub with an actual OpenAI / Anthropic call.
    """
    try:
        return _call_openai(context, user_message)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"AI call failed, falling back to stub: {exc}")
        return _stub_response(context, user_message)


async def stream_chat_with_ai(
    context: dict[str, Any], user_message: str
) -> AsyncGenerator[str, None]:
    """
    Async generator that streams the AI response token-by-token.
    Used by the WebSocket endpoint.
    """
    try:
        async for chunk in _stream_openai(context, user_message):
            yield chunk
    except Exception as exc:  # noqa: BLE001
        logger.error(f"AI streaming failed: {exc}")
        yield _stub_response(context, user_message)


# ---------------------------------------------------------------------------
# OpenAI implementation (comment in when OPENAI_API_KEY is present)
# ---------------------------------------------------------------------------
def _call_openai(context: dict[str, Any], user_message: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        messages = [
            {"role": "system", "content": build_system_prompt(context)},
            *context["chat_history"],
            {"role": "user", "content": user_message},
        ]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        if "insufficient_quota" in str(exc) or "429" in str(exc):
            return '{"error": "OpenAI API Quota Exceeded. Please check your billing details."}'
        if "invalid_api_key" in str(exc) or "401" in str(exc):
            return '{"error": "Invalid OpenAI API Key. Please check your .env file."}'
        raise exc


async def _stream_openai(
    context: dict[str, Any], user_message: str
) -> AsyncGenerator[str, None]:
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        messages = [
            {"role": "system", "content": build_system_prompt(context)},
            *context["chat_history"],
            {"role": "user", "content": user_message},
        ]
        async with client.chat.completions.stream(
            model="gpt-4o",
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text
    except Exception as exc:
        if "insufficient_quota" in str(exc) or "429" in str(exc):
            yield '{"error": "OpenAI API Quota Exceeded. Please check your billing details."}'
        elif "invalid_api_key" in str(exc) or "401" in str(exc):
            yield '{"error": "Invalid OpenAI API Key. Please check your .env file."}'
        else:
            raise exc


# ---------------------------------------------------------------------------
# Stub fallback (always works, no API key required)
# ---------------------------------------------------------------------------
def _stub_response(context: dict[str, Any], user_message: str) -> str:
    name = context["profile"].get("name", "Student")
    gpa = context["profile"].get("gpa")
    schools = context["profile"].get("target_universities", [])

    gpa_note = f"Your current GPA is {gpa}." if gpa else ""
    schools_note = (
        f"You are targeting: {', '.join(schools[:3])}."
        if schools
        else "You haven't set target schools yet."
    )

    return (
        f"Hi {name}! You asked: \"{user_message}\"\n\n"
        f"{gpa_note} {schools_note}\n\n"
        "This is a stub response — connect OPENAI_API_KEY in your .env to get "
        "real AI-powered advice tailored exclusively to your profile."
    )
