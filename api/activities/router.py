from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_student
from database.database import get_db
from database.models import Activity
from api.activities.schemas import ActivityCreate, ActivityUpdate, ActivityResponse
from memory.mem0_client import memory_manager

router = APIRouter(prefix="/activities", tags=["Activities"])


# ---------------------------------------------------------------------------
# Ownership helper
# ---------------------------------------------------------------------------
def _get_owned_activity(activity_id: int, student_id: str, db: Session) -> Activity:
    """
    Fetch an activity by PK and verify it belongs to the authenticated student.
    Raises 404 if missing, 403 if owned by someone else.
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    if str(activity.student_id) != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to access this activity",
        )
    return activity


# ---------------------------------------------------------------------------
# GET /api/activities
# ---------------------------------------------------------------------------
@router.get("", response_model=List[ActivityResponse])
def get_activities(
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Return all activities for the authenticated student, sorted by start_date DESC."""
    activities = (
        db.query(Activity)
        .filter(Activity.student_id == student_id)
        .order_by(Activity.start_date.desc().nullslast())
        .all()
    )
    return activities


# ---------------------------------------------------------------------------
# POST /api/activities
# ---------------------------------------------------------------------------
@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def add_activity(
    payload: ActivityCreate,
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Create a new activity record.
    student_id is ALWAYS taken from the JWT — never from the request body.
    Writes a natural-language memory entry to Mem0 after saving.
    """
    new_activity = Activity(
        student_id=student_id,
        **payload.dict(),
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    # --- Update Mem0 memory via StudentMemoryManager ---
    memory_manager.remember_activity(student_id, {
        "id": new_activity.id,
        "activity_name": new_activity.activity_name,
        "category": new_activity.category,
        "role": new_activity.role,
        "hours_per_week": new_activity.hours_per_week,
        "achievements": new_activity.achievements or [],
    })

    return new_activity


# ---------------------------------------------------------------------------
# PUT /api/activities/{activity_id}
# ---------------------------------------------------------------------------
@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    payload: ActivityUpdate,
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Update an activity.  Verifies ownership before any changes.
    Only explicitly provided fields are modified (partial update).
    """
    activity = _get_owned_activity(activity_id, student_id, db)

    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)
    return activity


# ---------------------------------------------------------------------------
# DELETE /api/activities/{activity_id}
# ---------------------------------------------------------------------------
@router.delete("/{activity_id}", response_model=dict)
def delete_activity(
    activity_id: int,
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Delete an activity. Verifies the record belongs to the caller first."""
    activity = _get_owned_activity(activity_id, student_id, db)
    db.delete(activity)
    db.commit()
    return {"message": f"Activity '{activity.activity_name}' deleted successfully"}
