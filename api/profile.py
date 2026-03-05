from datetime import date, datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_student
from database.database import get_db
from database.models import Student, Milestone, Activity
from api.schemas import ProfileResponse, ProfileUpdate, DashboardResponse, MilestoneSummary, ActivitySummary
from utils.profile_stats import calculate_profile_completion, calculate_readiness_score

router = APIRouter(prefix="/profile", tags=["Profile"])


def _get_student_or_404(student_id: str, db: Session) -> Student:
    """Shared helper: fetch the student record that belongs to the caller."""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    return student


# ---------------------------------------------------------------------------
# GET /api/profile
# ---------------------------------------------------------------------------
@router.get("", response_model=ProfileResponse)
def get_profile(
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Return the authenticated student's profile.
    The student_id is taken exclusively from the JWT token – never from the URL or body.
    """
    student = _get_student_or_404(student_id, db)
    return student


# ---------------------------------------------------------------------------
# PUT /api/profile
# ---------------------------------------------------------------------------
@router.put("", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdate,
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Update the authenticated student's profile.
    Only fields explicitly provided (non-None) are updated.
    """
    student = _get_student_or_404(student_id, db)

    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


# ---------------------------------------------------------------------------
# GET /api/dashboard
# ---------------------------------------------------------------------------
@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Return dashboard statistics for the authenticated student:
    - Profile completion percentage
    - Next 5 upcoming milestones (ordered by due_date)
    - Last 10 activities (recent achievements)
    - Readiness score (0-100)
    """
    student = _get_student_or_404(student_id, db)

    # --- Profile completion ---
    completion_pct = calculate_profile_completion(student)

    # --- Upcoming milestones: next 5 pending/in-progress, ordered by due_date asc ---
    today = date.today()
    upcoming_milestones: List[Milestone] = (
        db.query(Milestone)
        .filter(
            Milestone.student_id == student_id,
            Milestone.status.in_(["pending", "in_progress"]),
            Milestone.due_date >= today,
        )
        .order_by(Milestone.due_date.asc())
        .limit(5)
        .all()
    )

    # --- Recent achievements: last 10 activities (proxy for achievements) ---
    recent_activities: List[Activity] = (
        db.query(Activity)
        .filter(Activity.student_id == student_id)
        .order_by(Activity.created_at.desc())
        .limit(10)
        .all()
    )

    # --- Readiness score ---
    readiness_score = calculate_readiness_score(student)

    return DashboardResponse(
        profile_completion_pct=completion_pct,
        upcoming_milestones=[MilestoneSummary.from_orm(m) for m in upcoming_milestones],
        recent_achievements=[ActivitySummary.from_orm(a) for a in recent_activities],
        readiness_score=readiness_score,
    )
