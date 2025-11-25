from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_current_user, get_db, require_role

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", response_model=schemas.CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    course_in: schemas.CourseCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> schemas.CourseRead:
    if db.query(models.Course).filter(models.Course.code == course_in.code).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course code already exists")
    course = models.Course(**course_in.dict())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("", response_model=list[schemas.CourseRead])
def list_courses(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)) -> list[schemas.CourseRead]:
    return db.query(models.Course).all()


@router.get("/{course_id}", response_model=schemas.CourseRead)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
) -> schemas.CourseRead:
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.put("/{course_id}", response_model=schemas.CourseRead)
def update_course(
    course_id: int,
    course_in: schemas.CourseUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> schemas.CourseRead:
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    for key, value in course_in.dict(exclude_unset=True).items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> None:
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    db.delete(course)
    db.commit()
