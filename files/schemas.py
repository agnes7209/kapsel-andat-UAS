from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    role: Optional[str] = None


class UserBase(BaseModel):
    full_name: str
    email: EmailStr


class UserRead(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str = Field(min_length=6)
    role: str = "student"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[str] = None


class CourseBase(BaseModel):
    code: str
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CourseRead(CourseBase):
    id: int

    class Config:
        orm_mode = True


class ActivityBase(BaseModel):
    course_id: int
    name: str
    description: Optional[str] = None
    category: str = "general"


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class ActivityRead(ActivityBase):
    id: int

    class Config:
        orm_mode = True


class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int
    final_score: Optional[float] = None
    completion_rate: Optional[float] = Field(None, ge=0, le=100)
    last_activity_at: Optional[datetime] = None


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentUpdate(BaseModel):
    final_score: Optional[float] = None
    completion_rate: Optional[float] = Field(None, ge=0, le=100)
    last_activity_at: Optional[datetime] = None


class EnrollmentRead(EnrollmentBase):
    id: int

    class Config:
        orm_mode = True


class InteractionLogBase(BaseModel):
    student_id: int
    course_id: int
    activity_id: int
    duration_minutes: float = Field(ge=0)
    interaction_type: str = "general"
    timestamp: Optional[datetime] = None
    discussion_posts: int = Field(0, ge=0)
    notes: Optional[str] = None


class InteractionLogCreate(InteractionLogBase):
    pass


class InteractionLogUpdate(BaseModel):
    duration_minutes: Optional[float] = Field(None, ge=0)
    interaction_type: Optional[str] = None
    timestamp: Optional[datetime] = None
    discussion_posts: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class InteractionLogRead(InteractionLogBase):
    id: int

    class Config:
        orm_mode = True


class AverageDurationResponse(BaseModel):
    key: str
    average_duration: float


class DiscussionParticipationResponse(BaseModel):
    student_id: int
    student_name: str
    total_discussion_posts: int


class ActivityPerformanceResponse(BaseModel):
    student_id: int
    student_name: str
    course_id: int
    course_title: str
    interaction_count: int
    total_duration: float
    final_score: Optional[float]
    completion_rate: Optional[float]


class LowActivityStudentResponse(BaseModel):
    student_id: int
    student_name: str
    course_id: int
    course_title: str
    average_duration: float
    interaction_count: int


class ActivityTrendResponse(BaseModel):
    period: str
    total_duration: float
    interaction_count: int
