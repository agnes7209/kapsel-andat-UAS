from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_current_user, get_db, require_role

router = APIRouter(prefix="/activities", tags=["activities"])


@router.post("", response_model=schemas.ActivityRead, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity_in: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> schemas.ActivityRead:
    course = db.query(models.Course).filter(models.Course.id == activity_in.course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course not found")
    activity = models.Activity(**activity_in.dict())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.get("", response_model=list[schemas.ActivityRead])
def list_activities(
    course_id: int | None = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
) -> list[schemas.ActivityRead]:
    query = db.query(models.Activity)
    if course_id is not None:
        query = query.filter(models.Activity.course_id == course_id)
    return query.all()


@router.get("/{activity_id}", response_model=schemas.ActivityRead)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
) -> schemas.ActivityRead:
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    return activity


@router.put("/{activity_id}", response_model=schemas.ActivityRead)
def update_activity(
    activity_id: int,
    activity_in: schemas.ActivityUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> schemas.ActivityRead:
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    for key, value in activity_in.dict(exclude_unset=True).items():
        setattr(activity, key, value)
    db.commit()
    db.refresh(activity)
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> None:
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    db.delete(activity)
    db.commit()
