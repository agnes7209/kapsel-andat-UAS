from fastapi import FastAPI
from database import Base, engine, SessionLocal
from modules.accounts.routers import createAccount, deleteAccount, readAccount, updateAccount
from modules.quiz.routers import createQuizQuestion, deleteQuizQuestion, readQuizQuestion, createQuizAnswer
import pandas as pd
import os
from tqdm import tqdm 

# Import model
from modules.students.models import StudentModel, calculate_and_save_grades, update_student_grades
from modules.accounts.models import AccountModel

# Import fungsi seed
from modules.quiz.seed_answers import seed_random_answers, clear_all_answers 

app = FastAPI(title="Learning Activity Monitoring API")

app.include_router(createAccount.router)
app.include_router(deleteAccount.router)
app.include_router(updateAccount.router)
app.include_router(readAccount.router)

app.include_router(createQuizQuestion.router)
app.include_router(deleteQuizQuestion.router)
app.include_router(readQuizQuestion.router)
app.include_router(createQuizAnswer.router)


@app.on_event("startup")
def startup_event():
    print("=" * 60)
    print("🚀 SISTEM PEMANTAUAN PEMBELAJARAN ONLINE - STARTUP")
    print("=" * 60)
    
    print("\n📋 Langkah 1: Pra-pemrosesan Data...")
    prepare_data()
    print("✅ Pra-pemrosesan Data Selesai")
    
    print("\n📋 Langkah 2: Membuat dan Mengisi Database...")
    setup_database()
    print("✅ Database Siap")
    
    print("\n📋 Langkah 3: Mengisi Jawaban Acak Mahasiswa...")
    seed_random_answers()  # INI YANG DITAMBAHKAN
    print("✅ Jawaban Acak Terisi")
    
    print("\n📋 Langkah 4: Menghitung dan Memperbarui Nilai...")
    calculate_and_update_all_grades()
    print("✅ Perhitungan Nilai Selesai")
    
    print("\n" + "=" * 60)
    print("✅ APLIKASI SIAP DIGUNAKAN")
    print("=" * 60)

# Definisikan variabel global untuk path
folder_path = 'C:/Users/Asus/Documents/KULIAH/SEMESTER/Kapita Selekta Analitika Data/UAS' 
file_awal = "student_performance_large_dataset.csv"
file_data_students = "data_students.csv"
file_account = "accounts.csv"

def prepare_data():
    # Path lengkap untuk file
    path_data_students = os.path.join(folder_path, file_data_students)
    path_account = os.path.join(folder_path, file_account)
    path_file_awal = os.path.join(folder_path, file_awal)

    if os.path.exists(path_data_students) and os.path.exists(path_account):
        print("✅ Data sudah ada. Proses data dilewati.")
        return

    print("⏳ Data belum ditemukan. Memulai proses pembuatan data...")
    # Cek apakah file sumber ada
    if not os.path.exists(path_file_awal):
        print(f"❌ Error: File sumber '{path_file_awal}' tidak ditemukan. Tidak dapat membuat data.")
        return
    try:
        data = pd.read_csv(path_file_awal, sep=",")
        print(f"✅ File sumber berhasil dibaca. Jumlah data: {len(data)} baris")
    except FileNotFoundError:
        print(f"❌ Error: File sumber '{os.path.exists(folder_path,file_awal)}' tidak ditemukan. Tidak dapat membuat data.")
        return

    # --- Persiapan data_student.csv ---
    data_student = data.drop(['Age',
                            'Preferred_Learning_Style',
                            'Online_Courses_Completed',
                            'Assignment_Completion_Rate (%)',
                            'Exam_Score (%)',
                            'Use_of_Educational_Tech',
                            'Self_Reported_Stress_Level',
                            'Time_Spent_on_Social_Media (hours/week)',
                            'Sleep_Hours_per_Night',
                            'Final_Grade'],
                             axis=1)
    data_student = data_student.rename(columns={'Attendance_Rate (%)': 'Attendance_Rate_percent'})
    data_student = data_student[data_student['Gender'] != 'Other']
    data_student = data_student.drop('Gender', axis=1)
    data_student = data_student.drop(index=data_student.index[200:]) 

    # Tambahkan kolom kosong untuk Quiz_Exam_Completion_Rate dan Final Grade
    data_student['Quiz_Exam_Completion_Rate'] = 0  
    data_student['Final_Grade'] = 'E'

    file_name_student = 'data_student.csv'
    data_student.to_csv(os.path.join(folder_path, file_data_students), index=False)
    print(f"File '{file_data_students}' berhasil dibuat.")

    # --- Persiapan accounts.csv ---
    data_account = data.drop(['Study_Hours_per_Week',
                            'Participation_in_Discussions',
                            'Attendance_Rate (%)',
                            'Preferred_Learning_Style',
                            'Online_Courses_Completed',
                            'Assignment_Completion_Rate (%)',
                            'Exam_Score (%)',
                            'Use_of_Educational_Tech',
                            'Self_Reported_Stress_Level',
                            'Time_Spent_on_Social_Media (hours/week)',
                            'Sleep_Hours_per_Night',
                            'Final_Grade'],
                             axis=1)
    data_account['Role'] = 'student'
    data_account= data_account[data_account['Gender'] != 'Other']
    data_account = data_account.rename(columns={'Student_ID': 'Account_ID'})
    data_account = data_account.drop(index=data_account.index[200:]) 
    
    file_name_account = 'accounts.csv'
    data_account.to_csv(os.path.join(folder_path, file_account), index=False)
    print(f"File '{file_account}' berhasil dibuat.")

def setup_database():
    """Membuat tabel dan mengimpor data dari CSV ke database"""
    print("--- Membuat tabel database... ---")
    
    # Tampilkan tabel yang akan dibuat
    print(f"✅ Tabel yang akan dibuat: {Base.metadata.tables.keys()}")
    
    # Membuat semua tabel yang didefinisikan oleh Base
    Base.metadata.create_all(bind=engine)
    print("✅ Tabel berhasil dibuat/diperiksa")
    
    db = SessionLocal()
    
    try:
        # 1. Impor data ke tabel accounts
        print("⏳ Mengimpor data accounts ke database...")
        accounts_path = os.path.join(folder_path, file_account)
        
        if os.path.exists(accounts_path):
            accounts_df = pd.read_csv(accounts_path)
            print(f"📊 Data accounts dari CSV: {len(accounts_df)} baris")
            print(f"📋 Kolom accounts: {list(accounts_df.columns)}")
            
            # Cek apakah tabel sudah ada data
            existing_accounts = db.query(AccountModel).count()
            
            if existing_accounts == 0:
                accounts_data = accounts_df.to_dict('records')
                
                # Debug: Tampilkan contoh data pertama
                if accounts_data:
                    print(f"📝 Contoh data accounts pertama: {accounts_data[0]}")
                
                # Masukkan data ke database
                for record in tqdm(accounts_data, desc="Accounts"):
                    try:
                        account = AccountModel(
                            Account_ID=str(record['Account_ID']),
                            Age=int(record['Age']),
                            Gender=str(record['Gender']),
                            Role=str(record['Role'])
                        )
                        db.add(account)
                    except Exception as e:
                        print(f"❌ Error pada record {record}: {str(e)}")
                        raise
                
                db.commit()
                print(f"✅ {len(accounts_data)} data accounts berhasil diimpor")
            else:
                print(f"ℹ️  Tabel accounts sudah berisi {existing_accounts} data, dilewati")
        else:
            print(f"❌ File {file_account} tidak ditemukan di {accounts_path}")
        
        # 2. Impor data ke tabel students
        print("\n⏳ Mengimpor data students ke database...")
        students_path = os.path.join(folder_path, file_data_students)
        
        if os.path.exists(students_path):
            students_df = pd.read_csv(students_path)
            print(f"📊 Data students dari CSV: {len(students_df)} baris")
            print(f"📋 Kolom students: {list(students_df.columns)}")
            
            # Cek apakah tabel sudah ada data
            existing_students = db.query(StudentModel).count()
            
            if existing_students == 0:
                students_data = students_df.to_dict('records')
                
                # Debug: Tampilkan contoh data pertama
                if students_data:
                    print(f"📝 Contoh data students pertama: {students_data[0]}")
                
                # Masukkan data ke database
                for record in tqdm(students_data, desc="Students"):
                    try:
                        # Konversi ke tipe data yang benar
                        student = StudentModel(
                            Student_ID=str(record['Student_ID']),
                            Study_Hours_per_Week=int(record['Study_Hours_per_Week']),
                            Participation_in_Discussions=str(record['Participation_in_Discussions']),
                            Quiz_Exam_Completion_Rate=int(record['Quiz_Exam_Completion_Rate']),
                            Attendance_Rate_percent=int(record['Attendance_Rate_percent']),
                            Final_Grade=int(record['Final_Grade'])
                        )
                        db.add(student)
                    except Exception as e:
                        print(f"❌ Error pada record {record}: {str(e)}")
                        raise
                
                db.commit()
                print(f"✅ {len(students_data)} data students berhasil diimpor")
            else:
                print(f"ℹ️  Tabel students sudah berisi {existing_students} data, dilewati")
        else:
            print(f"❌ File {file_data_students} tidak ditemukan di {students_path}")
        
        # Verifikasi data yang sudah diimpor
        print("\n✅ Verifikasi data di database:")
        print(f"   - Total accounts: {db.query(AccountModel).count()}")
        print(f"   - Total students: {db.query(StudentModel).count()}")
        
        # Tampilkan contoh data
        print("\n📊 Contoh 3 data accounts:")
        for account in db.query(AccountModel).limit(3).all():
            print(f"   - {account.Account_ID}, Age: {account.Age}, Gender: {account.Gender}, Role: {account.Role}")
        
        print("\n📊 Contoh 3 data students:")
        for student in db.query(StudentModel).limit(3).all():
            print(f"   - {student.Student_ID}, Study Hours: {student.Study_Hours_per_Week}, Attendance: {student.Attendance_Rate_percent}%")
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error saat mengimpor data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e
    finally:
        db.close()

def calculate_and_update_all_grades():
    """
    Menghitung nilai quiz dan memperbarui data_students
    """
    from database import SessionLocal

    db = SessionLocal()
    try:
        print("📊 Langkah 1: Menghitung nilai quiz Q1, Q2, E1...")
        
        # Hitung nilai untuk setiap quiz (semua mahasiswa)
        calculate_and_save_grades(db, "Q1", "Kalkulus")
        calculate_and_save_grades(db, "Q2", "Kalkulus")
        calculate_and_save_grades(db, "E1", "Kalkulus")
        
        print("📊 Langkah 2: Memperbarui completion rate dan final grade...")
        update_student_grades(db)
        
        print("✅ Semua perhitungan nilai selesai")
    except Exception as e:
        print(f"❌ Error dalam perhitungan nilai: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()