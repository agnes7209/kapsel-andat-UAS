import random
from sqlalchemy.orm import Session
from database import SessionLocal
from modules.quiz.models import QuizAnswersModel
from modules.students.models import StudentModel
from datetime import datetime

def seed_random_answers():
    """
    Mengisi jawaban acak untuk semua mahasiswa (200 mahasiswa)
    untuk quiz Q1, Q2, dan E1 dengan Course_ID 'Kalkulus'
    """
    db = SessionLocal()
    try:
        # Cek apakah sudah ada data jawaban
        existing_answers = db.query(QuizAnswersModel).count()
        if existing_answers > 0:
            print(f"⚠️  Tabel log_quizanswer sudah berisi {existing_answers} data. Proses seed dilewati.")
            return

        # Ambil semua mahasiswa dari data_students
        students = db.query(StudentModel.Student_ID).all()
        
        if not students:
            print("❌ Tidak ada data mahasiswa. Pastikan data_students sudah terisi.")
            return
        
        print(f"📊 Mengisi jawaban acak untuk {len(students)} mahasiswa...")
        
        # Daftar quiz dengan jumlah soal masing-masing
        quizzes = [
            {"quiz_id": "Q1", "course_id": "Kalkulus", "total_questions": 20},
            {"quiz_id": "Q2", "course_id": "Kalkulus", "total_questions": 20},
            {"quiz_id": "E1", "course_id": "Kalkulus", "total_questions": 20}
        ]
        
        # Pilihan jawaban
        answer_choices = ['A', 'B', 'C', 'D', 'E']
        
        total_records = 0
        
        for student in students:
            student_id = student.Student_ID
            
            for quiz in quizzes:
                quiz_id = quiz["quiz_id"]
                course_id = quiz["course_id"]
                total_questions = quiz["total_questions"]
                
                # Generate jawaban acak untuk setiap soal
                for question_num in range(1, total_questions + 1):
                    random_answer = random.choice(answer_choices)
                    
                    answer_record = QuizAnswersModel(
                        Student_ID=student_id,
                        Course_ID=course_id,
                        Quiz_ID=quiz_id,
                        Question_Number=question_num,
                        Answer=random_answer,
                        Log_Timestamp=datetime.now()
                    )
                    
                    db.add(answer_record)
                    total_records += 1
        
        # Commit ke database
        db.commit()
        
        print(f"✅ {total_records} jawaban acak berhasil ditambahkan untuk {len(students)} mahasiswa")
        print(f"   - Setiap mahasiswa mengerjakan 3 quiz (Q1, Q2, E1)")
        print(f"   - Setiap quiz memiliki 20 soal")
        print(f"   - Total: {len(students)} × 3 × 20 = {total_records} records")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error saat mengisi jawaban acak: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def clear_all_answers():
    """
    Menghapus semua data jawaban (hati-hati: untuk debugging saja)
    """
    db = SessionLocal()
    try:
        count = db.query(QuizAnswersModel).count()
        db.query(QuizAnswersModel).delete()
        db.commit()
        print(f"🗑️  {count} data jawaban telah dihapus")
    except Exception as e:
        db.rollback()
        print(f"❌ Error menghapus data: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    # Untuk menjalankan secara langsung
    seed_random_answers()