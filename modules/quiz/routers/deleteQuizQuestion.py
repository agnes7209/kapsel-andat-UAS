from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from database import get_db
from modules.quiz.models import QuizQuestionsModel
from modules.quiz.schema.schemas import QuizQuestion, ResponseModel


router = APIRouter()

@router.delete("/quizquestions/{Quiz_ID}/")
def delete_quizquestion(Quiz_ID: str, db: Session = Depends(get_db)):
    quizquestion = db.query(QuizQuestionsModel).filter(QuizQuestionsModel.Quiz_ID == Quiz_ID).first()

    if not quizquestion:
        raise HTTPException(status_code=404, detail="Quiz ID not found")

    db.delete(quizquestion)
    db.commit()
    
    return {
        "success": True,
        "message": f"Quiz question {Quiz_ID} deleted.",
    }