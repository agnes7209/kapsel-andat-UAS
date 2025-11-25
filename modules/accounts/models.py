from sqlalchemy import Column, Integer, String, Float, Text, Enum
from database import Base

class AccountModel(Base):
    __tablename__= "accounts"

    Account_ID = Column(String(20), primary_key=True, index=True)
    Age = Column(Integer, nullable=False)
    Gender = Column(String(20), nullable=False)
    Role = Column(Enum(RoleEnum), nullable=False)

class RoleEnum(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"