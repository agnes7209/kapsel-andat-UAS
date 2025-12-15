import random
from sqlalchemy.orm import Session
from database import SessionLocal
from modules.quiz.models import QuizAnswersModel
from modules.students.models import StudentModel
from datetime import datetime

def determine_grade_target(study_hours: int, participation: str) -> str:
    """
    Menentukan target nilai berdasarkan kriteria
    
    Returns: Target grade range ('A', 'AB', 'BC', 'BCD', 'CD', 'E', etc.)
    """
    participation = participation.strip().upper()
    
    # Kriteria 1: Study_Hours_per_Week>= 35 dan Participation_in_Discussions = Yes → A
    if study_hours >= 35 and participation == "YES":
        return "A"
    
    # Kriteria 2: Study_Hours_per_Week>= 35 dan Participation_in_Discussions = No → A/B
    elif study_hours >= 35 and participation == "NO":
        return "AB"
    
    # Kriteria 3: 35>Study_Hours_per_Week>= 27 dan Participation = Yes → A/B
    elif 27 <= study_hours < 35 and participation == "YES":
        return "AB"
    
    # Kriteria 4: 35>Study_Hours_per_Week>= 27 dan Participation = No → A/B/C
    elif 27 <= study_hours < 35 and participation == "NO":
        return "ABC"
    
    # Kriteria 5: 27>Study_Hours_per_Week>=21 dan Participation = Yes → B/C
    elif 21 <= study_hours < 27 and participation == "YES":
        return "BC"
    
    # Kriteria 6: 27>Study_Hours_per_Week>=21 dan Participation = No → B/C/D
    elif 21 <= study_hours < 27 and participation == "NO":
        return "BCD"
    
    # Kriteria 7: 21>Study_Hours_per_Week>=14 dan Participation = Yes → B/C
    elif 14 <= study_hours < 21 and participation == "YES":
        return "BC"
    
    # Kriteria 8: Study_Hours_per_Week<14 dan Participation = Yes → C/D
    elif study_hours < 14 and participation == "YES":
        return "CD"
    
    # Kriteria 9: Study_Hours_per_Week<14 dan Participation = No → E
    elif study_hours < 14 and participation == "NO":
        return "E"
    
    # Fallback
    return "CD"

def get_target_percentage(grade_range: str) -> int:
    """
    Mengonversi grade range ke persentase nilai target
    """
    range_to_percentage = {
        "A": (85, 100),      # A: 85-100%
        "AB": (70, 89),      # A/B: 70-89%
        "ABC": (60, 79),     # A/B/C: 60-79%
        "BC": (65, 79),      # B/C: 65-79%
        "BCD": (55, 74),     # B/C/D: 55-74%
        "CD": (50, 69),      # C/D: 50-69%
        "E": (0, 49)         # E: 0-49%
    }
    
    return range_to_percentage.get(grade_range, (50, 69))

def generate_smart_answer(study_hours: int, participation: str, question_num: int) -> str:
    """
    Menghasilkan jawaban "pintar" berdasarkan profil mahasiswa
    """
    answer_choices = ['A', 'B', 'C', 'D', 'E']
    
    # Tentukan target grade range
    grade_range = determine_grade_target(study_hours, participation)
    min_percent, max_percent = get_target_percentage(grade_range)
    target_percent = random.randint(min_percent, max_percent)
    
    # Hitung probability untuk jawaban benar
    # Misalnya: target 80% benar → probability benar = 0.8
    correct_probability = target_percent / 100
    
    # Untuk beberapa soal pertama, buat lebih mudah (warming up)
    if question_num <= 5:
        correct_probability += 0.1  # Tambah 10% untuk soal mudah
    
    # Untuk soal sulit (akhir), kurangi sedikit
    if question_num >= 16:
        correct_probability -= 0.05
    
    # Batasi probability antara 0.1 dan 0.95
    correct_probability = max(0.1, min(0.95, correct_probability))
    
    # Generate jawaban
    if random.random() < correct_probability:
        # Jawaban benar: pilih A, B, C, D, atau E (acak tapi sesuai pattern)
        # Untuk pattern: lebih sering A/B untuk mahasiswa baik, C/D/E untuk yang kurang
        if grade_range in ["A", "AB"]:
            return random.choice(['A', 'B', 'A', 'B', 'C'])  # 80% A/B
        elif grade_range in ["ABC", "BC"]:
            return random.choice(['B', 'C', 'A', 'B', 'C', 'D'])  # 67% B/C
        elif grade_range in ["BCD", "CD"]:
            return random.choice(['C', 'D', 'B', 'C', 'D', 'E'])  # 67% C/D
        else:  # E
            return random.choice(['D', 'E', 'C', 'D', 'E'])  # 80% D/E
    else:
        # Jawaban salah: pilih acak dari semua pilihan
        return random.choice(answer_choices)

def seed_smart_answers():
    """
    Mengisi jawaban "pintar" yang menghasilkan distribusi nilai sesuai kriteria
    """
    db = SessionLocal()
    try:
        # Cek apakah sudah ada data jawaban
        existing_answers = db.query(QuizAnswersModel).count()
        if existing_answers > 0:
            print(f"⚠️  Tabel log_quizanswer sudah berisi {existing_answers} data. Proses seed dilewati.")
            return

        # Ambil semua mahasiswa dengan data lengkap
        students = db.query(
            StudentModel.Student_ID, 
            StudentModel.Study_Hours_per_Week,
            StudentModel.Participation_in_Discussions
        ).all()
        
        if not students:
            print("❌ Tidak ada data mahasiswa. Pastikan data_students sudah terisi.")
            return
        
        print(f"📊 Mengisi jawaban pintar untuk {len(students)} mahasiswa...")
        
        # Daftar quiz
        quizzes = [
            {"quiz_id": "Q1", "course_id": "Kalkulus", "total_questions": 20},
            {"quiz_id": "Q2", "course_id": "Kalkulus", "total_questions": 20},
            {"quiz_id": "E1", "course_id": "Kalkulus", "total_questions": 20}
        ]
        
        total_records = 0
        
        for student in students:
            student_id = study_hours = participation = student.Student_ID
            study_hours = student.Study_Hours_per_Week
            participation = student.Participation_in_Discussions
            
            # Tentukan target grade untuk mahasiswa ini
            target_range = determine_grade_target(study_hours, participation)
            
            print(f"  Student {student_id}: {study_hours} jam/minggu, Participation: {participation} → Target: {target_range}")
            
            for quiz in quizzes:
                quiz_id = quiz["quiz_id"]
                course_id = quiz["course_id"]
                total_questions = quiz["total_questions"]
                
                # Generate jawaban pintar untuk setiap soal
                for question_num in range(1, total_questions + 1):
                    smart_answer = generate_smart_answer(study_hours, participation, question_num)
                    
                    answer_record = QuizAnswersModel(
                        Student_ID=student_id,
                        Course_ID=course_id,
                        Quiz_ID=quiz_id,
                        Question_Number=question_num,
                        Answer=smart_answer,
                        Log_Timestamp=datetime.now()
                    )
                    
                    db.add(answer_record)
                    total_records += 1
        
        # Commit ke database
        db.commit()
        
        print(f"\n✅ {total_records} jawaban pintar berhasil ditambahkan")
        print(f"   - {len(students)} mahasiswa × 3 quiz × 20 soal = {total_records} records")
        
        # Tampilkan distribusi target
        print("\n📈 DISTRIBUSI TARGET NILAI BERDASARKAN PROFIL:")
        print("-" * 50)
        
        distribution = {}
        for student in students:
            target = determine_grade_target(student.Study_Hours_per_Week, student.Participation_in_Discussions)
            distribution[target] = distribution.get(target, 0) + 1
        
        for target, count in sorted(distribution.items()):
            percentage = (count / len(students)) * 100
            print(f"  {target}: {count} mahasiswa ({percentage:.1f}%)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error saat mengisi jawaban pintar: {str(e)}")
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
    seed_smart_answers()