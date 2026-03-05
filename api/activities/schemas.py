from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime


class ActivityCreate(BaseModel):
    activity_name: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=100)
    hours_per_week: Optional[int] = Field(None, ge=0, le=168)
    start_date: Optional[date] = None
    achievements: Optional[List[str]] = None


class ActivityUpdate(BaseModel):
    activity_name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=100)
    hours_per_week: Optional[int] = Field(None, ge=0, le=168)
    start_date: Optional[date] = None
    achievements: Optional[List[str]] = None


class ActivityResponse(BaseModel):
    id: int
    student_id: UUID
    activity_name: str
    category: Optional[str] = None
    role: Optional[str] = None
    hours_per_week: Optional[int] = None
    start_date: Optional[date] = None
    achievements: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True
