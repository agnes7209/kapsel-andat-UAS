from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from database import get_db
from modules.accounts.models import AccountModel
from modules.accounts.schema.schemas import ResponseModel

router = APIRouter()

@router.get("/accounts/", response_model=ResponseModel)
def get_accounts(db: Session = Depends(get_db)):
    accounts = db.query(AccountModel).all()
    return {
        "success": True,
        "message": "Accounts successfully fetched",
        "data": accounts
    }

@router.get("/accounts/{Account_ID}", response_model=ResponseModel)
def get_accounts(Account_ID: int, db: Session = Depends(get_db)):
    account = db.query(AccountModel).filter(AccountModel.id == Account_ID).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

        return{
            "success": True,
            "massage": "Account successfully fetched",
            "data": account
        }
