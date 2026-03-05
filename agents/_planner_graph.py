"""
LangGraph Planning Workflow — the full multi-agent graph.

Graph topology:
  research_node ──┐
  academic_advisor_node ──┤
                          ├──> strategist_node ──> timeline_manager_node ──> merger_node
  activities_coach_node ──┘

The first three agents run in PARALLEL (fan-out), then strategist uses their
output to build the plan, then timeline manager and merger finalize everything.

Entry point: run_planning_workflow(student_id, query, db)
"""
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from agents.state import PlanningState
from agents.strategist import strategist_node
from agents.academic_advisor import academic_advisor_node
from agents.activities_coach import activities_coach_node
from agents.research_agent import research_node
from agents.timeline_manager import timeline_manager_node
from agents.merger import merger_node
from memory.mem0_client import memory_manager
from rag.combined_rag import rag_system
from database.models import Student, Course, Activity, StrategicPlan

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Build the LangGraph StateGraph
# ---------------------------------------------------------------------------
def _build_graph():
    """
    Compile and return the planning StateGraph.
    Import `langgraph` lazily so the rest of the app works even if it's not installed.
    """
    try:
        from langgraph.graph import StateGraph, END  # type: ignore

        workflow = StateGraph(PlanningState)

        # Register nodes
        workflow.add_node("research",          research_node)
        workflow.add_node("academic_advisor",  academic_advisor_node)
        workflow.add_node("activities_coach",  activities_coach_node)
        workflow.add_node("strategist",        strategist_node)
        workflow.add_node("timeline_manager",  timeline_manager_node)
        workflow.add_node("merger",            merger_node)

        # Fan-out: three parallel specialist agents
        workflow.set_entry_point("research")
        workflow.add_edge("research",         "academic_advisor")
        workflow.add_edge("academic_advisor", "activities_coach")
        # Strategist waits until all three have written into state
        # (For true parallelism use Send API; simple chain is easier to debug)
        workflow.add_edge("activities_coach", "strategist")

        # Sequential finalisation
        workflow.add_edge("strategist",       "timeline_manager")
        workflow.add_edge("timeline_manager", "merger")
        workflow.add_edge("merger",           END)

        return workflow.compile()

    except ImportError:
        logger.warning("langgraph not installed — planning graph unavailable.")
        return None


_planning_graph = None   # lazy singleton


def _get_graph():
    global _planning_graph
    if _planning_graph is None:
        _planning_graph = _build_graph()
    return _planning_graph


# ---------------------------------------------------------------------------
# Data loaders — all filtered by student_id
# ---------------------------------------------------------------------------
def _load_profile(student: Student) -> dict[str, Any]:
    return {
        "name": f"{student.first_name} {student.last_name}",
        "current_grade": student.current_grade,
        "graduation_year": student.graduation_year,
        "gpa": student.gpa,
        "sat_score": student.sat_score,
        "act_score": student.act_score,
        "target_universities": student.target_universities or [],
        "target_majors": student.target_majors or [],
    }


def _load_courses(db: Session, student_id: str) -> list[dict]:
    return [
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


def _load_activities(db: Session, student_id: str) -> list[dict]:
    return [
        {
            "activity_name": a.activity_name,
            "category": a.category,
            "role": a.role,
            "hours_per_week": a.hours_per_week,
            "achievements": a.achievements or [],
        }
        for a in db.query(Activity).filter(Activity.student_id == student_id).all()
    ]


# ---------------------------------------------------------------------------
# Safety guard — called before building initial state
# ---------------------------------------------------------------------------
def _assert_isolation(student_id: str, student: Student) -> None:
    """
    Hard assertion: verify the DB row's student_id matches the JWT-derived student_id.
    If these ever differ, it means a serious bug — raise immediately.
    """
    if str(student.student_id) != str(student_id):
        raise PermissionError(
            f"ISOLATION VIOLATION: JWT student_id={student_id} "
            f"!= DB student_id={student.student_id}"
        )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
async def run_planning_workflow(
    student_id: str,
    query: str,
    db: Session,
) -> dict[str, Any]:
    """
    Fetch ALL data for the given student, build isolated state, run the graph.

    Parameters
    ----------
    student_id : str   From JWT — never from request body.
    query      : str   User's question or planning intent.
    db         : Session  SQLAlchemy session for data loading.

    Returns
    -------
    Final PlanningState dict with 'plan', 'recommendations', 'milestone_updates', etc.
    """
    # 1. Load and validate student — SAFETY CHECK
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise ValueError(f"Student not found: {student_id}")
    _assert_isolation(student_id, student)

    # 2. Load all context filtered by student_id
    profile = _load_profile(student)
    courses = _load_courses(db, student_id)
    activities = _load_activities(db, student_id)

    goals = {
        "target_universities": profile["target_universities"],
        "target_majors": profile["target_majors"],
    }

    # 3. Mem0 memories for this student only
    raw_memories = memory_manager.search_memory(student_id, query, limit=8)
    memories = [m.get("memory", str(m)) for m in raw_memories]

    # 4. RAG: shared university data + student's private documents, both filtered
    rag_result = rag_system.query_for_student(student_id=student_id, query=query)
    rag_context = rag_result["combined_text"]

    # 5. Build initial state — student_id is the isolation anchor
    initial_state: PlanningState = {
        "student_id": student_id,
        "student_profile": profile,
        "student_courses": courses,
        "student_activities": activities,
        "student_goals": goals,
        "query": query,
        "rag_context": rag_context,
        "memories": memories,
        # Agent outputs — empty until nodes run
        "plan": {},
        "course_recommendations": [],
        "activity_suggestions": [],
        "university_insights": [],
        "milestone_updates": [],
        "recommendations": [],
    }

    # 6. Run graph
    graph = _get_graph()
    if graph is None:
        # langgraph not installed — run nodes manually in sequence
        logger.warning("LangGraph unavailable — running agent nodes sequentially as fallback.")
        state: dict[str, Any] = dict(initial_state)
        for node_fn in [
            research_node,
            academic_advisor_node,
            activities_coach_node,
            strategist_node,
            timeline_manager_node,
            merger_node,
        ]:
            state.update(node_fn(state))  # type: ignore[arg-type]
        return state

    result = await graph.ainvoke(initial_state)
    logger.info(f"[PlanningWorkflow] Completed for student {student_id}")
    return result
