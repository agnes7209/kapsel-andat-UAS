from sqlalchemy import Column, Integer, String, Float, Text
from database import Base

class QuizQuestionsModel(Base):
    __tablename__= "log_quizquestion"

    Quiz_ID = Column(String(20), primary_key=True, index=True)
    Course_ID = Column(String(20), nullable=False)
    Link_Question = Column(String(225), nullable=False)
  