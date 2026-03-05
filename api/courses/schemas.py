from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class CourseCreate(BaseModel):
    course_name: str = Field(..., min_length=1, max_length=200)
    course_level: Optional[str] = Field(None, max_length=50)
    grade: Optional[str] = Field(None, max_length=5)
    credits: Optional[float] = Field(None, ge=0)
    semester: Optional[str] = Field(None, max_length=20)
    year: Optional[int] = Field(None, ge=1900, le=2100)


class CourseUpdate(BaseModel):
    course_name: Optional[str] = Field(None, min_length=1, max_length=200)
    course_level: Optional[str] = Field(None, max_length=50)
    grade: Optional[str] = Field(None, max_length=5)
    credits: Optional[float] = Field(None, ge=0)
    semester: Optional[str] = Field(None, max_length=20)
    year: Optional[int] = Field(None, ge=1900, le=2100)


class CourseResponse(BaseModel):
    id: int
    student_id: UUID
    course_name: str
    course_level: Optional[str] = None
    grade: Optional[str] = None
    credits: Optional[float] = None
    semester: Optional[str] = None
    year: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
