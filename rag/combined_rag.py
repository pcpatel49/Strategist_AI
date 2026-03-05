"""
CombinedRAGSystem — merges shared university data with the student's private documents.

Usage in chat:
    rag = CombinedRAGSystem()
    context = rag.query_for_student(student_id="<uuid>", query="How do I improve my SAT score?")
    # context["university_results"]  — public university data
    # context["student_results"]     — only this student's private docs
    # context["combined_text"]       — ready-to-inject string for the AI prompt
"""
from __future__ import annotations

from typing import Any, Optional

from rag.university_rag import UniversityRAG
from rag.student_rag import StudentDocumentRAG


class CombinedRAGSystem:
    """
    Facade that queries both RAG indexes and merges the results.

    Public data (UniversityRAG)  — searched without student_id.
    Private data (StudentDocumentRAG) — always filtered by student_id.
    """

    def __init__(self) -> None:
        self.university_rag = UniversityRAG()
        self.student_rag = StudentDocumentRAG()

    def query_for_student(
        self,
        student_id: str,
        query: str,
        university_filter: Optional[str] = None,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """
        Parallel-style query over both indexes.
        Returns a dict with individually accessible result lists AND a
        pre-formatted `combined_text` string for injecting into the AI prompt.
        """
        # 1. Shared university data — student_id irrelevant
        university_results = self.university_rag.query_university(
            query=query,
            university_filter=university_filter,
            top_k=top_k,
        )

        # 2. Private student documents — always filtered by student_id
        student_results = self.student_rag.query_student_documents(
            student_id=student_id,
            query=query,
            top_k=top_k,
        )

        combined_text = _format_combined(university_results, student_results)

        return {
            "university_results": university_results,
            "student_results": student_results,
            "combined_text": combined_text,
        }

    # ------------------------------------------------------------------ shortcuts
    def add_student_document(self, student_id: str, doc_name: str, content: str) -> str:
        return self.student_rag.add_student_document(student_id, doc_name, content)

    def delete_student_document(self, vector_id: str) -> bool:
        return self.student_rag.delete_student_document(vector_id)

    def delete_all_student_documents(self, student_id: str) -> bool:
        return self.student_rag.delete_all_student_documents(student_id)

    def ingest_university_document(
        self, text: str, university: str, doc_type: str = "general"
    ) -> str:
        return self.university_rag.ingest_university_document(text, university, doc_type)


# ---------------------------------------------------------------------------
# Internal formatter
# ---------------------------------------------------------------------------
def _format_combined(
    university_results: list[dict],
    student_results: list[dict],
) -> str:
    sections: list[str] = []

    if university_results:
        sections.append("=== University Reference Data ===")
        for r in university_results:
            sections.append(
                f"[{r.get('university', 'Unknown')} | {r.get('doc_type', '')}]\n{r['text']}"
            )

    if student_results:
        sections.append("\n=== Your Private Documents ===")
        for r in student_results:
            sections.append(f"[{r.get('doc_name', 'Document')}]\n{r['text']}")

    return "\n\n".join(sections) if sections else "No relevant documents found."


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
rag_system = CombinedRAGSystem()
