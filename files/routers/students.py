from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, require_role
from ..security import get_password_hash

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_student(
    student_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> schemas.UserRead:
    if db.query(models.User).filter(models.User.email == student_in.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if student_in.role and student_in.role != models.UserRole.STUDENT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be student")
    db_student = models.User(
        full_name=student_in.full_name,
        email=student_in.email,
        hashed_password=get_password_hash(student_in.password),
        role=models.UserRole.STUDENT,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.get("", response_model=list[schemas.UserRead])
def list_students(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> list[schemas.UserRead]:
    return db.query(models.User).filter(models.User.role == models.UserRole.STUDENT).all()


@router.get("/{student_id}", response_model=schemas.UserRead)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> schemas.UserRead:
    student = db.query(models.User).filter(
        models.User.id == student_id, models.User.role == models.UserRole.STUDENT
    ).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=schemas.UserRead)
def update_student(
    student_id: int,
    student_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> schemas.UserRead:
    student = db.query(models.User).filter(
        models.User.id == student_id, models.User.role == models.UserRole.STUDENT
    ).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    if student_in.email and student_in.email != student.email:
        if db.query(models.User).filter(models.User.email == student_in.email).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        student.email = student_in.email
    if student_in.full_name:
        student.full_name = student_in.full_name
    if student_in.password:
        student.hashed_password = get_password_hash(student_in.password)
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role(models.UserRole.ADMIN)),
) -> None:
    student = db.query(models.User).filter(
        models.User.id == student_id, models.User.role == models.UserRole.STUDENT
    ).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    db.delete(student)
    db.commit()
