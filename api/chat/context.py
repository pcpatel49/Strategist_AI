"""
Context assembler for the AI chat agent.

Builds a fully isolated, student-scoped context dictionary from the database
and Mem0. The AI agent receives ONLY this dict — it never cross-contaminates
between students.
"""
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from database.models import ChatMessage, Course, Activity, Student, StrategicPlan
from memory.mem0_client import memory_manager
from rag.combined_rag import rag_system

logger = logging.getLogger(__name__)

CHAT_HISTORY_LIMIT = 20   # last N messages passed to the LLM
MEMORY_SEARCH_LIMIT = 5   # top-K Mem0 results


def build_student_context(
    student_id: str,
    user_message: str,
    db: Session,
) -> dict[str, Any]:
    """
    Assemble an isolated context package for the AI agent.

    Every query is filtered by ``student_id`` — no other student's data
    can bleed through.

    Returns
    -------
    dict with keys:
        student_id, profile, courses, activities, plan_summary,
        chat_history, relevant_memories
    """

    # ── 1. Profile ────────────────────────────────────────────────────────────
    student: Student | None = (
        db.query(Student).filter(Student.student_id == student_id).first()
    )
    if not student:
        raise ValueError(f"No student profile found for student_id={student_id}")

    profile = {
        "name": f"{student.first_name} {student.last_name}",
        "current_grade": student.current_grade,
        "graduation_year": student.graduation_year,
        "gpa": student.gpa,
        "sat_score": student.sat_score,
        "act_score": student.act_score,
        "target_universities": student.target_universities or [],
        "target_majors": student.target_majors or [],
    }

    # ── 2. Courses ────────────────────────────────────────────────────────────
    courses = [
        {
            "course_name": c.course_name,
            "course_level": c.course_level,
            "grade": c.grade,
            "credits": c.credits,
            "semester": c.semester,
            "year": c.year,
        }
        for c in db.query(Course).filter(Course.student_id == student_id).all()
    ]

    # ── 3. Activities ────────────────────────────────────────────────────────
    activities = [
        {
            "activity_name": a.activity_name,
            "category": a.category,
            "role": a.role,
            "hours_per_week": a.hours_per_week,
            "achievements": a.achievements or [],
        }
        for a in db.query(Activity).filter(Activity.student_id == student_id).all()
    ]

    # ── 4. Plan summary ──────────────────────────────────────────────────────
    plan: StrategicPlan | None = (
        db.query(StrategicPlan)
        .filter(StrategicPlan.student_id == student_id)
        .first()
    )
    plan_summary = None
    if plan and plan.plan_data:
        pd = plan.plan_data
        plan_summary = {
            "summary": pd.get("summary"),
            "target_schools": pd.get("target_schools", []),
            "target_majors": pd.get("target_majors", []),
            "academic_recommendations": pd.get("academic_recommendations", []),
            "activity_recommendations": pd.get("activity_recommendations", []),
        }

    # ── 5. Chat history (last N messages, chronological) ─────────────────────
    recent_msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.student_id == student_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(CHAT_HISTORY_LIMIT)
        .all()
    )
    chat_history = [
        {"role": m.role, "content": m.content}
        for m in reversed(recent_msgs)   # oldest first for the LLM
    ]

    # ── 6. Relevant memories from Mem0 ───────────────────────────────────────
    raw_memories = memory_manager.search_memory(student_id, user_message, limit=MEMORY_SEARCH_LIMIT)
    # Mem0 returns list of {"memory": str, ...} dicts
    relevant_memories = [
        m.get("memory", str(m)) for m in raw_memories[:MEMORY_SEARCH_LIMIT]
    ]

    # ── 7. RAG: shared university data + student's private documents ──────────
    rag_context = rag_system.query_for_student(
        student_id=student_id,
        query=user_message,
        # Pass the first target university as an optional filter hint
        university_filter=(
            profile["target_universities"][0]
            if profile["target_universities"]
            else None
        ),
    )

    return {
        "student_id": student_id,
        "profile": profile,
        "courses": courses,
        "activities": activities,
        "plan_summary": plan_summary,
        "chat_history": chat_history,
        "relevant_memories": relevant_memories,
        "rag_university": rag_context["university_results"],
        "rag_private_docs": rag_context["student_results"],
        "rag_combined_text": rag_context["combined_text"],
    }
