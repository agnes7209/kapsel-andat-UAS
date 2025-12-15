from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from modules.students.models import calculate_grade, calculate_grades_for_all_students
from modules.students.schema.schemas import ResponseIndGradeModel, ResponseAllGradeModel, AllGrade, IndGrade

router = APIRouter()

@router.post("/individual_grade/{student_id}/{quiz_id}/{course_id}/", response_model=ResponseIndGradeModel, status_code=201)
async def calculate_single_grade(indgrade: IndGrade, db: Session = Depends(get_db)):
    try:   
        grade = calculate_grade(
            db, 
            indgrade.student_id, 
            indgrade.quiz_id, 
            indgrade.course_id
        )
        if grade == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Tidak dapat menghitung grade. Pastikan data jawaban dan solusi tersedia."
            )
        
        return {
            "exists": True,
            "message": "Grade berhasil dihitung",
            "data": {
                "student_id": indgrade.student_id,
                "quiz_id": indgrade.quiz_id,
                "course_id": indgrade.course_id,
                "grade": grade
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error menghitung grade: {str(e)}"
        )

@router.post("/all_grade/{student_id}/{quiz_id}/{course_id}/", response_model=ResponseAllGradeModel, status_code=201)
async def calculate_all_grades(allgrade: AllGrade, db: Session = Depends(get_db)):
    try:   
        # Gunakan fungsi baru untuk menghitung semua siswa
        from modules.students.models import calculate_grades_for_all_students
        results = calculate_grades_for_all_students(
            db, 
            allgrade.quiz_id, 
            allgrade.course_id
        )
        
        return {
            "exists": True,
            "message": "Grade berhasil dihitung untuk semua siswa",
            "data": {
                "quiz_id": allgrade.quiz_id,
                "course_id": allgrade.course_id,
                "total_students": len(results),
                "results": results
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error menghitung grade semua siswa: {str(e)}"
        )

@router.get("/individual_grade/{student_id}/{quiz_id}/{course_id}/", response_model=ResponseIndGradeModel)
async def check_existing_grade(indgrade: IndGrade, db: Session = Depends(get_db)):
    from modules.students.models import StudentGradeModel
    from sqlalchemy import and_
    
    existing_grade = db.query(StudentGradeModel).filter(
        and_(
            StudentGradeModel.Student_ID == student_id,
            StudentGradeModel.Quiz_ID == quiz_id,
            StudentGradeModel.Course_ID == course_id
        )
    ).first()
    
    if existing_grade:
        return {
            "exists": True,
            "message": "New account successfully created",
            "data": {
                "student_id": student_id,
                "quiz_id": quiz_id,
                "course_id": course_id,
                "grade": existing_grade.Grade
            }
        }
    else:
        return {
            "exists": False,
            "message": "Grade belum dihitung"
        }