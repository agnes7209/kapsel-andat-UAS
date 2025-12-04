from pydantic import BaseModel

class QuizQuestion(BaseModel):
    Quiz_ID: str
    Course_ID: str
    PDF_Name: str
    # Link_Question tidak perlu di input, karena di-generate otomatis

class QuizResponse(BaseModel):
    Quiz_ID: str
    Course_ID: str
    PDF_Name: str
    Link_Question: str

class ResponseModel(BaseModel):
    success: bool
    message: str
    data: QuizResponse