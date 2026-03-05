from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from auth.dependencies import get_current_student
from database.database import get_db
from database.models import Activity, Course, Milestone, StrategicPlan, Student
from api.plan.schemas import MilestoneResponse, PlanResponse, PlanUpdate
from agents._planner_graph import run_planning_workflow
from memory.mem0_client import memory_manager

router = APIRouter(tags=["Plan & Milestones"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_owned_plan(student_id: str, db: Session) -> StrategicPlan:
    plan = (
        db.query(StrategicPlan)
        .options(joinedload(StrategicPlan.milestones))
        .filter(StrategicPlan.student_id == student_id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No strategic plan found")
    return plan


def _get_owned_milestone(milestone_id: int, student_id: str, db: Session) -> Milestone:
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
    if str(milestone.student_id) != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to access this milestone",
        )
    return milestone


def _profile_to_dict(student: Student) -> dict:
    return {
        "first_name": student.first_name,
        "last_name": student.last_name,
        "gpa": student.gpa,
        "sat_score": student.sat_score,
        "act_score": student.act_score,
        "graduation_year": student.graduation_year,
        "current_grade": student.current_grade,
        "target_universities": student.target_universities or [],
        "target_majors": student.target_majors or [],
    }


def _course_to_dict(c: Course) -> dict:
    return {
        "course_name": c.course_name,
        "course_level": c.course_level,
        "grade": c.grade,
        "credits": c.credits,
        "semester": c.semester,
        "year": c.year,
    }


def _activity_to_dict(a: Activity) -> dict:
    return {
        "activity_name": a.activity_name,
        "category": a.category,
        "role": a.role,
        "hours_per_week": a.hours_per_week,
        "achievements": a.achievements or [],
    }


# ---------------------------------------------------------------------------
# GET /api/plan  – fetch current plan + milestones
# ---------------------------------------------------------------------------
@router.get("/plan", response_model=PlanResponse)
def get_plan(
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Return the authenticated student's strategic plan with all milestones."""
    return _get_owned_plan(student_id, db)


# ---------------------------------------------------------------------------
# POST /api/plan/generate  – generate a brand-new plan via LangGraph agents
# ---------------------------------------------------------------------------
@router.post("/plan/generate", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def generate_plan(
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Run the full LangGraph multi-agent workflow for the authenticated student.
    All data is fetched inside the workflow filtered by student_id (from JWT).
    Upserts the strategic plan and seeds milestones from agent output.
    """
    try:
        result = await run_planning_workflow(
            student_id=student_id,
            query="Generate my complete 4-year college strategic plan",
            db=db,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    # Package workflow outputs as plan_data
    plan_data = {
        **result.get("plan", {}),
        "course_recommendations": result.get("course_recommendations", []),
        "activity_suggestions": result.get("activity_suggestions", []),
        "university_insights": result.get("university_insights", []),
        "recommendations": result.get("recommendations", []),
    }

    # Upsert the strategic plan row
    existing_plan = db.query(StrategicPlan).filter(StrategicPlan.student_id == student_id).first()
    if existing_plan:
        db.query(Milestone).filter(Milestone.plan_id == existing_plan.id).delete()
        existing_plan.plan_data = plan_data
        existing_plan.updated_at = datetime.now(timezone.utc)
        plan = existing_plan
    else:
        plan = StrategicPlan(student_id=student_id, plan_data=plan_data)
        db.add(plan)

    db.flush()

    # Seed milestones from TimelineManagerAgent output
    milestone_source = result.get("milestone_updates") or plan_data.get("milestones", [])
    for m in milestone_source:
        db_milestone = Milestone(
            student_id=student_id,
            plan_id=plan.id,
            semester=m.get("semester"),
            title=m.get("title", "Untitled milestone"),
            description=m.get("description"),
            status=m.get("status", "pending"),
        )
        db.add(db_milestone)

    db.commit()
    db.refresh(plan)

    return (
        db.query(StrategicPlan)
        .options(joinedload(StrategicPlan.milestones))
        .filter(StrategicPlan.id == plan.id)
        .first()
    )


# ---------------------------------------------------------------------------
# PUT /api/plan  – manual plan_data update
# ---------------------------------------------------------------------------
@router.put("/plan", response_model=PlanResponse)
def update_plan(
    payload: PlanUpdate,
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Manually overwrite plan_data. Verifies ownership via the helper."""
    plan = _get_owned_plan(student_id, db)
    plan.plan_data = payload.plan_data
    plan.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(plan)

    # Fire memory update if goals changed
    pd = payload.plan_data
    if pd.get("target_schools") or pd.get("target_majors"):
        memory_manager.remember_goals_update(
            student_id,
            universities=pd.get("target_schools", []),
            majors=pd.get("target_majors", []),
        )

    return (
        db.query(StrategicPlan)
        .options(joinedload(StrategicPlan.milestones))
        .filter(StrategicPlan.id == plan.id)
        .first()
    )


# ---------------------------------------------------------------------------
# GET /api/milestones  – list milestones, optional semester filter
# ---------------------------------------------------------------------------
@router.get("/milestones", response_model=List[MilestoneResponse])
def get_milestones(
    semester: Optional[str] = Query(None, description="Filter by semester, e.g. '9th-Fall'"),
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Return milestones for the authenticated student with an optional semester filter."""
    q = db.query(Milestone).filter(Milestone.student_id == student_id)
    if semester:
        q = q.filter(Milestone.semester == semester)
    return q.order_by(Milestone.due_date.asc().nullslast()).all()


# ---------------------------------------------------------------------------
# PUT /api/milestones/{milestone_id}/complete
# ---------------------------------------------------------------------------
@router.put("/milestones/{milestone_id}/complete", response_model=MilestoneResponse)
def complete_milestone(
    milestone_id: int,
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Mark a milestone as completed.
    Verifies the milestone belongs to the authenticated student before updating.
    """
    milestone = _get_owned_milestone(milestone_id, student_id, db)
    now = datetime.now(timezone.utc)
    milestone.status = "completed"
    milestone.completed_at = now
    db.commit()
    db.refresh(milestone)

    # Persist achievement to Mem0
    memory_manager.remember_milestone_complete(student_id, {
        "id": milestone.id,
        "title": milestone.title,
        "semester": milestone.semester,
        "completed_at": now.isoformat(),
    })

    return milestone
