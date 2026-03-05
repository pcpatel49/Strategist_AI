"""
StudentMemoryManager — fully isolated Mem0 memory per student.

Isolation guarantee: every method accepts a student_id and passes it as
`user_id` to Mem0. Mem0 physically partitions memories by user_id, so
calling search/get/delete with student_id X can never touch student Y's data.

Graceful degradation: if MEM0_API_KEY is absent (local dev) every method
is a no-op and the rest of the application continues to work normally.
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class StudentMemoryManager:
    """
    Thread-safe Mem0 wrapper with per-student isolation.

    Usage
    -----
    memory = StudentMemoryManager()

    # Add a fact
    memory.add_memory(student_id, "Completed AP Chemistry with grade A")

    # Search for relevant memories
    results = memory.search_memory(student_id, "chemistry courses")

    # GDPR-compliant bulk delete
    memory.delete_all_memories(student_id)
    """

    def __init__(self) -> None:
        self._client = None   # lazy init

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_client(self):
        if self._client is not None:
            return self._client

        api_key = os.getenv("MEM0_API_KEY")
        if not api_key:
            logger.warning(
                "MEM0_API_KEY not set — StudentMemoryManager running in no-op mode."
            )
            return None

        try:
            from mem0 import MemoryClient  # type: ignore
            self._client = MemoryClient(api_key=api_key)
            logger.info("Mem0 client initialised successfully.")
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Failed to initialise Mem0 client: {exc}")

        return self._client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def add_memory(
        self,
        student_id: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Add a memory for a specific student.

        Parameters
        ----------
        student_id : str   Used as Mem0 user_id → full isolation.
        text       : str   Natural-language fact to remember.
        metadata   : dict  Optional structured tags stored alongside.
        """
        client = self._get_client()
        if client is None:
            return

        try:
            client.add(
                [{"role": "user", "content": text}],
                user_id=student_id,
                metadata=metadata or {},
            )
            logger.debug(f"[Mem0] Added memory for student {student_id}: {text[:80]}")
        except Exception as exc:  # noqa: BLE001
            logger.error(f"[Mem0] add_memory failed for {student_id}: {exc}")

    def search_memory(
        self,
        student_id: str,
        query: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Search ONLY this student's memories.
        Returns a list of Mem0 memory dicts: [{"memory": str, ...}, ...]
        """
        client = self._get_client()
        if client is None:
            return []

        try:
            results = client.search(query, user_id=student_id, limit=limit)
            return results if isinstance(results, list) else []
        except Exception as exc:  # noqa: BLE001
            logger.error(f"[Mem0] search_memory failed for {student_id}: {exc}")
            return []

    def get_all_memories(self, student_id: str) -> list[dict[str, Any]]:
        """
        Retrieve every memory stored for this student.
        Useful for profile summaries or admin inspection.
        """
        client = self._get_client()
        if client is None:
            return []

        try:
            results = client.get_all(user_id=student_id)
            return results if isinstance(results, list) else []
        except Exception as exc:  # noqa: BLE001
            logger.error(f"[Mem0] get_all_memories failed for {student_id}: {exc}")
            return []

    def delete_all_memories(self, student_id: str) -> bool:
        """
        Bulk-delete all memories for a student.
        Call this when the student requests account deletion (GDPR right to erasure).

        Returns True on success, False on failure.
        """
        client = self._get_client()
        if client is None:
            return False

        try:
            client.delete_all(user_id=student_id)
            logger.info(f"[Mem0] All memories deleted for student {student_id}")
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error(f"[Mem0] delete_all_memories failed for {student_id}: {exc}")
            return False

    # ------------------------------------------------------------------
    # Convenience memory builders (called from routers)
    # ------------------------------------------------------------------
    def remember_course(self, student_id: str, course: dict[str, Any]) -> None:
        grade_part = f"with grade {course['grade']}" if course.get("grade") else ""
        credits_part = f"({course['credits']} credits)" if course.get("credits") else ""
        text = (
            f"Completed course: {course['course_name']} "
            f"[{course.get('course_level', 'standard')}] "
            f"{grade_part} {credits_part} "
            f"in {course.get('semester', '')} {course.get('year', '')}".strip()
        )
        self.add_memory(
            student_id, text,
            metadata={"type": "course", "course_id": course.get("id")}
        )

    def remember_activity(self, student_id: str, activity: dict[str, Any]) -> None:
        role_part = f"as {activity['role']}" if activity.get("role") else ""
        hours_part = f"{activity['hours_per_week']} hrs/week" if activity.get("hours_per_week") else ""
        achievements = activity.get("achievements") or []
        ach_part = f"Achievements: {', '.join(achievements)}" if achievements else ""
        text = (
            f"Extracurricular: {activity['activity_name']} "
            f"[{activity.get('category', 'general')}] {role_part} {hours_part}. {ach_part}"
        ).strip()
        self.add_memory(
            student_id, text,
            metadata={"type": "activity", "activity_id": activity.get("id")}
        )

    def remember_milestone_complete(self, student_id: str, milestone: dict[str, Any]) -> None:
        text = (
            f"Completed milestone: {milestone['title']} "
            f"(semester: {milestone.get('semester', 'N/A')}) "
            f"on {milestone.get('completed_at', 'unknown date')}"
        )
        self.add_memory(
            student_id, text,
            metadata={"type": "milestone", "milestone_id": milestone.get("id")}
        )

    def remember_goals_update(self, student_id: str, universities: list[str], majors: list[str]) -> None:
        text = (
            f"Updated target universities: {', '.join(universities) or 'none'}. "
            f"Target majors: {', '.join(majors) or 'none'}."
        )
        self.add_memory(student_id, text, metadata={"type": "goals"})


# ---------------------------------------------------------------------------
# Module-level singleton — import this everywhere
# ---------------------------------------------------------------------------
memory_manager = StudentMemoryManager()
