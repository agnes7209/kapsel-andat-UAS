from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, event
from sqlalchemy.orm import relationship, Session
from modules.quiz.models import QuizAnswersModel
from database import Base, engine
from sqlalchemy import and_
from typing import Dict, List

class StudentModel(Base):
    __tablename__ = "data_students"
    
    Student_ID = Column(String(6), primary_key=True, index=True)
    Study_Hours_per_Week = Column(Integer)
    Participation_in_Discussions = Column(String(3))
    Attendance_Rate_percent = Column(Integer)
    Quiz_Exam_Completion_Rate = Column(Integer)
    Final_Grade = Column(Integer)

# Relationship to StudentGradeModel
    # grades = relationship("StudentGradeModel", back_populates="student")

# class StudentGradeModel(Base):
#     __tablename__= "student_grade"

#     Grade_ID = Column(Integer, primary_key=True, autoincrement=True, index=True)
#     Student_ID = Column(String(10), ForeignKey('data_students.Student_ID'), nullable=False)
#     Quiz_ID = Column(String(20), nullable=True)
#     Course_ID = Column(String(10), nullable=True)
#     Grade = Column(Integer, nullable=True)
#     Is_Calculated = Column(Boolean, default=False)

#     # Relationship to StudentModel
#     student = relationship("StudentModel", back_populates="grades")
#      __table_args__ = (
#         {'sqlite_autoincrement': True},
#     )

# Model untuk solusi Q1
class SolutionQ1(Base):
    __tablename__ = "1998 AP Calculus AB_131-135_1-20 (solutions)"
    
    Number = Column(Integer, primary_key=True)
    Solution = Column(Text, nullable=False)
    Quiz_ID = Column(String(10), default="Q1")

# Model untuk solusi Q2
class SolutionQ2(Base):
    __tablename__ = "1998 AP Calculus BC_144-150_1-20 (solutions)"
    
    Number = Column(Integer, primary_key=True)
    Solution = Column(Text, nullable=False)
    Quiz_ID = Column(String(10), default="Q2")

# Model untuk solusi E1
class SolutionE1(Base):
    __tablename__ = "1997 AP Calculus AB_106-112_1-20 (solutions)"
    
    Number = Column(Integer, primary_key=True)
    Solution = Column(Text, nullable=False)
    Quiz_ID = Column(String(10), default="E1")

class QuizSolutionModel(Base):
    """Model untuk tabel solusi quiz"""
    __tablename__ = "quiz_solutions"  # Ganti dengan nama tabel solusi yang sesuai
    
    Solution_ID = Column(Integer, primary_key=True, autoincrement=True)
    Quiz_ID = Column(String(20), nullable=False)
    Question_Number = Column(Integer, nullable=False)
    Correct_Answer = Column(String(255), nullable=False)
    Solution_Text = Column(Text, nullable=True)  # Untuk penjelasan
    

# Method untuk menghitung grade otomatis
def calculate_grade(db_session, student_id, quiz_id, course_id):
    """
    Menghitung grade berdasarkan jawaban siswa dan solusi
    :param db_session: SQLAlchemy database session
    :param student_id: ID siswa
    :param quiz_id: ID quiz
    :param course_id: ID kursus
    :return: Grade yang dihitung
    """
    try:
        print(f"\n=== Memulai perhitungan grade untuk {student_id}, Quiz: {quiz_id}, Course: {course_id} ===")
        
        # Ambil jawaban siswa dari database
        student_answers = db_session.query(QuizAnswersModel).filter(
            and_(
                QuizAnswersModel.Student_ID == student_id,
                QuizAnswersModel.Quiz_ID == quiz_id,
                QuizAnswersModel.Course_ID == course_id
            )
        ).order_by(QuizAnswersModel.Question_Number).all()
        
        print(f"Jumlah jawaban ditemukan: {len(student_answers)}")
        
        if not student_answers:
            print(f"⚠️ Tidak ditemukan jawaban untuk student_id={student_id}, quiz_id={quiz_id}, course_id={course_id}")
            return 0
        
        # Pilih model solusi berdasarkan Quiz_ID
        solution_model = None
        if quiz_id == "Q1":
            solution_model = SolutionQ1
            print("Menggunakan solusi Q1")
        elif quiz_id == "Q2":
            solution_model = SolutionQ2
            print("Menggunakan solusi Q2")
        elif quiz_id == "E1":
            solution_model = SolutionE1
            print("Menggunakan solusi E1")
        else:
            print(f"❌ Quiz ID {quiz_id} tidak dikenali")
            return 0
        
        # Ambil solusi dari database
        solutions = db_session.query(solution_model).order_by(solution_model.Number).all()
        
        print(f"Jumlah solusi ditemukan: {len(solutions)}")
        
        if not solutions:
            print(f"❌ Tidak ditemukan solusi untuk quiz_id={quiz_id}")
            return 0
        
        # Debug: Tampilkan beberapa solusi
        print("Contoh solusi (5 pertama):")
        for sol in solutions[:5]:
            print(f"  Soal {sol.Number}: {sol.Solution[:50]}...")
        
        # Debug: Tampilkan beberapa jawaban
        print("Contoh jawaban siswa (5 pertama):")
        for ans in student_answers[:5]:
            print(f"  Soal {ans.Question_Number}: {ans.Answer}")
        
        # Hitung persentase benar
        correct_count = 0
        total_questions = len(solutions)
        
        # Buat dictionary untuk solusi agar lebih mudah diakses
        solution_dict = {sol.Number: sol.Solution for sol in solutions}
        
        print(f"\nMembandingkan {len(student_answers)} jawaban dengan {len(solutions)} solusi:")
        
        for answer in student_answers:
            if answer.Question_Number in solution_dict:
                # Bandingkan jawaban siswa dengan solusi
                student_answer = str(answer.Answer).strip().lower() if answer.Answer else ""
                correct_solution = str(solution_dict[answer.Question_Number]).strip().lower()
                
                print(f"  Soal {answer.Question_Number}: Siswa='{student_answer}', Kunci='{correct_solution}'")
                
                if student_answer and student_answer == correct_solution:
                    correct_count += 1
                    print(f"    ✅ BENAR!")
                else:
                    print(f"    ❌ SALAH")
        
        # Hitung grade
        grade = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        # Bulatkan ke integer terdekat
        grade = round(grade)
        
        print(f"\nHasil: {correct_count} benar dari {total_questions} soal = {grade}%")
        
        # Cek apakah grade sudah ada
        existing_grade = db_session.query(StudentGradeModel).filter(
            and_(
                StudentGradeModel.Student_ID == student_id,
                StudentGradeModel.Quiz_ID == quiz_id,
                StudentGradeModel.Course_ID == course_id
            )
        ).first()
        
        if existing_grade:
            # Update grade yang sudah ada
            existing_grade.Grade = grade
            print(f"✓ Grade diperbarui di database")
        else:
            # Buat record grade baru
            new_grade = StudentGradeModel(
                Student_ID=student_id,
                Quiz_ID=quiz_id,
                Course_ID=course_id,
                Grade=grade
            )
            db_session.add(new_grade)
            print(f"✓ Grade baru ditambahkan ke database")
        
        # Commit perubahan ke database
        db_session.commit()
        
        print(f"✓ Grade berhasil dihitung untuk {student_id}: {grade}%\n")
        return grade
        
    except Exception as e:
        print(f"❌ Error dalam calculate_grade: {str(e)}")
        import traceback
        traceback.print_exc()
        db_session.rollback()
        return 0




def calculate_grades_for_all_students(db_session, quiz_id, course_id):
    """
    Menghitung grade untuk semua siswa yang telah mengerjakan quiz tertentu
    """
    try:
        # Ambil semua student_id unik yang memiliki jawaban untuk quiz ini
        student_ids = db_session.query(QuizAnswersModel.Student_ID).filter(
            and_(
                QuizAnswersModel.Quiz_ID == quiz_id,
                QuizAnswersModel.Course_ID == course_id
            )
        ).distinct().all()
        
        print(f"Menghitung grade untuk {len(student_ids)} siswa...")
        
        results = []
        for (student_id,) in student_ids:
            grade = calculate_grade(db_session, student_id, quiz_id, course_id)
            results.append({
                'student_id': student_id,
                'grade': grade
            })
        
        return results
        
    except Exception as e:
        print(f"Error dalam calculate_grades_for_all_students: {str(e)}")
        return []