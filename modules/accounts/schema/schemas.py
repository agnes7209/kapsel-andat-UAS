from pydantic import BaseModel
from enum import Enum as PyEnum

class RoleEnum(PyEnum):
    student = "student"
    teacher = "teacher"
    admin = "admin"

class Account(BaseModel):
    Account_ID: str
    Age: int
    Gender: str
    Role: str

class AccountResponse(BaseModel):
    Account_ID: str
    Role: str

class ResponseModel(BaseModel):
    success: bool
    message: str
    data: AccountResponse