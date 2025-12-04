#Tempat untuk buat soal 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from database import get_db
from modules.quiz.models import QuizQuestionsModel
from modules.quiz.schema.schemas import QuizQuestion, ResponseModel
import urllib.parse
import httpx 

router = APIRouter()

# Konfigurasi GitHub repository
GITHUB_USER = "agnes7209"
GITHUB_REPO = "kapsel-andat-UAS"
GITHUB_BRANCH = "main"
GITHUB_FOLDER = "quiz_questionaries"  # Folder di repo untuk menyimpan PDF

# Base URL untuk file di GitHub (format raw)
GITHUB_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_FOLDER}/"

async def check_pdf_exists_in_github(PDF_Name: str) -> bool:
    # Mengecek apakah file PDF ada di repository GitHub
    pdf_name_encoded = urllib.parse.quote(PDF_Name)
    raw_url = f"{GITHUB_BASE_URL}{pdf_name_encoded}"
    
    try:
        async with httpx.AsyncClient() as client:
            # Coba akses file langsung
            response = await client.head(raw_url)  # Gunakan HEAD untuk hanya cek header
            
            # Jika response 200, file ditemukan
            if response.status_code == 200:
                return True
            else:
                print(f"File not found. Status code: {response.status_code}")
                print(f"URL checked: {raw_url}")
                return False
    except Exceptionas as e:
        print(f"Error checking PDF: {e}")
        return False

@router.post("/quizquestions/", response_model=ResponseModel, status_code=201)
async def create_quizquestion(quizquestion: QuizQuestion, db: Session = Depends(get_db)):
    # Cek apakah Quiz_ID sudah ada
    existing_quiz = db.query(QuizQuestionsModel).filter(QuizQuestionsModel.Quiz_ID == quizquestion.Quiz_ID).first()
    if existing_quiz:
        raise HTTPException(
            status_code=400, 
            detail=f"Quiz_ID '{quizquestion.Quiz_ID}' sudah terdaftar di database."
        )
    
    # Panggil fungsi validasi PDF
    pdf_exists = await check_pdf_exists_in_github(quizquestion.PDF_Name)
    if not pdf_exists:
        raise HTTPException(
            status_code=400,
            detail=
            f"File PDF '{quizquestion.PDF_Name}' tidak ditemukan di repository GitHub."
            f"Pastikan file sudah diupload ke: {GITHUB_BASE_URL}."
        )

    # Generate link otomatis dari nama PDF
    pdf_name_encoded = urllib.parse.quote(quizquestion.PDF_Name)
    link_question = f"{GITHUB_BASE_URL}pdf_questions/{pdf_name_encoded}"

     # Buat objek baru
    new_quizquestion = QuizQuestionsModel(
        Quiz_ID = quizquestion.Quiz_ID, 
        Course_ID = quizquestion.Course_ID,
        PDF_Name = quizquestion.PDF_Name,
        Link_Question = generated_link
    )

    db.add(new_quizquestion)
    db.commit()
    db.refresh(new_quizquestion)
    
    return {
        "success": True,
        "message": "New quiz question successfully created",
        "data": {
            "Quiz_ID": new_question.Quiz_ID,
            "Course_ID": new_question.Course_ID,
            "PDF_Name": new_question.PDF_Name,
            "Link_Question": new_question.Link_Question  # Link akan langsung bisa dibuka
        }
    }