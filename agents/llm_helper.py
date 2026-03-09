"""
Shared LLM helper used by all agent nodes.

Wraps OpenAI chat completions with:
- A student-context-aware system prompt
- Graceful stub fallback when OPENAI_API_KEY is absent
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
) -> str:
    """
    Call OpenAI gpt-4o synchronously.
    Returns the model response text, or a stub message on failure.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("[LLM] OPENAI_API_KEY not set — using stub response.")
        return f"[STUB] {user_prompt[:120]}"

    try:
        from openai import OpenAI  # type: ignore
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:  # noqa: BLE001
        logger.error(f"[LLM] call failed: {exc}")
        if "insufficient_quota" in str(exc) or "429" in str(exc):
            return '{"error": "OpenAI API Quota Exceeded. Please check your billing details."}'
        if "invalid_api_key" in str(exc) or "401" in str(exc):
            return '{"error": "Invalid OpenAI API Key. Please check your .env file."}'
        return f"[LLM ERROR] {exc}"


def build_student_header(state: dict[str, Any]) -> str:
    """Create a concise student-context block for any system prompt."""
    p = state.get("student_profile", {})
    return (
        f"Student: {p.get('name', 'Unknown')} | "
        f"Grade: {p.get('current_grade')} | "
        f"Grad Year: {p.get('graduation_year')} | "
        f"GPA: {p.get('gpa')} | "
        f"SAT: {p.get('sat_score')} | ACT: {p.get('act_score')}\n"
        f"Target Schools: {', '.join(p.get('target_universities', [])) or 'Not set'}\n"
        f"Target Majors:  {', '.join(p.get('target_majors', [])) or 'Not set'}\n"
        f"Student ID: {state.get('student_id')}  ← Do NOT reference data from any other student."
    )
