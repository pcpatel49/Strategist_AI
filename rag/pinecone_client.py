"""
Pinecone client factory — shared singleton, lazy init.
Gracefully degrades when PINECONE_API_KEY is absent (local dev / CI).
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

_pinecone_client = None
UNIVERSITY_INDEX = "university-data"
STUDENT_DOCS_INDEX = "student-documents"
EMBEDDING_DIMENSION = 1536   # matches text-embedding-ada-002 / text-embedding-3-small


def get_pinecone_client():
    global _pinecone_client
    if _pinecone_client is not None:
        return _pinecone_client

    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        logger.warning("PINECONE_API_KEY not set — RAG running in stub mode.")
        return None

    try:
        from pinecone import Pinecone  # type: ignore
        _pinecone_client = Pinecone(api_key=api_key)
        logger.info("Pinecone client initialised.")
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Failed to initialise Pinecone: {exc}")

    return _pinecone_client


def get_embedding(text: str) -> list[float]:
    """
    Generate a text embedding via OpenAI.
    Falls back to a zero-vector stub when OPENAI_API_KEY is absent.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return [0.0] * EMBEDDING_DIMENSION

    try:
        from openai import OpenAI  # type: ignore
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small",
        )
        return response.data[0].embedding
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Embedding failed: {exc}")
        return [0.0] * EMBEDDING_DIMENSION
