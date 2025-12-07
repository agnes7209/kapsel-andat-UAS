from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from database import get_db
from modules.accounts.models import AccountModel
from modules.accounts.schema.schemas import ResponseModel

router = APIRouter()

@router.get("/accounts/{Account_ID}/", response_model=ResponseModel)
def get_account(Account_ID: str, db: Session = Depends(get_db)):
    account = db.query(AccountModel).filter(AccountModel.Account_ID == Account_ID).first()
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )
    return{
            "success": True,
            "message": "Account successfully fetched",
            "data": account
    }