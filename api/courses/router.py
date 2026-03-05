from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_student
from database.database import get_db
from database.models import Course
from api.courses.schemas import CourseCreate, CourseUpdate, CourseResponse
from memory.mem0_client import memory_manager

router = APIRouter(prefix="/courses", tags=["Courses"])


# ---------------------------------------------------------------------------
# Ownership helper
# ---------------------------------------------------------------------------
def _get_owned_course(course_id: int, student_id: str, db: Session) -> Course:
    """
    Fetch a course by PK and verify it belongs to the authenticated student.
    Raises 404 if the course doesn't exist, 403 if it's owned by someone else.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if str(course.student_id) != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to access this course",
        )
    return course


# ---------------------------------------------------------------------------
# GET /api/courses
# ---------------------------------------------------------------------------
@router.get("", response_model=List[CourseResponse])
def get_courses(
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Return all courses for the authenticated student, newest year/semester first."""
    courses = (
        db.query(Course)
        .filter(Course.student_id == student_id)
        .order_by(Course.year.desc().nullslast(), Course.semester.desc())
        .all()
    )
    return courses


# ---------------------------------------------------------------------------
# POST /api/courses
# ---------------------------------------------------------------------------
@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def add_course(
    payload: CourseCreate,
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Create a new course record.
    student_id is ALWAYS taken from the JWT — never from the request body.
    After saving, a memory entry is pushed to Mem0.
    """
    new_course = Course(
        student_id=student_id,
        **payload.dict(),
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    # --- Update Mem0 memory via StudentMemoryManager ---
    memory_manager.remember_course(student_id, {
        "id": new_course.id,
        "course_name": new_course.course_name,
        "course_level": new_course.course_level,
        "grade": new_course.grade,
        "credits": new_course.credits,
        "semester": new_course.semester,
        "year": new_course.year,
    })

    return new_course


# ---------------------------------------------------------------------------
# PUT /api/courses/{course_id}
# ---------------------------------------------------------------------------
@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    payload: CourseUpdate,
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Update a course.  Verifies ownership before making any changes.
    Only explicitly supplied fields are modified (partial update).
    """
    course = _get_owned_course(course_id, student_id, db)

    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)
    return course


# ---------------------------------------------------------------------------
# DELETE /api/courses/{course_id}
# ---------------------------------------------------------------------------
@router.delete("/{course_id}", response_model=dict)
def delete_course(
    course_id: int,
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Delete a course.  Verifies ownership — a student cannot delete another's record.
    """
    course = _get_owned_course(course_id, student_id, db)
    db.delete(course)
    db.commit()
    return {"message": f"Course '{course.course_name}' deleted successfully"}
