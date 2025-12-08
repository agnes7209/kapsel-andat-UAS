from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class QuizQuestionsModel(Base):
    __tablename__= "log_quizquestion"

    Quiz_ID = Column(String(20), primary_key=True, index=True)
    Course_ID = Column(String(20), nullable=False)
    PDF_Name = Column(String(225), nullable=False)
    Link_Question = Column(String(225), nullable=False)

class QuizAnswersModel(Base):
    __tablename__= "log_quizanswer"

    Answer_ID = Column(Integer, primary_key=True, autoincrement=True, index=True)
    Log_Timestamp = Column(DateTime, default=datetime.utcnow)
    Student_ID = Column(String(10), nullable=False)
    Course_ID = Column(String(10), nullable=False)
    Quiz_ID = Column(String(10), nullable=False)
    Question_Number = Column(Integer, nullable=False)
    Answer = Column(String(255), nullable=True)