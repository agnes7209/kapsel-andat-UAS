from fastapi import FastAPI
from database import Base, engine
from modules.accounts.routers import createAccount, deleteAccount, readAccount, updateAccount
from modules.quiz.routers import createQuizQuestion
import pandas as pd
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Learning Activity Monitoring API")

app.include_router(createAccount.router)
app.include_router(deleteAccount.router)
app.include_router(updateAccount.router)
app.include_router(readAccount.router)

app.include_router(createQuizQuestion.router)


@app.on_event("startup")
def startup_event():
    print("--- Memulai Pra-pemrosesan Data... ---")
    prepare_data() # Panggil fungsi pra-pemrosesan data Anda di sini
    print("--- Pra-pemrosesan Data Selesai. Aplikasi Siap. ---")


def prepare_data():
    folder_path = 'C:/Users/Asus/Documents/KULIAH/SEMESTER/Kapita Selekta Analitika Data/UAS' 
    file_awal = "student_performance_large_dataset.csv"
    file_data_students = "data_students.csv"
    file_account = "accounts.csv"

    if os.path.exists(os.path.join(folder_path,file_data_students)) and os.path.exists(os.path.join(folder_path,file_account)):
        print("✅ Data sudah ada. Proses data dilewati.")
        return

    print("⏳ Data belum ditemukan. Memulai proses pembuatan data...")
    try:
        data = pd.read_csv(os.path.exists(folder_path,file_awal), sep=",")
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

    #UPDATE KE SQL YANG BELUM