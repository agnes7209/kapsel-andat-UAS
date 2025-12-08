from datetime import datetime
from pydantic import BaseModel

class QuizQuestion(BaseModel):
    Quiz_ID: str
    Course_ID: str
    PDF_Name: str
    # Link_Question tidak perlu di input, karena di-generate otomatis

class QuizQuestionResponse(BaseModel):
    Quiz_ID: str
    Course_ID: str
    PDF_Name: str
    Link_Question: str

class ResponseQuestionModel(BaseModel):
    success: bool
    message: str
    data: QuizQuestionResponse


class QuizAnswer(BaseModel):
    Student_ID: str
    Course_ID: str
    Quiz_ID: str
    Question_Number: int
    Answer: str
    # Log_Timestamp tidak perlu di input, karena di-generate otomatis

class QuizAnswerResponse(BaseModel):
    Answer_ID: int
    Student_ID: str
    Course_ID: str
    Quiz_ID: str
    Question_Number: int
    Answer: str
    Timestamp: datetime

class ResponseAnswerModel(BaseModel):
    success: bool
    message: str
    data: QuizAnswerResponse