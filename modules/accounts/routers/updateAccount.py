from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from database import get_db
from modules.accounts.models import AccountModel
from modules.accounts.schema.schemas import Account, AccountUpdate, ResponseModel

router =APIRouter()

@router.put("/accounts/{Account_ID}/{code}/", response_model=ResponseModel)
def update_account(Account_ID: str, code:str, updated_account: Account, db: Session = Depends(get_db)):
    account = db.query(AccountModel).filter(AccountModel.Account_ID == Account_ID).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if code != "kode_update":
        raise HTTPException(status_code=403, detail="Wrong code, don't have permission to update.")

    if updated_account.Account_ID != Account_ID:
        existing_account = db.query(AccountModel).filter(AccountModel.Account_ID == updated_account.Account_ID).first()
        if existing_account:
            raise HTTPException(status_code=400, detail=f"Cannot update. Account_ID '{updated_account.Account_ID}' already exists in the database.")
    
    # Full update
    account.Account_ID = updated_account.Account_ID
    account.Age = updated_account.Age
    account.Gender = updated_account.Gender
    account.Role = updated_account.Role

    db.commit()
    db.refresh(account)

    return {
        "success": True,
        "message": "Account successfully updated",
        "data": account
    }