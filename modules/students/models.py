from sqlalchemy import Column, Integer, String, Float
from database import Base

class StudentModel(Base):
    __tablename__ = "students"
    
    Student_ID = Column(String(6), primary_key=True, index=True)
    Age = Column(Integer, nullable=False)
    Gender = Column(String(10), nullable=False)
    Study_Hours_per_Week = Column(Integer, nullable=False)
    Online_Courses_Completed = Column(Integer, nullable=False)
    Participation_in_Discussions = Column(String(3), nullable=False)
    Assignment_Completion_Rate_percent = Column(Integer, nullable=False)
    Exam_Score_percent = Column(Integer, nullable=False)
    Attendance_Rate_percent = Column(Integer, nullable=False)
    Final_Grade = Column(String(2), nullable=False)