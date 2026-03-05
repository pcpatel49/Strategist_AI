"""
Recommendation Merger — final node in the LangGraph workflow.

Collects outputs from all specialist agents and merges them into
a flat `recommendations` list that is returned to the caller.
No LLM call needed here — this is pure data assembly.
"""
from __future__ import annotations

import logging
from typing import Any

from agents.state import PlanningState

logger = logging.getLogger(__name__)


def merger_node(state: PlanningState) -> dict[str, Any]:
    """
    LangGraph node: MergerAgent (deterministic — no LLM).

    Collects:
      - plan["priority_actions"]
      - course_recommendations
      - activity_suggestions
      - university_insights

    Returns: {"recommendations": List[str]}
    """
    student_id = state["student_id"]
    logger.info(f"[MergerAgent] Merging recommendations for student {student_id}")

    merged: list[str] = []

    plan = state.get("plan", {})
    for action in plan.get("priority_actions", []):
        merged.append(f"[Strategic] {action}")

    for rec in state.get("course_recommendations", []):
        merged.append(f"[Academic] {rec}")

    for sug in state.get("activity_suggestions", []):
        merged.append(f"[Activity] {sug}")

    for insight in state.get("university_insights", []):
        merged.append(f"[Research] {insight}")

    logger.info(f"[MergerAgent] {len(merged)} total recommendations for student {student_id}")
    return {"recommendations": merged}
