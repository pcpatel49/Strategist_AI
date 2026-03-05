"""
Academic Advisor Agent — recommends courses based on the student's history.

Safety: receives ONLY the pre-filtered state; issues no DB queries.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from agents.state import PlanningState
from agents.llm_helper import call_llm, build_student_header

logger = logging.getLogger(__name__)


def academic_advisor_node(state: PlanningState) -> dict[str, Any]:
    """
    LangGraph node: AcademicAdvisorAgent.

    Input state keys used: student_id, student_profile, student_courses,
                           student_goals, query, rag_context
    Output: {"course_recommendations": List[str]}
    """
    student_id = state["student_id"]
    logger.info(f"[AcademicAdvisorAgent] Running for student {student_id}")

    system_prompt = f"""You are a school academic counselor specialising in college-prep course selection.
Advise the following student on course selection. Use ONLY their data below.

{build_student_header(state)}

RAG University Context (for reference only):
{state.get('rag_context', '')[:600]}
"""
    taken = [c.get("course_name", "") for c in state.get("student_courses", [])]
    levels = list({c.get("course_level", "standard") for c in state.get("student_courses", [])})

    user_prompt = f"""
Student query: {state['query']}

Courses already taken: {json.dumps(taken)}
Course levels experienced: {levels}
Target majors: {state['student_profile'].get('target_majors', [])}

Recommend 5–8 specific courses the student should take next.
Return a plain JSON array of strings, e.g.: ["AP Calculus BC", "AP Computer Science A", ...]
"""
    raw = call_llm(system_prompt, user_prompt, temperature=0.5)

    try:
        recs = json.loads(raw)
        if not isinstance(recs, list):
            recs = [str(recs)]
    except json.JSONDecodeError:
        recs = [line.strip("- ").strip() for line in raw.splitlines() if line.strip()]

    logger.info(f"[AcademicAdvisorAgent] {len(recs)} course recs for student {student_id}")
    return {"course_recommendations": recs}
