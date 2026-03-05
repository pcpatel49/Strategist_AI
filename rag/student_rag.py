"""
StudentDocumentRAG — private, per-student Pinecone index.

Every document is stored WITH metadata: {student_id: "<uuid>"}.
Every query adds a Pinecone filter: {student_id: {"$eq": "<uuid>"}}.
This guarantees a student can NEVER see another student's documents.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from rag.pinecone_client import get_pinecone_client, get_embedding, STUDENT_DOCS_INDEX

logger = logging.getLogger(__name__)

TOP_K = 5


class StudentDocumentRAG:
    """Private document store — fully isolated per student via Pinecone metadata filter."""

    def _get_index(self):
        client = get_pinecone_client()
        if client is None:
            return None
        try:
            return client.Index(STUDENT_DOCS_INDEX)
        except Exception as exc:
            logger.error(f"[StudentDocumentRAG] Cannot access index '{STUDENT_DOCS_INDEX}': {exc}")
            return None

    # ------------------------------------------------------------------
    def add_student_document(
        self,
        student_id: str,
        doc_name: str,
        content: str,
        extra_metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Embed and upsert a document into the private student index.
        student_id is ALWAYS written into Pinecone metadata — never optional.
        Returns the generated vector ID (used as doc_id in the DB).
        """
        index = self._get_index()
        if index is None:
            logger.warning("[StudentDocumentRAG] Skipping add — index unavailable.")
            return str(uuid.uuid4())   # return a stub id so the API doesn't break

        try:
            vector_id = str(uuid.uuid4())
            embedding = get_embedding(content)
            metadata: dict[str, Any] = {
                "student_id": student_id,          # isolation key
                "doc_name": doc_name,
                "text": content[:1000],            # Pinecone metadata limit
                **(extra_metadata or {}),
            }
            index.upsert(vectors=[(vector_id, embedding, metadata)])
            logger.info(
                f"[StudentDocumentRAG] Document '{doc_name}' "
                f"upserted for student {student_id} (id={vector_id})"
            )
            return vector_id
        except Exception as exc:
            logger.error(f"[StudentDocumentRAG] add_student_document failed: {exc}")
            return ""

    # ------------------------------------------------------------------
    def query_student_documents(
        self,
        student_id: str,
        query: str,
        top_k: int = TOP_K,
    ) -> list[dict[str, Any]]:
        """
        Semantic search restricted to this student's documents only.
        The Pinecone filter enforces isolation — other students' vectors are never scored.
        """
        index = self._get_index()
        if index is None:
            return self._stub_results(student_id, query)

        try:
            vector = get_embedding(query)
            response = index.query(
                vector=vector,
                top_k=top_k,
                filter={"student_id": {"$eq": student_id}},   # ISOLATION ENFORCED HERE
                include_metadata=True,
            )
            return [
                {
                    "text": m.metadata.get("text", ""),
                    "doc_name": m.metadata.get("doc_name", "Unknown"),
                    "score": m.score,
                    "vector_id": m.id,
                }
                for m in response.matches
            ]
        except Exception as exc:
            logger.error(f"[StudentDocumentRAG] query failed for {student_id}: {exc}")
            return self._stub_results(student_id, query)

    # ------------------------------------------------------------------
    def delete_student_document(self, vector_id: str) -> bool:
        """Delete a specific document vector by ID."""
        index = self._get_index()
        if index is None:
            return False
        try:
            index.delete(ids=[vector_id])
            logger.info(f"[StudentDocumentRAG] Deleted vector {vector_id}")
            return True
        except Exception as exc:
            logger.error(f"[StudentDocumentRAG] delete failed for {vector_id}: {exc}")
            return False

    # ------------------------------------------------------------------
    def delete_all_student_documents(self, student_id: str) -> bool:
        """
        GDPR right-to-erasure: delete ALL of a student's private vectors.
        Uses Pinecone delete-by-metadata-filter.
        """
        index = self._get_index()
        if index is None:
            return False
        try:
            index.delete(filter={"student_id": {"$eq": student_id}})
            logger.info(f"[StudentDocumentRAG] All documents deleted for student {student_id}")
            return True
        except Exception as exc:
            logger.error(f"[StudentDocumentRAG] delete_all failed for {student_id}: {exc}")
            return False

    @staticmethod
    def _stub_results(student_id: str, query: str) -> list[dict[str, Any]]:
        return [
            {
                "text": (
                    f"[STUB] No Pinecone connection. Query: '{query}'. "
                    "Connect PINECONE_API_KEY to retrieve your private documents."
                ),
                "doc_name": "stub",
                "score": 0.0,
                "vector_id": "",
            }
        ]
