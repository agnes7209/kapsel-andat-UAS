from sqlalchemy import Column, Integer, String
from sqlalchemy.types import Enum as SQLAlchemyEnum
from enum import Enum as PyEnum
from database import Base

class RoleEnum(PyEnum):
    student = "student"
    teacher = "teacher"
    admin = "admin"

class AccountModel(Base):
    __tablename__= "accounts"

    Account_ID = Column(String(6), primary_key=True, index=True)
    Age = Column(Integer, nullable=False)
    Gender = Column(String(6), nullable=False)
    Role = Column(String(225), nullable=False)