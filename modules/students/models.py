from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, event, Float, Enum, func
from sqlalchemy.orm import relationship, Session
from modules.quiz.models import QuizAnswersModel
from database import Base, engine
from sqlalchemy import and_
from typing import Dict, List
import enum

# Enum untuk Grade
class GradeLetter(enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"

class StudentModel(Base):
    __tablename__ = "data_students"
    
    Student_ID = Column(String(6), primary_key=True, index=True)
    Study_Hours_per_Week = Column(Integer)
    Participation_in_Discussions = Column(String(3))
    Attendance_Rate_percent = Column(Integer)
    Quiz_Exam_Completion_Rate = Column(Integer, default=0)
    Final_Grade = Column(String(1))

    # Relationship to StudentGradeModel
    grades = relationship("StudentGradeModel", back_populates="student")

class StudentGradeModel(Base):
    __tablename__ = "student_grade"

    Grade_ID = Column(Integer, primary_key=True, autoincrement=True, index=True)
    Student_ID = Column(String(10), ForeignKey('data_students.Student_ID'), nullable=False)
    Quiz_ID = Column(String(20), nullable=True)
    Course_ID = Column(String(10), nullable=True)
    Grade = Column(Integer, nullable=True)  

    # Relationship to StudentModel
    student = relationship("StudentModel", back_populates="grades")

# Model untuk solusi Q1
class SolutionQ1(Base):
    __tablename__ = "quiz1_solutions_1998_ap_calculus_ab"
    
    Number = Column(Integer, primary_key=True)
    Solution = Column(Text, nullable=False)

# Model untuk solusi Q2
class SolutionQ2(Base):
    __tablename__ = "quiz2_solutions_1998_ap_calculus_bc"
    
    Number = Column(Integer, primary_key=True)
    Solution = Column(Text, nullable=False)

# Model untuk solusi E1
class SolutionE1(Base):
    __tablename__ = "exam1_solutions_1997_ap_calculus_ab"
    
    Number = Column(Integer, primary_key=True)
    Solution = Column(Text, nullable=False)

class QuizSolutionModel(Base):
    """Model untuk tabel solusi quiz"""
    __tablename__ = "quiz_solutions"
    
    Solution_ID = Column(Integer, primary_key=True, autoincrement=True)
    Quiz_ID = Column(String(20), nullable=False)
    Question_Number = Column(Integer, nullable=False)
    Correct_Answer = Column(String(255), nullable=False)
    Solution_Text = Column(Text, nullable=True)

# Fungsi untuk menghitung nilai per quiz di QuizAnswersModel(log_quizanswer)
def calculate_and_save_grades(db_session: Session, 
                            quiz_id: str, 
                            course_id: str = "Kalkulus",
                            student_id: str = None):
    """
    Menghitung dan menyimpan nilai quiz ke database
    
    Parameters:
    - student_id: Jika None, hitung untuk semua mahasiswa
    - quiz_id: Q1, Q2, atau E1
    - course_id: Default "Kalkulus"
    """
    try:
        # Tentukan mahasiswa mana yang akan dihitung
        if student_id:
            students_query = db_session.query(StudentModel.Student_ID).filter(
                StudentModel.Student_ID == student_id
            )
            print(f"📊 Menghitung nilai {quiz_id} untuk mahasiswa {student_id}...")
        else:
            students_query = db_session.query(StudentModel.Student_ID)
            print(f"📊 Menghitung nilai {quiz_id} untuk semua mahasiswa...")
        
        students = students_query.all()
        
        if not students:
            print(f"⚠️ Tidak ada mahasiswa ditemukan")
            return 0
        
        total_calculated = 0
        total_questions = 20  # Semua quiz ada 20 soal
        
        # Tentukan model solusi
        if quiz_id == "Q1":
            solution_model = SolutionQ1
        elif quiz_id == "Q2":
            solution_model = SolutionQ2
        elif quiz_id == "E1":
            solution_model = SolutionE1
        else:
            print(f"⚠️ Quiz ID {quiz_id} tidak dikenali")
            return 0
        
        # Ambil semua solusi sekaligus (lebih efisien)
        solutions = db_session.query(solution_model).all()
        if not solutions:
            print(f"⚠️ Tidak ada solusi untuk quiz {quiz_id}")
            return 0
        
        # Buat dictionary solusi untuk akses cepat
        solution_dict = {sol.Number: sol.Solution.strip().lower() for sol in solutions}
        
        for (student_id,) in students:
            # Ambil semua jawaban mahasiswa untuk quiz ini
            student_answers = db_session.query(QuizAnswersModel).filter(
                and_(
                    QuizAnswersModel.Student_ID == student_id,
                    QuizAnswersModel.Quiz_ID == quiz_id,
                    QuizAnswersModel.Course_ID == course_id
                )
            ).all()
            
            # Hitung nilai
            if not student_answers:
                grade = 0  # Tidak ada jawaban
            else:
                correct_count = 0
                for answer in student_answers:
                    question_num = answer.Question_Number
                    if question_num in solution_dict:
                        student_answer = answer.Answer.strip().lower() if answer.Answer else ""
                        if student_answer == solution_dict[question_num]:
                            correct_count += 1
                
                grade = int((correct_count / total_questions) * 100)
            
            # Simpan atau update ke database
            existing_grade = db_session.query(StudentGradeModel).filter(
                and_(
                    StudentGradeModel.Student_ID == student_id,
                    StudentGradeModel.Quiz_ID == quiz_id,
                    StudentGradeModel.Course_ID == course_id
                )
            ).first()
            
            if existing_grade:
                existing_grade.Grade = grade
            else:
                new_grade = StudentGradeModel(
                    Student_ID=student_id,
                    Quiz_ID=quiz_id,
                    Course_ID=course_id,
                    Grade=grade
                )
                db_session.add(new_grade)
            
            total_calculated += 1
        
        # Commit sekali untuk semua perubahan
        db_session.commit()
        
        print(f"✅ {total_calculated} nilai {quiz_id} telah dihitung dan disimpan")
        return total_calculated
        
    except Exception as e:
        db_session.rollback()
        print(f"❌ Error menghitung nilai {quiz_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0
    # Hitung untuk semua mahasiswa
        # calculate_and_save_grades(db, "Q1", "Kalkulus")

    # Hitung untuk satu mahasiswa
        # calculate_and_save_grades(db, "Q1", "Kalkulus", "S00001")

# Fungsi untuk menghitung Quiz_Exam_Completion_Rate di data_students
def calculate_completion_rate(db_session: Session, student_id: str) -> int:
    """
    Menghitung persentase quiz dan exam yang telah diikuti mahasiswa
    """
    try:
        # Total quiz yang tersedia (Q1, Q2, E1)
        total_quizzes = 3
        
        # Hitung berapa banyak quiz yang sudah dijawab oleh mahasiswa
        answered_quizzes = db_session.query(QuizAnswersModel.Quiz_ID)\
            .filter(QuizAnswersModel.Student_ID == student_id)\
            .distinct()\
            .count()
        
        # Hitung persentase
        if total_quizzes > 0:
            completion_rate = (answered_quizzes / total_quizzes) * 100
        else:
            completion_rate = 0
        
        return int(completion_rate)
        
    except Exception as e:
        print(f"❌ Error dalam calculate_completion_rate: {str(e)}")
        return 0
# Fungsi untuk menghitung Final_Grade di data_students berdasarkan semua nilai quiz
def calculate_final_grade(db_session: Session, student_id: str) -> str:
    """
    Menghitung nilai akhir (A/B/C/D/E) berdasarkan semua nilai quiz
    """
    try:
        # Ambil semua nilai quiz yang sudah dihitung untuk mahasiswa ini
        grades = db_session.query(StudentGradeModel.Grade)\
            .filter(
                and_(
                    StudentGradeModel.Student_ID == student_id,
                    StudentGradeModel.Course_ID == "Kalkulus",
                    StudentGradeModel.Quiz_ID.in_(["Q1", "Q2", "E1"])
                )
            )\
            .all()
        
        if not grades:
            print(f"⚠️ Mahasiswa {student_id} belum memiliki nilai quiz")
            return "E"  # Default grade jika tidak ada nilai
        
        # Filter hanya nilai yang tidak NULL
        valid_grades = [grade[0] for grade in grades if grade[0] is not None]
        
        if not valid_grades:
            print(f"⚠️ Mahasiswa {student_id} memiliki nilai NULL semua")
            return "E"

        # Hitung rata-rata semua nilai quiz (bobot sama)
        total_grade = sum(valid_grades)
        average_grade = total_grade / len(valid_grades)
        
        print(f"📊 Perhitungan {student_id}: Total={total_grade}, Rata-rata={average_grade:.2f}, Jumlah quiz={len(valid_grades)}")
        
        # Konversi ke Grade Letter berdasarkan range
        if average_grade >= 77:
            return "A"
        elif average_grade >= 67:
            return "B"
        elif average_grade >= 60:
            return "C"
        elif average_grade >= 50:
            return "D"
        else:
            return "E"
            
    except Exception as e:
        print(f"❌ Error dalam calculate_final_grade: {str(e)}")
        return "E"
# Fungsi untuk memperbarui kolom-kolom di tabel data_students
def update_student_grades(db_session: Session, student_id: str = None):
    """
    Memperbarui Quiz_Exam_Completion_Rate dan Final_Grade
    - Jika student_id diberikan: update hanya mahasiswa tersebut
    - Jika student_id=None: update semua mahasiswa
    """
    try:
        if student_id:
            # Update hanya satu mahasiswa
            students_query = db_session.query(StudentModel).filter(
                StudentModel.Student_ID == student_id
            )
            print(f"⏳ Memperbarui nilai untuk mahasiswa {student_id}...")
        else:
            # Update semua mahasiswa
            students_query = db_session.query(StudentModel)
            print(f"⏳ Memperbarui nilai untuk semua mahasiswa...")
        
        students = students_query.all()
        
        if not students:
            print(f"⚠️ Tidak ada mahasiswa ditemukan")
            return
        
        updated_count = 0
        
        for student in students:
            # Hitung completion rate
            completion_rate = calculate_completion_rate(db_session, student.Student_ID)
            
            # Hitung final grade
            final_grade = calculate_final_grade(db_session, student.Student_ID)
            
            # Update data student
            student.Quiz_Exam_Completion_Rate = completion_rate
            student.Final_Grade = final_grade
            
            updated_count += 1
        
        # COMMIT SEKALI untuk semua perubahan
        db_session.commit()
        
        if student_id:
            print(f"✅ Nilai mahasiswa {student_id} diperbarui: Completion={completion_rate}%, Grade={final_grade}")
        else:
            print(f"✅ {updated_count} nilai mahasiswa telah diperbarui")
        
    except Exception as e:
        db_session.rollback()
        if student_id:
            print(f"❌ Error memperbarui nilai mahasiswa {student_id}: {str(e)}")
        else:
            print(f"❌ Error memperbarui nilai semua mahasiswa: {str(e)}")
        import traceback
        traceback.print_exc()
    # Update satu mahasiswa
        # update_student_grades(db, "S00001")

    # Update semua mahasiswa 
        # update_student_grades(db)  # atau update_student_grades(db, None)

