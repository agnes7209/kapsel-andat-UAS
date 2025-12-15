from pydantic import BaseModel

class IndGrade(BaseModel):
    student_id: str
    quiz_id: str
    course_id: str

class IndGradeResponse(BaseModel):
    student_id: str
    quiz_id: str
    course_id: str
    grade: int

class ResponseIndGradeModel(BaseModel):
    success: bool
    message: str
    data: IndGradeResponse


class AllGrade(BaseModel):
    quiz_id: str
    course_id: str

class AllGradeResponse(BaseModel):
    quiz_id: str
    course_id: str
    total_students: int
    results: str

class ResponseAllGradeModel(BaseModel):
    success: bool
    message: str
    data: AllGradeResponse