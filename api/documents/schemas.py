from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    id: int
    student_id: UUID
    doc_name: str
    vector_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UniversitySearchResponse(BaseModel):
    text: str
    university: str
    doc_type: Optional[str] = None
    score: float
