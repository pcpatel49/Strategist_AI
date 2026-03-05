"""
Activities Coach Agent — suggests extracurricular activities based on the student's interests.

Safety: receives ONLY the pre-filtered state; issues no DB queries.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from agents.state import PlanningState
from agents.llm_helper import call_llm, build_student_header

logger = logging.getLogger(__name__)


def activities_coach_node(state: PlanningState) -> dict[str, Any]:
    """
    LangGraph node: ActivitiesCoachAgent.

    Input state keys used: student_id, student_profile, student_activities,
                           student_goals, query
    Output: {"activity_suggestions": List[str]}
    """
    student_id = state["student_id"]
    logger.info(f"[ActivitiesCoachAgent] Running for student {student_id}")

    system_prompt = f"""You are a college admissions extracurricular coach.
Your job is to suggest impactful activities for ONE specific student based on their profile.
Only reference data provided below — never infer data from other students.

{build_student_header(state)}
"""
    current_activities = [
        f"{a.get('activity_name')} ({a.get('category', 'general')}) — {a.get('role', 'member')}"
        for a in state.get("student_activities", [])
    ]

    user_prompt = f"""
Student query: {state['query']}

Current activities:
{json.dumps(current_activities, indent=1)}

Target majors: {state['student_profile'].get('target_majors', [])}
Target schools: {state['student_profile'].get('target_universities', [])}

Suggest 5 high-impact activities that:
1. Build on existing interests
2. Fill gaps for target schools
3. Include at least one leadership / community-service option

Return a plain JSON array of suggestion strings.
"""
    raw = call_llm(system_prompt, user_prompt, temperature=0.7)

    try:
        suggestions = json.loads(raw)
        if not isinstance(suggestions, list):
            suggestions = [str(suggestions)]
    except json.JSONDecodeError:
        suggestions = [line.strip("- ").strip() for line in raw.splitlines() if line.strip()]

    logger.info(f"[ActivitiesCoachAgent] {len(suggestions)} suggestions for student {student_id}")
    return {"activity_suggestions": suggestions}
