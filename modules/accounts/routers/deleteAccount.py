from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from database import get_db
from modules.accounts.models import AccountModel
from modules.accounts.schema.schemas import ResponseModel

router = APIRouter()

@router.delete("/accounts/{Account_ID}/")
def delete_account(Account_ID: str, db: Session = Depends(get_db)):
    account = db.query(AccountModel).filter(AccountModel.Account_ID == Account_ID).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(account)
    db.commit()
    
    return {
        "success": True,
        "message": f"Account {Account_ID} deleted.",
    }