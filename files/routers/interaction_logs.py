from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_current_user, get_db

router = APIRouter(prefix="/interaction-logs", tags=["interaction_logs"])


def _ensure_course_and_activity(db: Session, course_id: int, activity_id: int) -> None:
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course not found")
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Activity not found")
    if activity.course_id != course.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Activity does not belong to the course"
        )


def _ensure_student(db: Session, student_id: int) -> models.User:
    student = db.query(models.User).filter(
        models.User.id == student_id, models.User.role == models.UserRole.STUDENT
    ).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student not found")
    return student


@router.post("", response_model=schemas.InteractionLogRead, status_code=status.HTTP_201_CREATED)
def create_log(
    log_in: schemas.InteractionLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.InteractionLogRead:
    student = _ensure_student(db, log_in.student_id)
    if current_user.role == models.UserRole.STUDENT and current_user.id != log_in.student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot log activity for other students")
    _ensure_course_and_activity(db, log_in.course_id, log_in.activity_id)
    log_data = log_in.dict()
    if log_data.get("timestamp") is None:
        log_data.pop("timestamp")
    log = models.InteractionLog(**log_data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("", response_model=list[schemas.InteractionLogRead])
def list_logs(
    student_id: int | None = None,
    course_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> list[schemas.InteractionLogRead]:
    query = db.query(models.InteractionLog)
    if current_user.role == models.UserRole.STUDENT:
        query = query.filter(models.InteractionLog.student_id == current_user.id)
        if course_id is not None:
            query = query.filter(models.InteractionLog.course_id == course_id)
    else:
        if student_id is not None:
            query = query.filter(models.InteractionLog.student_id == student_id)
        if course_id is not None:
            query = query.filter(models.InteractionLog.course_id == course_id)
    return query.order_by(models.InteractionLog.timestamp.desc()).all()


@router.get("/{log_id}", response_model=schemas.InteractionLogRead)
def get_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.InteractionLogRead:
    log = db.query(models.InteractionLog).filter(models.InteractionLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction log not found")
    if current_user.role == models.UserRole.STUDENT and log.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return log


@router.put("/{log_id}", response_model=schemas.InteractionLogRead)
def update_log(
    log_id: int,
    log_in: schemas.InteractionLogUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.InteractionLogRead:
    log = db.query(models.InteractionLog).filter(models.InteractionLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction log not found")
    if current_user.role == models.UserRole.STUDENT and log.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update logs for other students")
    data = log_in.dict(exclude_unset=True)
    if "timestamp" in data and data["timestamp"] is None:
        data.pop("timestamp")
    for key, value in data.items():
        setattr(log, key, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> None:
    log = db.query(models.InteractionLog).filter(models.InteractionLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction log not found")
    if current_user.role == models.UserRole.STUDENT and log.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete logs for other students")
    db.delete(log)
    db.commit()
