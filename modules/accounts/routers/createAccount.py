from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session 
from database import get_db
from modules.accounts.models import AccountModel
from modules.accounts.schema.schemas import Account, ResponseModel

router = APIRouter()

@router.post("/accounts/", response_model=ResponseModel)
def create_account(account: Account, db: Session = Depends(get_db)):
    new_account = AccountModel(
        Account_ID = account.Account_ID, 
        Age = account.Age,
        Gender = account.Gender,
        Role = account.Role
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    
    return {
        "success": True,
        "message": "New account successfully created",
        "data": {
            "Account_ID": new_account.Account_ID,
            "Role": new_account.Role
        }
    }