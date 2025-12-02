from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from database import get_db
from modules.accounts.models import AccountModel
from modules.accounts.schema.schemas import Account, ResponseModel

router = APIRouter()

@router.post("/accounts/", response_model=ResponseModel, status_code=201)
def create_account(account: Account, db: Session = Depends(get_db)):
    new_account = AccountModel(
        Account_ID = account.Account_ID, 
        Age = account.Age,
        Gender = account.Gender,
        Role = account.Role
    )
    
    existing_account = db.query(AccountModel).filter(AccountModel.Account_ID == account.Account_ID).first()
    if existing_account:
        raise HTTPException(status_code=400, detail=f"Cannot create account. Account_ID '{account.Account_ID}' already exists in the database.")
    

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