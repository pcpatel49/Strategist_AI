"""
PlanningState — shared TypedDict that flows through every agent node.

student_id is the isolation anchor: every piece of data in this state was
fetched with a WHERE student_id = ? filter before the workflow started.
Agents receive this state and MUST NOT issue any DB queries of their own.
"""
from __future__ import annotations

from typing import Any, List, TypedDict


class PlanningState(TypedDict):
    # ── Identity (set once, never mutated by agents) ─────────────────────────
    student_id: str           # CRITICAL — identifies which student's data this is

    # ── Student data (pre-fetched, pre-filtered) ─────────────────────────────
    student_profile: dict[str, Any]        # from students table WHERE student_id = ?
    student_courses: List[dict[str, Any]]  # from courses  table WHERE student_id = ?
    student_activities: List[dict[str, Any]] # from activities WHERE student_id = ?
    student_goals: dict[str, Any]          # subset of profile (universities, majors)

    # ── Query & external context ─────────────────────────────────────────────
    query: str                             # original user question / intent

    rag_context: str                       # combined_text from CombinedRAGSystem
    memories: List[str]                    # from Mem0 search(student_id, query)

    # ── Agent outputs (populated as the graph progresses) ────────────────────
    plan: dict[str, Any]                   # StrategistAgent output
    course_recommendations: List[str]      # AcademicAdvisorAgent output
    activity_suggestions: List[str]        # ActivitiesCoachAgent output
    university_insights: List[str]         # ResearchAgent output
    milestone_updates: List[dict[str, Any]] # TimelineManagerAgent output
    recommendations: List[str]             # merged final recommendations
