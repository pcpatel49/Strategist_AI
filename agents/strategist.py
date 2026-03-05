"""
Strategist Agent — creates the student's 4-year college-prep plan.

Safety: receives ONLY the pre-filtered state; issues no DB queries.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from agents.state import PlanningState
from agents.llm_helper import call_llm, build_student_header

logger = logging.getLogger(__name__)


def strategist_node(state: PlanningState) -> dict[str, Any]:
    """
    LangGraph node: StrategistAgent.

    Input state keys used: student_id, student_profile, student_courses,
                           student_activities, student_goals, query, memories
    Output: {"plan": dict}
    """
    student_id = state["student_id"]
    logger.info(f"[StrategistAgent] Running for student {student_id}")

    system_prompt = f"""You are an expert college admissions strategist.
You are creating a personalized 4-year plan for ONE specific student.
Work ONLY with the data provided below — never invent or borrow data from other students.

{build_student_header(state)}

Memories: {chr(10).join(state.get('memories', []) or ['None'])}
RAG Context: {state.get('rag_context', '')[:800]}
"""
    courses_summary = json.dumps(state.get("student_courses", [])[:10], indent=1)
    activities_summary = json.dumps(state.get("student_activities", [])[:10], indent=1)

    user_prompt = f"""
Student query: {state['query']}

Current courses (max 10):
{courses_summary}

Current activities (max 10):
{activities_summary}

Respond with a JSON object:
{{
  "summary": "one-paragraph strategic overview",
  "semester_goals": {{"9th-Fall": ["goal1", ...], "9th-Spring": [...], ...}},
  "academic_track": "e.g. STEM / Humanities / Pre-Med",
  "priority_actions": ["action1", "action2", ...]
}}
"""
    raw = call_llm(system_prompt, user_prompt, temperature=0.6)

    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        # LLM didn't return valid JSON — wrap raw text
        plan = {
            "summary": raw,
            "semester_goals": {},
            "academic_track": "General",
            "priority_actions": [],
        }

    logger.info(f"[StrategistAgent] Plan generated for student {student_id}")
    return {"plan": plan}
