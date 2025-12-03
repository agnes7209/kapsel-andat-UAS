from pydantic import BaseModel
import re

class QuizQuestions(BaseModel):
    Quiz_ID: str
    Course_ID: str
    Link_Question: str

    @validator('Link_Question')
    def validate_pdf_filename(cls, v):
        if not v.endswith('.pdf'):
            raise ValueError('File harus berformat PDF (.pdf)')
        return v

class QuizResponse(BaseModel):
    Account_ID: str
    Role: str

class ResponseModel(BaseModel):
    success: bool
    message: str
    data: QuizResponse

class QuizUpdate(BaseModel):
    Account_ID: str
    Age: int
    Gender: str
    Role: str