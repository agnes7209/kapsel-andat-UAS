#Tempat student isi jawab
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from datetime import datetime
from sqlalchemy import and_
from database import get_db
from modules.quiz.models import QuizAnswersModel
from modules.quiz.schema.schemas import QuizAnswer, ResponseAnswerModel

router = APIRouter()

@router.post("/quizanswers/", response_model=ResponseAnswerModel, status_code=201)
def create_quizanswer(quizanswer: QuizAnswer, db: Session = Depends(get_db)):
    # Cek apakah jawaban untuk kombinasi Student_ID, Course_ID, Question_Number sudah ada
    existing_answer = db.query(QuizAnswersModel).filter(
        and_(
            QuizAnswersModel.Student_ID == quizanswer.Student_ID,
            QuizAnswersModel.Course_ID == quizanswer.Course_ID,
            QuizAnswersModel.Question_Number == quizanswer.Question_Number
        )
    ).first()

    if existing_answer:
        raise HTTPException(
            status_code=400, 
            detail=f"Update to change answer."
        )

    # Buat timestamp sekarang
    current_timestamp = datetime.now()

    new_quizanswer = QuizAnswersModel(
        Student_ID= quizanswer.Student_ID,
        Course_ID= quizanswer.Course_ID,
        Quiz_ID= quizanswer.Quiz_ID,
        Quetion_Number= quizanswer.Question_Number,
        Answer= quizanswer.Answer
        Log_Timestamp= current_timestamp 
    )

    db.add(new_quizanswer)
    db.commit()
    db.refresh(new_quizanswer)
    
    return {
        "success": True,
        "message": "New account successfully created",
        "data": {
            Student_ID= new_quizanswer.Student_ID,
            Course_ID= new_quizanswer.Course_ID,
            Quiz_ID= new_quizanswer.Quiz_ID,
            Quetion_Number= new_quizanswer.Question_Number,
            Answer= new_quizanswer.Answer
            Timestamp= new_quizanswer.Log_Timestamp
        }
    }