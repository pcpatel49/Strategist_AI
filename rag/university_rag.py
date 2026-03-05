"""
UniversityRAG — shared, public Pinecone index.

Stores Common Data Sets, admission requirements, deadlines.
No student_id filtering — all authenticated students can query.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

from rag.pinecone_client import get_pinecone_client, get_embedding, UNIVERSITY_INDEX

logger = logging.getLogger(__name__)

TOP_K = 5


class UniversityRAG:
    """Query shared university reference data. No per-student filtering required."""

    def _get_index(self):
        client = get_pinecone_client()
        if client is None:
            return None
        try:
            return client.Index(UNIVERSITY_INDEX)
        except Exception as exc:
            logger.error(f"[UniversityRAG] Cannot access index '{UNIVERSITY_INDEX}': {exc}")
            return None

    # ------------------------------------------------------------------
    def query_university(
        self,
        query: str,
        university_filter: Optional[str] = None,
        top_k: int = TOP_K,
    ) -> list[dict[str, Any]]:
        """
        Semantic search over shared university data.

        Parameters
        ----------
        query            : str  Natural language question.
        university_filter: str  Optional — filter by university name metadata field.
        top_k            : int  Number of results to return.

        Returns list of dicts: [{"text": str, "university": str, "score": float}]
        """
        index = self._get_index()
        if index is None:
            return self._stub_results(query, university_filter)

        try:
            vector = get_embedding(query)
            filter_dict: dict[str, Any] = {}
            if university_filter:
                filter_dict["university"] = {"$eq": university_filter}

            response = index.query(
                vector=vector,
                top_k=top_k,
                filter=filter_dict if filter_dict else None,
                include_metadata=True,
            )
            return [
                {
                    "text": m.metadata.get("text", ""),
                    "university": m.metadata.get("university", "Unknown"),
                    "doc_type": m.metadata.get("doc_type", "general"),
                    "score": m.score,
                }
                for m in response.matches
            ]
        except Exception as exc:
            logger.error(f"[UniversityRAG] query failed: {exc}")
            return self._stub_results(query, university_filter)

    def ingest_university_document(
        self,
        text: str,
        university: str,
        doc_type: str = "general",
        extra_metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Embed and upsert a university document into the shared index.
        Returns the generated vector ID.
        """
        index = self._get_index()
        if index is None:
            logger.warning("[UniversityRAG] Skipping ingest — index unavailable.")
            return ""

        try:
            vector_id = str(uuid.uuid4())
            embedding = get_embedding(text)
            metadata = {
                "text": text[:1000],    # Pinecone metadata size limit
                "university": university,
                "doc_type": doc_type,
                **(extra_metadata or {}),
            }
            index.upsert(vectors=[(vector_id, embedding, metadata)])
            logger.info(f"[UniversityRAG] Upserted document for {university} (id={vector_id})")
            return vector_id
        except Exception as exc:
            logger.error(f"[UniversityRAG] ingest failed: {exc}")
            return ""

    @staticmethod
    def _stub_results(query: str, university_filter: Optional[str]) -> list[dict[str, Any]]:
        scope = f" for {university_filter}" if university_filter else ""
        return [
            {
                "text": (
                    f"[STUB] University data{scope}: No Pinecone connection. "
                    f"Query was: '{query}'. "
                    "Connect PINECONE_API_KEY to get real admissions data."
                ),
                "university": university_filter or "General",
                "doc_type": "stub",
                "score": 0.0,
            }
        ]
