import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    interactions = relationship("InteractionLog", back_populates="student", cascade="all, delete")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    activities = relationship("Activity", back_populates="course", cascade="all, delete-orphan")
    interaction_logs = relationship("InteractionLog", back_populates="course", cascade="all, delete")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, default="general")

    course = relationship("Course", back_populates="activities")
    logs = relationship("InteractionLog", back_populates="activity", cascade="all, delete")

    __table_args__ = (UniqueConstraint("course_id", "name", name="uq_activity_course_name"),)


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    final_score = Column(Float, nullable=True)
    completion_rate = Column(Float, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)

    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_enrollment_student_course"),)


class InteractionLog(Base):
    __tablename__ = "interaction_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    duration_minutes = Column(Float, nullable=False, default=0.0)
    interaction_type = Column(String(100), nullable=False, default="general")
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    discussion_posts = Column(Integer, nullable=False, default=0)
    notes = Column(Text, nullable=True)

    student = relationship("User", back_populates="interactions")
    course = relationship("Course", back_populates="interaction_logs")
    activity = relationship("Activity", back_populates="logs")

    __table_args__ = (
        UniqueConstraint(
            "student_id", "course_id", "activity_id", "timestamp", name="uq_log_unique_event"
        ),
    )
