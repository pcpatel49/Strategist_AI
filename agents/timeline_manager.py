"""
Timeline Manager Agent — reviews the student's milestones and produces actionable updates.

Safety: receives ONLY the pre-filtered state; issues no DB queries.
"""
from __future__ import annotations

import json
import logging
from datetime import date
from typing import Any

from agents.state import PlanningState
from agents.llm_helper import call_llm, build_student_header

logger = logging.getLogger(__name__)


def timeline_manager_node(state: PlanningState) -> dict[str, Any]:
    """
    LangGraph node: TimelineManagerAgent.

    Inspects the plan produced by the StrategistAgent and converts semester
    goals into concrete milestone dicts that can be seeded into the DB.

    Input state keys used: student_id, student_profile, student_goals, plan, query
    Output: {"milestone_updates": List[dict]}
    """
    student_id = state["student_id"]
    logger.info(f"[TimelineManagerAgent] Running for student {student_id}")

    plan = state.get("plan", {})
    semester_goals = plan.get("semester_goals", {})

    if not semester_goals:
        # No plan yet — generate standalone timeline advice
        return {
            "milestone_updates": [
                {
                    "semester": "Next",
                    "title": "Generate your strategic plan first",
                    "description": "Call POST /api/plan/generate to create a full 4-year plan.",
                    "status": "pending",
                }
            ]
        }

    system_prompt = f"""You are a college-prep timeline manager.
Convert semester goals into concrete, prioritised milestones for ONE student.
Only use the data below — do NOT reference other students.

{build_student_header(state)}
"""
    today = date.today().isoformat()
    user_prompt = f"""
Today: {today}
Student query: {state['query']}

Semester goals from strategist:
{json.dumps(semester_goals, indent=2)}

For each semester that has goals, return a JSON array of milestone objects:
[
  {{
    "semester": "9th-Fall",
    "title": "Clear, actionable title",
    "description": "1–2 sentence detail",
    "status": "pending"
  }},
  ...
]
Return ONLY the JSON array.
"""
    raw = call_llm(system_prompt, user_prompt, temperature=0.4)

    try:
        milestones = json.loads(raw)
        if not isinstance(milestones, list):
            milestones = []
    except json.JSONDecodeError:
        # Fallback: synthesise directly from semester_goals without LLM
        milestones = [
            {
                "semester": sem,
                "title": goal,
                "description": f"Auto-generated from strategist plan for semester {sem}",
                "status": "pending",
            }
            for sem, goals in semester_goals.items()
            for goal in (goals if isinstance(goals, list) else [goals])
        ]

    logger.info(f"[TimelineManagerAgent] {len(milestones)} milestones for student {student_id}")
    return {"milestone_updates": milestones}
