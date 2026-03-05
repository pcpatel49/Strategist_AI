from datetime import date, datetime
from typing import List
from uuid import UUID

from database.models import Student, Milestone, Activity


def calculate_profile_completion(student: Student) -> float:
    """
    Calculate what percentage of the student profile is filled in.
    Checks all optional fields and scores each one.
    """
    fields = [
        student.first_name,
        student.last_name,
        student.current_grade,
        student.graduation_year,
        student.gpa,
        student.sat_score,
        student.act_score,
        student.target_universities,
        student.target_majors,
    ]
    filled = sum(1 for f in fields if f is not None and f != [] and f != "")
    return round((filled / len(fields)) * 100, 1)


def calculate_readiness_score(student: Student) -> float:
    """
    Heuristic readiness score out of 100 based on profile data quality.
    In production, this could be driven by AI agent analysis.
    """
    score = 0.0

    # GPA scoring (max 30 pts)
    if student.gpa:
        score += min(student.gpa / 4.0, 1.0) * 30

    # Test scores (max 25 pts)
    if student.sat_score:
        score += min(student.sat_score / 1600, 1.0) * 15
    if student.act_score:
        score += min(student.act_score / 36, 1.0) * 10

    # Target schools defined (max 20 pts)
    if student.target_universities:
        score += min(len(student.target_universities) / 5, 1.0) * 20

    # Target majors defined (max 10 pts)
    if student.target_majors:
        score += min(len(student.target_majors) / 3, 1.0) * 10

    # Course & activity data (max 15 pts — rough proxy from relationships)
    if student.courses:
        score += min(len(student.courses) / 6, 1.0) * 8
    if student.activities:
        score += min(len(student.activities) / 4, 1.0) * 7

    return round(min(score, 100.0), 1)
