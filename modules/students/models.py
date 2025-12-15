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
    Grade = Column(Float, nullable=True)  # Changed to Float for decimal values

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

# Fungsi untuk menghitung Quiz_Exam_Completion_Rate
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

# Fungsi untuk menghitung Final_Grade berdasarkan semua nilai quiz
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
                    StudentGradeModel.Is_Calculated == True
                )
            )\
            .all()
        
        if not grades:
            return "E"  # Default grade jika tidak ada nilai
        
        # Hitung rata-rata semua nilai quiz (bobot sama)
        total_grade = sum([grade[0] for grade in grades if grade[0] is not None])
        average_grade = total_grade / len(grades)
        
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

# Fungsi untuk memperbarui nilai student di tabel data_students
def update_student_grades(db_session: Session, student_id: str):
    """
    Memperbarui Quiz_Exam_Completion_Rate dan Final_Grade untuk mahasiswa
    """
    try:
        # Hitung completion rate
        completion_rate = calculate_completion_rate(db_session, student_id)
        
        # Hitung final grade
        final_grade = calculate_final_grade(db_session, student_id)
        
        # Update data di tabel students
        student = db_session.query(StudentModel).filter(
            StudentModel.Student_ID == student_id
        ).first()
        
        if student:
            student.Quiz_Exam_Completion_Rate = completion_rate
            student.Final_Grade = final_grade
            db_session.commit()
            print(f"✅ Data student {student_id} diperbarui: Completion={completion_rate}%, Grade={final_grade}")
        else:
            print(f"❌ Student {student_id} tidak ditemukan")
            
    except Exception as e:
        db_session.rollback()
        print(f"❌ Error dalam update_student_grades: {str(e)}")

# Fungsi untuk memperbarui semua student
def update_all_students_grades(db_session: Session):
    """
    Memperbarui nilai untuk semua mahasiswa
    """
    try:
        # Ambil semua student
        students = db_session.query(StudentModel).all()
        
        print(f"⏳ Memperbarui nilai untuk {len(students)} mahasiswa...")
        
        for student in students:
            update_student_grades(db_session, student.Student_ID)
            
        print(f"✅ Semua nilai mahasiswa telah diperbarui")
        
    except Exception as e:
        print(f"❌ Error dalam update_all_students_grades: {str(e)}")

# Method untuk menghitung grade otomatis dengan perbaikan
def calculate_grade(db_session, student_id, quiz_id, course_id):
    """
    Menghitung grade berdasarkan jawaban siswa dan solusi
    """
    try:
        print(f"\n=== Memulai perhitungan grade untuk {student_id}, Quiz: {quiz_id} ===")
        
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
            print(f"⚠️ Tidak ditemukan jawaban untuk student_id={student_id}, quiz_id={quiz_id}")
            # Tandai sebagai tidak dikerjakan tapi buat record dengan nilai 0
            create_empty_grade_record(db_session, student_id, quiz_id, course_id)
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
                
                # Debug output hanya untuk beberapa soal pertama
                if answer.Question_Number <= 5:
                    print(f"  Soal {answer.Question_Number}: Siswa='{student_answer}', Kunci='{correct_solution}'")
                
                if student_answer and student_answer == correct_solution:
                    correct_count += 1
        
        # Hitung grade dalam persentase
        grade = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        # Bulatkan ke 2 desimal
        grade = round(grade, 2)
        
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
            existing_grade.Is_Calculated = True
            print(f"✓ Grade diperbarui di database")
        else:
            # Buat record grade baru
            new_grade = StudentGradeModel(
                Student_ID=student_id,
                Quiz_ID=quiz_id,
                Course_ID=course_id,
                Grade=grade,
                Is_Calculated=True
            )
            db_session.add(new_grade)
            print(f"✓ Grade baru ditambahkan ke database")
        
        # Commit perubahan ke database
        db_session.commit()
        
        # Update nilai student setelah menghitung grade
        update_student_grades(db_session, student_id)
        
        print(f"✓ Grade berhasil dihitung untuk {student_id}: {grade}%\n")
        return grade
        
    except Exception as e:
        print(f"❌ Error dalam calculate_grade: {str(e)}")
        import traceback
        traceback.print_exc()
        db_session.rollback()
        return 0

def create_empty_grade_record(db_session, student_id, quiz_id, course_id):
    """
    Membuat record grade dengan nilai 0 untuk quiz yang tidak dikerjakan
    """
    try:
        # Cek apakah record sudah ada
        existing_grade = db_session.query(StudentGradeModel).filter(
            and_(
                StudentGradeModel.Student_ID == student_id,
                StudentGradeModel.Quiz_ID == quiz_id,
                StudentGradeModel.Course_ID == course_id
            )
        ).first()
        
        if not existing_grade:
            new_grade = StudentGradeModel(
                Student_ID=student_id,
                Quiz_ID=quiz_id,
                Course_ID=course_id,
                Grade=0.0,
                Is_Calculated=True
            )
            db_session.add(new_grade)
            db_session.commit()
            print(f"✓ Record grade kosong dibuat untuk {student_id}, quiz {quiz_id}")
            
    except Exception as e:
        print(f"❌ Error dalam create_empty_grade_record: {str(e)}")
        db_session.rollback()

def calculate_grades_for_all_students(db_session, quiz_id, course_id):
    """
    Menghitung grade untuk semua siswa yang telah mengerjakan quiz tertentu
    """
    try:
        # Ambil semua student_id dari tabel students
        students = db_session.query(StudentModel.Student_ID).all()
        
        print(f"Menghitung grade untuk {len(students)} siswa pada quiz {quiz_id}...")
        
        results = []
        for (student_id,) in students:
            # Untuk setiap student, hitung grade (akan membuat record dengan nilai 0 jika tidak ada jawaban)
            grade = calculate_grade(db_session, student_id, quiz_id, course_id)
            results.append({
                'student_id': student_id,
                'grade': grade
            })
        
        # Update semua nilai student setelah menghitung semua grade
        update_all_students_grades(db_session)
        
        return results
        
    except Exception as e:
        print(f"Error dalam calculate_grades_for_all_students: {str(e)}")
        return []

# Event listener untuk memperbarui nilai otomatis ketika ada perubahan di QuizAnswersModel
@event.listens_for(QuizAnswersModel, 'after_insert')
@event.listens_for(QuizAnswersModel, 'after_update')
@event.listens_for(QuizAnswersModel, 'after_delete')
def update_grades_on_answer_change(mapper, connection, target):
    """
    Memperbarui nilai secara otomatis ketika ada perubahan pada jawaban quiz
    """
    db_session = Session(bind=connection)
    try:
        student_id = target.Student_ID
        quiz_id = target.Quiz_ID
        course_id = target.Course_ID
        
        print(f"⏳ Memperbarui nilai setelah perubahan jawaban untuk {student_id}, quiz {quiz_id}")
        
        # Hitung ulang grade untuk quiz ini
        calculate_grade(db_session, student_id, quiz_id, course_id)
        
    except Exception as e:
        print(f"❌ Error dalam update_grades_on_answer_change: {str(e)}")
    finally:
        db_session.close()