from sqlalchemy import Column, Integer, String, Float, Text
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

    Log_Timestamp = Column(datetime, primary_key=True, index=True)
    Student_ID = Column(String(10), nullable=False)
    Course_ID = Column(String(10), nullable=False)
    Question_Number = Column(int, nullable=False)
    Answer = Column(String(22), nullable=False)