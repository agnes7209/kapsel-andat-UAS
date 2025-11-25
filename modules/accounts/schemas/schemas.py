from pydantic import BaseModel

class Account(BaseModel):
    Account_ID : str
    Age : int
    Gender : str
    Role : enum

class AccountResponse(BaseModel):
    Account_ID: str
    Role: enum

class ResponseModel(BaseModel):
    success: bool
    message: str
    data: AccountResponse