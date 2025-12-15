from sqlalchemy.orm import Session
from database import SessionLocal
from modules.students.models import StudentModel

def should_fix_grades() -> bool:
    """
    Mengecek apakah semua mahasiswa memiliki nilai E
    Return True jika 100% nilai adalah E
    """
    db = SessionLocal()
    try:
        total_students = db.query(StudentModel).count()
        if total_students == 0:
            return False
        
        e_students = db.query(StudentModel).filter(
            StudentModel.Final_Grade == 'E'
        ).count()
        
        # Hitung persentase
        percentage_e = (e_students / total_students) * 100
        
        print(f"📊 Status nilai mahasiswa:")
        print(f"  - Total mahasiswa: {total_students}")
        print(f"  - Nilai E: {e_students}")
        print(f"  - Persentase E: {percentage_e:.1f}%")
        
        return percentage_e == 100.0
        
    except Exception as e:
        print(f"❌ Error mengecek status nilai: {str(e)}")
        return False
    finally:
        db.close()

def normalize_participation(participation: str) -> str:
    """Normalisasi nilai participation menjadi YES atau NO"""
    if participation is None:
        return "NO"
    
    part_str = str(participation).strip().upper()
    
    if part_str in ["YES", "Y", "1", "TRUE"]:
        return "YES"
    elif part_str in ["NO", "N", "0", "FALSE"]:
        return "NO"
    
    # Default parsing
    if "YES" in part_str or "Y" == part_str[0]:
        return "YES"
    else:
        return "NO"

def determine_final_grade(study_hours: int, participation: str) -> str:
    """
    Menentukan Final_Grade berdasarkan kriteria yang diberikan
    
    Kriteria:
    1. Study_Hours_per_Week>= 35 dan Participation_in_Discussions = Yes → A
    2. Study_Hours_per_Week>= 35 dan Participation_in_Discussions = No → A/B 
    3. 35>Study_Hours_per_Week>= 27 dan Participation_in_Discussions = Yes → A/B
    4. 35>Study_Hours_per_Week>= 27 dan Participation_in_Discussions = No → A/B/C
    5. 27>Study_Hours_per_Week>=21 dan Participation_in_Discussions = Yes → B/C
    6. 27>Study_Hours_per_Week>=21 dan Participation_in_Discussions = No → B/C/D 
    7. 21>Study_Hours_per_Week>=14 dan Participation_in_Discussions = Yes → B/C
    8. Study_Hours_per_Week<14 dan Participation_in_Discussions = Yes → C/D
    9. Study_Hours_per_Week<14 dan Participation_in_Discussions = No → E
    """
    part_norm = normalize_participation(participation)
    
    # Kriteria 1: >=35 jam dan Yes → A
    if study_hours >= 35 and part_norm == "YES":
        return "A"
    
    # Kriteria 2: >=35 jam dan No → A/B (random antara A dan B)
    elif study_hours >= 35 and part_norm == "NO":
        import random
        return random.choice(["A", "B"])
    
    # Kriteria 3: 27-34 jam dan Yes → A/B
    elif 27 <= study_hours < 35 and part_norm == "YES":
        import random
        return random.choice(["A", "B"])
    
    # Kriteria 4: 27-34 jam dan No → A/B/C
    elif 27 <= study_hours < 35 and part_norm == "NO":
        import random
        return random.choice(["A", "B", "C"])
    
    # Kriteria 5: 21-26 jam dan Yes → B/C
    elif 21 <= study_hours < 27 and part_norm == "YES":
        import random
        return random.choice(["B", "C"])
    
    # Kriteria 6: 21-26 jam dan No → B/C/D
    elif 21 <= study_hours < 27 and part_norm == "NO":
        import random
        return random.choice(["B", "C", "D"])
    
    # Kriteria 7: 14-20 jam dan Yes → B/C
    elif 14 <= study_hours < 21 and part_norm == "YES":
        import random
        return random.choice(["B", "C"])
    
    # Kriteria 8: <14 jam dan Yes → C/D
    elif study_hours < 14 and part_norm == "YES":
        import random
        return random.choice(["C", "D"])
    
    # Kriteria 9: <14 jam dan No → E
    elif study_hours < 14 and part_norm == "NO":
        return "E"
    
    # Fallback (seharusnya tidak terjadi)
    return "E"

def fix_final_grades():
    """
    Memperbaiki Final_Grade pada tabel data_students berdasarkan kriteria
    Hanya dijalankan jika 100% mahasiswa memiliki nilai E
    """
    print("\n🔧 MENGECEK DAN MEMPERBAIKI FINAL GRADE...")
    print("=" * 50)
    
    # Cek apakah perlu diperbaiki
    if not should_fix_grades():
        print("❌ Tidak perlu memperbaiki: tidak semua mahasiswa bernilai E")
        print("ℹ️  Program akan berhenti di sini")
        return False
    
    print("✅ Kondisi terpenuhi: 100% mahasiswa bernilai E")
    print("⏳ Memulai perbaikan Final Grade...")
    
    db = SessionLocal()
    try:
        # Ambil semua mahasiswa
        students = db.query(StudentModel).all()
        total_students = len(students)
        
        print(f"\n📊 Memproses {total_students} mahasiswa...")
        
        # Counter untuk statistik
        grade_distribution = {
            "A": 0, "B": 0, "C": 0, "D": 0, "E": 0
        }
        
        # Update setiap mahasiswa
        for i, student in enumerate(students, 1):
            # Tentukan Final Grade berdasarkan kriteria
            final_grade = determine_final_grade(
                student.Study_Hours_per_Week,
                student.Participation_in_Discussions
            )
            
            # Update Final Grade
            student.Final_Grade = final_grade
            
            # Hitung distribusi
            grade_distribution[final_grade] += 1
            
            # Tampilkan progress setiap 50 mahasiswa
            if i % 50 == 0:
                print(f"  Progress: {i}/{total_students}")
        
        # Commit perubahan
        db.commit()
        
        # Tampilkan hasil
        print("\n✅ PERBAIKAN SELESAI!")
        print("=" * 50)
        print("📈 DISTRIBUSI FINAL GRADE BARU:")
        for grade, count in grade_distribution.items():
            percentage = (count / total_students) * 100
            print(f"  {grade}: {count} mahasiswa ({percentage:.1f}%)")
        
        # Tampilkan contoh data
        print("\n👨‍🎓 CONTOH PERUBAHAN (5 mahasiswa pertama):")
        print("-" * 40)
        sample_students = db.query(StudentModel).limit(5).all()
        for student in sample_students:
            print(f"  {student.Student_ID}: {student.Study_Hours_per_Week} jam, "
                  f"Partisipasi: {student.Participation_in_Discussions} → "
                  f"Final Grade: {student.Final_Grade}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error memperbaiki Final Grade: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

# def force_fix_grades():
#     """
#     Memperbaiki Final_Grade tanpa cek kondisi (force mode)
#     Hanya untuk debugging/testing
#     """
#     print("⚠️  FORCE MODE: Memperbaiki Final Grade tanpa cek kondisi...")
#     return fix_final_grades()

if __name__ == "__main__":
    # Untuk menjalankan secara langsung
    fix_final_grades()