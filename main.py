from fastapi import FastAPI
from database import Base, engine, SessionLocal
from modules.accounts.routers import createAccount, deleteAccount, readAccount, updateAccount
from modules.quiz.routers import createQuizQuestion, deleteQuizQuestion
import pandas as pd
import os

# Import model di sini untuk menghindari circular import
from modules.students.models import StudentModel
from modules.accounts.models import AccountModel

app = FastAPI(title="Learning Activity Monitoring API")

app.include_router(createAccount.router)
app.include_router(deleteAccount.router)
app.include_router(updateAccount.router)
app.include_router(readAccount.router)

app.include_router(createQuizQuestion.router)
app.include_router(deleteQuizQuestion.router)

@app.on_event("startup")
def startup_event():
    print("--- Memulai Pra-pemrosesan Data... ---")
    prepare_data() # Panggil fungsi pra-pemrosesan data Anda di sini
    print("--- Pra-pemrosesan Data Selesai. Aplikasi Siap. ---")
    print("--- Membuat dan Mengisi Database... ---")
    setup_database() # Panggil fungsi setup database
    print("--- Aplikasi Siap. ---")

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
    data_student = data.drop(['Preferred_Learning_Style',
                              'Use_of_Educational_Tech',
                              'Self_Reported_Stress_Level',
                              'Time_Spent_on_Social_Media (hours/week)',
                              'Sleep_Hours_per_Night'],
                             axis=1)

    data_student = data_student[data_student['Gender'] != 'Other']
    data_student = data_student.drop(index=data_student.index[200:]) 

    file_name_student = 'data_student.csv'
    data_student.to_csv(os.path.join(folder_path, file_data_students), index=False)
    print(f"File '{file_data_students}' berhasil dibuat.")

    # --- Persiapan accounts.csv ---
    data_account = data_student.drop(['Study_Hours_per_Week',
                                      'Online_Courses_Completed',
                                      'Participation_in_Discussions',
                                      'Assignment_Completion_Rate (%)',
                                      'Exam_Score (%)',
                                      'Attendance_Rate (%)',
                                      'Final_Grade'],
                                     axis=1)
    data_account['Role'] = 'student'
    data_account = data_account.rename(columns={'Student_ID': 'Account_ID'})
    
    file_name_account = 'accounts.csv'
    data_account.to_csv(os.path.join(folder_path, file_account), index=False)
    print(f"File '{file_account}' berhasil dibuat.")

# def setup_database(): #Membuat tabel dan mengisi data dari CSV ke database
#     print("--- Memulai Pembuatan Database SQL... ---")
#     # Buat semua tabel yang didefinisikan dalam Base
#     try:
#         Base.metadata.create_all(bind=engine)
#         print("✅ Tabel database berhasil dibuat/diperiksa.")
#     except Exception as e:
#         print(f"❌ Error membuat tabel: {e}")
#         return
    
#     # Path untuk file CSV
#     path_data_students = os.path.join(folder_path, file_data_students)
#     path_account = os.path.join(folder_path, file_account)

#     db = SessionLocal()
    
#     try:
#         # Cek apakah tabel sudah berisi data
#         student_count = db.query(StudentModel).count()
#         account_count = db.query(AccountModel).count()
        
#         print(f"📊 Jumlah data di tabel students: {student_count}")
#         print(f"📊 Jumlah data di tabel accounts: {account_count}")

#         # Jika tabel kosong, isi dari CSV
#         if student_count == 0 and os.path.exists(path_data_students):
#             print("⏳ Mengisi tabel students dari CSV...")
#             students_df = pd.read_csv(path_data_students)

#             # Konversi ke dictionary untuk bulk insert
#             students_data = students_df.to_dict(orient='records')

#             # Bulk insert
#             inserted_count = 0
#             for data in students_data:
#                 try:
#                 # Konversi tipe data 
#                     data['Student_ID'] = str(data['Student_ID'])
#                     data['Age'] = int(data['Age'])
#                     data['Gender'] = str(data['Gender'])
#                     data['Study_Hours_per_Week'] = int(data['Study_Hours_per_Week'])
#                     data['Online_Courses_Completed'] = int(data['Online_Courses_Completed'])
#                     data['Participation_in_Discussions'] = str(data['Participation_in_Discussions'])
#                     data['Assignment_Completion_Rate (%)'] = int(data['Assignment_Completion_Rate_percent'])
#                     data['Exam_Score (%)'] = int(data['Exam_Score_percent'])
#                     data['Attendance_Rate (%),Final_Grade'] = int(data['Attendance_Rate_percent'])

#                     student = StudentModel(**data)
#                     db.add(student)
#                     inserted_count += 1
#                 except Exception as e:
#                     print(f"⚠️ Error memproses data student: {data.get('Student_ID', 'Unknown')} - {e}")
#             db.commit()
#             print(f"✅ Tabel students berhasil diisi dengan {inserted_count} data.")        
        
#         if account_count == 0 and os.path.exists(path_account):
#             print("⏳ Mengisi tabel accounts dari CSV...")
#             accounts_df = pd.read_csv(path_account)
            
#             # Konversi ke dictionary untuk bulk insert
#             accounts_data = accounts_df.to_dict(orient='records')
            
#             # Bulk insert
#             inserted_accounts = 0
#             for data in accounts_data:
#                 try:
#                     # Konversi tipe data
#                     data['Account_ID'] = str(data['Account_ID'])
#                     data['Age'] = int(data['Age'])
#                     data['Gender'] = str(data['Gender'])
#                     data['Role'] = str(data['Role'])
        
#                     account = AccountModel(**data)
#                     db.add(account)
#                     inserted_accounts += 1
#                 except Exception as e:
#                     print(f"⚠️ Error memproses data account: {data.get('Account_ID', 'Unknown')} - {e}")
#             db.commit()
#             print(f"✅ Tabel accounts berhasil diisi dengan {inserted_accounts} data.")
        
#         if student_count > 0 and account_count > 0:
#             print("✅ Database sudah berisi data. Tidak ada data baru yang dimasukkan.")
            
#     except Exception as e:
#         db.rollback()
#         print(f"❌ Error mengisi database: {e}")
#     finally:
#         db.close()

