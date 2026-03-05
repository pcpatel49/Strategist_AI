"""
Research Agent — synthesizes RAG university data into student-specific insights.

Safety: receives ONLY the pre-filtered state; issues no DB queries.
The RAG context was already fetched with student_id isolation before this node runs.
"""
from __future__ import annotations

import logging
from typing import Any

from agents.state import PlanningState
from agents.llm_helper import call_llm, build_student_header

logger = logging.getLogger(__name__)


def research_node(state: PlanningState) -> dict[str, Any]:
    """
    LangGraph node: ResearchAgent.

    Input state keys used: student_id, student_profile, student_goals,
                           rag_context, query
    Output: {"university_insights": List[str]}
    """
    student_id = state["student_id"]
    logger.info(f"[ResearchAgent] Running for student {student_id}")

    rag_text = state.get("rag_context", "")
    if not rag_text or rag_text.startswith("[STUB]"):
        logger.warning("[ResearchAgent] No real RAG context available — skipping LLM call.")
        return {
            "university_insights": [
                "Connect PINECONE_API_KEY to get real university admission insights."
            ]
        }

    system_prompt = f"""You are a college research specialist.
Analyse the provided university data and extract specific, actionable insights
for the following student. Do NOT reference any other student's data.

{build_student_header(state)}
"""
    user_prompt = f"""
Student query: {state['query']}

University/document data (from RAG):
{rag_text[:1500]}

Extract 4–6 specific insights relevant to this student's target schools and majors.
Return a plain JSON array of concise insight strings.
"""
    raw = call_llm(system_prompt, user_prompt, temperature=0.4)

    try:
        import json
        insights = json.loads(raw)
        if not isinstance(insights, list):
            insights = [str(insights)]
    except Exception:  # noqa: BLE001
        insights = [line.strip("- ").strip() for line in raw.splitlines() if line.strip()]

    logger.info(f"[ResearchAgent] {len(insights)} insights for student {student_id}")
    return {"university_insights": insights}
