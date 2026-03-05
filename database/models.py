import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, Float, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255))
    otp = Column(String(6))
    otp_expires_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    student = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = "students"

    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    current_grade = Column(Integer)
    graduation_year = Column(Integer)
    gpa = Column(Float)
    sat_score = Column(Integer)
    act_score = Column(Integer)
    target_universities = Column(ARRAY(String))
    target_majors = Column(ARRAY(String))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="student")
    courses = relationship("Course", back_populates="student", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="student", cascade="all, delete-orphan")
    strategic_plan = relationship("StrategicPlan", back_populates="student", uselist=False, cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="student", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="student", cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    course_name = Column(String(200), nullable=False)
    course_level = Column(String(50))
    grade = Column(String(5))
    credits = Column(Float)
    semester = Column(String(20))
    year = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    student = relationship("Student", back_populates="courses")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    activity_name = Column(String(200), nullable=False)
    category = Column(String(50))
    role = Column(String(100))
    hours_per_week = Column(Integer)
    start_date = Column(Date)
    achievements = Column(ARRAY(String))
    created_at = Column(DateTime, server_default=func.now())

    student = relationship("Student", back_populates="activities")

class StrategicPlan(Base):
    __tablename__ = "strategic_plans"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, unique=True)
    plan_data = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    student = relationship("Student", back_populates="strategic_plan")
    milestones = relationship("Milestone", back_populates="plan", cascade="all, delete-orphan")

class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("strategic_plans.id", ondelete="CASCADE"))
    semester = Column(String(20))
    title = Column(String(200), nullable=False)
    description = Column(String)
    status = Column(String(20), default="pending")
    due_date = Column(Date)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    student = relationship("Student", back_populates="milestones")
    plan = relationship("StrategicPlan", back_populates="milestones")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(String, nullable=False)
    message_metadata = Column("metadata", JSONB)
    created_at = Column(DateTime, server_default=func.now())

    student = relationship("Student", back_populates="chat_messages")

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    blacklisted_on = Column(DateTime, server_default=func.now())


class StudentDocument(Base):
    """
    Tracks documents uploaded to the private Pinecone index.
    The vector_id column maps to the Pinecone vector so we can delete by ID.
    """
    __tablename__ = "student_documents"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doc_name = Column(String(255), nullable=False)
    vector_id = Column(String(255), nullable=False)   # Pinecone vector ID
    created_at = Column(DateTime, server_default=func.now())

    student = relationship("Student")
