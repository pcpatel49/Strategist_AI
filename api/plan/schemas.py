from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from uuid import UUID
from datetime import date, datetime


# ---------------------------------------------------------------------------
# Plan schemas
# ---------------------------------------------------------------------------
class PlanUpdate(BaseModel):
    plan_data: Dict[str, Any]


class MilestoneResponse(BaseModel):
    id: int
    student_id: UUID
    plan_id: Optional[int] = None
    semester: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PlanResponse(BaseModel):
    id: int
    student_id: UUID
    plan_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    milestones: List[MilestoneResponse] = []

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Milestone schemas
# ---------------------------------------------------------------------------
class MilestoneComplete(BaseModel):
    """Body is empty for the complete endpoint — all we need is the ID in the path."""
    pass
