#Tempat student isi jawab
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from sqlalchemy import and_
from datetime import datetime
from database import get_db
from modules.quiz.models import QuizAnswersModel
from modules.quiz.schema.schemas import QuizAnswer, ResponseAnswerModel

router = APIRouter()

@router.post("/quizanswers/", response_model=ResponseAnswerModel, status_code=201)
def create_quizanswer(quizanswer: QuizAnswer, db: Session = Depends(get_db)):
    # Cek apakah jawaban untuk kombinasi Student_ID, Course_ID, Quiz_ID, Question_Number sudah ada
    existing_answer = db.query(QuizAnswersModel).filter(
        and_(
            QuizAnswersModel.Student_ID == quizanswer.Student_ID,
            QuizAnswersModel.Course_ID == quizanswer.Course_ID,
            QuizAnswersModel.Quiz_ID == quizanswer.Quiz_ID,
            QuizAnswersModel.Question_Number == quizanswer.Question_Number
        )
    ).first()

    if existing_answer:
        raise HTTPException(
            status_code=400, 
            detail=f"Jawaban untuk soal ini sudah ada. Gunakan endpoint update untuk mengubah jawaban."
        )

    new_quizanswer = QuizAnswersModel(
        Student_ID= quizanswer.Student_ID,
        Course_ID= quizanswer.Course_ID,
        Quiz_ID= quizanswer.Quiz_ID,
        Question_Number= quizanswer.Question_Number,
        Answer= quizanswer.Answer
    )

    try:
        db.add(new_quizanswer)
        db.commit()
        db.refresh(new_quizanswer)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan jawaban: {str(e)}")
    
    return {
        "success": True,
        "message": "Jawaban quiz berhasil disimpan",
        "data": {
            "Answer_ID": new_quizanswer.Answer_ID,
            "Student_ID": new_quizanswer.Student_ID,
            "Course_ID": new_quizanswer.Course_ID,
            "Quiz_ID": new_quizanswer.Quiz_ID,
            "Question_Number": new_quizanswer.Question_Number,
            "Answer": new_quizanswer.Answer,
            "Timestamp": new_quizanswer.Log_Timestamp
        }
    }