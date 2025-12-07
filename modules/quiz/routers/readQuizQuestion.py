#Nampilin soal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from database import get_db
from modules.quiz.models import QuizQuestionsModel
from modules.quiz.schema.schemas import ResponseQuestionModel
router = APIRouter()

@router.get("/quizquestions/{Quiz_ID}/", response_model=ResponseQuestionModel)
def get_quizquestion(Quiz_IDResponseQuestionModel: str, db: Session = Depends(get_db)):
    existing_quiz = db.query(QuizQuestionsModel).filter(QuizQuestionsModel.Quiz_ID == Quiz_ID).first()
    if not existing_quiz:
        raise HTTPException(
            status_code=404, 
            detail="Quiz questions not found."
        )
    return {
        "success": True,
        "message": "Quiz Openned",
        "data": existing_quiz
    }