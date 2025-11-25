from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, require_role

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/average-duration", response_model=list[schemas.AverageDurationResponse])
def average_duration(
    group_by: str = Query("week", pattern="^(week|course)$"),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> list[schemas.AverageDurationResponse]:
    if group_by == "week":
        period_expr = func.strftime("%Y-W%W", models.InteractionLog.timestamp)
    else:
        period_expr = models.Course.code + " - " + models.Course.title
    query = (
        db.query(period_expr.label("key"), func.avg(models.InteractionLog.duration_minutes).label("avg_duration"))
        .join(models.Course, models.Course.id == models.InteractionLog.course_id)
        .group_by("key")
        .order_by("key")
    )
    return [schemas.AverageDurationResponse(key=row.key, average_duration=row.avg_duration or 0.0) for row in query]


@router.get("/discussion-participation", response_model=list[schemas.DiscussionParticipationResponse])
def discussion_participation(
    course_id: int | None = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> list[schemas.DiscussionParticipationResponse]:
    query = (
        db.query(
            models.User.id.label("student_id"),
            models.User.full_name.label("student_name"),
            func.sum(models.InteractionLog.discussion_posts).label("total_posts"),
        )
        .join(models.InteractionLog, models.InteractionLog.student_id == models.User.id)
        .filter(models.User.role == models.UserRole.STUDENT)
    )
    if course_id is not None:
        query = query.filter(models.InteractionLog.course_id == course_id)
    query = query.group_by(models.User.id).order_by(func.sum(models.InteractionLog.discussion_posts).desc())
    results = query.all()
    return [
        schemas.DiscussionParticipationResponse(
            student_id=row.student_id,
            student_name=row.student_name,
            total_discussion_posts=int(row.total_posts or 0),
        )
        for row in results
    ]


@router.get("/activity-performance", response_model=list[schemas.ActivityPerformanceResponse])
def activity_vs_performance(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> list[schemas.ActivityPerformanceResponse]:
    query = (
        db.query(
            models.User.id.label("student_id"),
            models.User.full_name.label("student_name"),
            models.Course.id.label("course_id"),
            models.Course.title.label("course_title"),
            func.count(models.InteractionLog.id).label("interaction_count"),
            func.sum(models.InteractionLog.duration_minutes).label("total_duration"),
            models.Enrollment.final_score,
            models.Enrollment.completion_rate,
        )
        .join(models.InteractionLog, models.InteractionLog.student_id == models.User.id)
        .join(models.Course, models.Course.id == models.InteractionLog.course_id)
        .outerjoin(
            models.Enrollment,
            (models.Enrollment.course_id == models.Course.id)
            & (models.Enrollment.student_id == models.User.id),
        )
        .filter(models.User.role == models.UserRole.STUDENT)
        .group_by(
            models.User.id,
            models.Course.id,
            models.Enrollment.final_score,
            models.Enrollment.completion_rate,
        )
    )
    return [
        schemas.ActivityPerformanceResponse(
            student_id=row.student_id,
            student_name=row.student_name,
            course_id=row.course_id,
            course_title=row.course_title,
            interaction_count=int(row.interaction_count or 0),
            total_duration=float(row.total_duration or 0.0),
            final_score=row.final_score,
            completion_rate=row.completion_rate,
        )
        for row in query
    ]


@router.get("/low-activity", response_model=list[schemas.LowActivityStudentResponse])
def low_activity_students(
    min_average_duration: float = Query(30.0, ge=0.0),
    min_interactions: int = Query(5, ge=0),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> list[schemas.LowActivityStudentResponse]:
    query = (
        db.query(
            models.User.id.label("student_id"),
            models.User.full_name.label("student_name"),
            models.Course.id.label("course_id"),
            models.Course.title.label("course_title"),
            func.avg(models.InteractionLog.duration_minutes).label("avg_duration"),
            func.count(models.InteractionLog.id).label("interaction_count"),
        )
        .join(models.InteractionLog, models.InteractionLog.student_id == models.User.id)
        .join(models.Course, models.Course.id == models.InteractionLog.course_id)
        .filter(models.User.role == models.UserRole.STUDENT)
        .group_by(models.User.id, models.Course.id)
        .having(func.avg(models.InteractionLog.duration_minutes) < min_average_duration)
        .having(func.count(models.InteractionLog.id) <= min_interactions)
        .order_by(func.avg(models.InteractionLog.duration_minutes))
    )
    results = query.all()
    return [
        schemas.LowActivityStudentResponse(
            student_id=row.student_id,
            student_name=row.student_name,
            course_id=row.course_id,
            course_title=row.course_title,
            average_duration=float(row.avg_duration or 0.0),
            interaction_count=int(row.interaction_count or 0),
        )
        for row in results
    ]


@router.get("/activity-trend", response_model=list[schemas.ActivityTrendResponse])
def activity_trend(
    period: str = Query("week", pattern="^(week|month)$"),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> list[schemas.ActivityTrendResponse]:
    if period == "week":
        period_expr = func.strftime("%Y-W%W", models.InteractionLog.timestamp)
    else:
        period_expr = func.strftime("%Y-%m", models.InteractionLog.timestamp)
    query = (
        db.query(
            period_expr.label("period"),
            func.sum(models.InteractionLog.duration_minutes).label("total_duration"),
            func.count(models.InteractionLog.id).label("interaction_count"),
        )
        .group_by("period")
        .order_by("period")
    )
    return [
        schemas.ActivityTrendResponse(
            period=row.period,
            total_duration=float(row.total_duration or 0.0),
            interaction_count=int(row.interaction_count or 0),
        )
        for row in query
    ]
