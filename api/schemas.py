from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date


class ProfileResponse(BaseModel):
    student_id: UUID
    first_name: str
    last_name: str
    current_grade: Optional[int] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    sat_score: Optional[int] = None
    act_score: Optional[int] = None
    target_universities: Optional[List[str]] = None
    target_majors: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    current_grade: Optional[int] = Field(None, ge=1, le=12)
    graduation_year: Optional[int] = Field(None, ge=2020, le=2100)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    sat_score: Optional[int] = Field(None, ge=400, le=1600)
    act_score: Optional[int] = Field(None, ge=1, le=36)
    target_universities: Optional[List[str]] = None
    target_majors: Optional[List[str]] = None


class MilestoneSummary(BaseModel):
    id: int
    title: str
    semester: Optional[str] = None
    status: str
    due_date: Optional[date] = None

    class Config:
        from_attributes = True


class ActivitySummary(BaseModel):
    id: int
    activity_name: str
    category: Optional[str] = None
    role: Optional[str] = None
    achievements: Optional[List[str]] = None

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    profile_completion_pct: float
    upcoming_milestones: List[MilestoneSummary]
    recent_achievements: List[ActivitySummary]
    readiness_score: float
