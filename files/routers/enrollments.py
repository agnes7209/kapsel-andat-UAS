from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_current_user, get_db, require_role

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.post("", response_model=schemas.EnrollmentRead, status_code=status.HTTP_201_CREATED)
def create_enrollment(
    enrollment_in: schemas.EnrollmentCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> schemas.EnrollmentRead:
    student = db.query(models.User).filter(
        models.User.id == enrollment_in.student_id, models.User.role == models.UserRole.STUDENT
    ).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student not found")
    course = db.query(models.Course).filter(models.Course.id == enrollment_in.course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course not found")
    enrollment = models.Enrollment(**enrollment_in.dict())
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("", response_model=list[schemas.EnrollmentRead])
def list_enrollments(
    student_id: int | None = None,
    course_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> list[schemas.EnrollmentRead]:
    query = db.query(models.Enrollment)
    if current_user.role == models.UserRole.STUDENT:
        query = query.filter(models.Enrollment.student_id == current_user.id)
    else:
        if student_id is not None:
            query = query.filter(models.Enrollment.student_id == student_id)
        if course_id is not None:
            query = query.filter(models.Enrollment.course_id == course_id)
    return query.all()


@router.put("/{enrollment_id}", response_model=schemas.EnrollmentRead)
def update_enrollment(
    enrollment_id: int,
    enrollment_in: schemas.EnrollmentUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> schemas.EnrollmentRead:
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    for key, value in enrollment_in.dict(exclude_unset=True).items():
        setattr(enrollment, key, value)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> None:
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    db.delete(enrollment)
    db.commit()
