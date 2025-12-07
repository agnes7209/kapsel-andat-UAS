#Tempat untuk penamaan/assign soal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from database import get_db
from modules.quiz.models import QuizQuestionsModel
from modules.quiz.schema.schemas import QuizQuestion, ResponseQuestionModel
import urllib.parse
import httpx 
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# Konfigurasi GitHub repository
GITHUB_USER = "agnes7209"
GITHUB_REPO = "kapsel-andat-UAS"
GITHUB_BRANCH = "main"
GITHUB_FOLDER = "quiz_questionaries"  # Folder di repo untuk menyimpan PDF

# Base URL untuk file di GitHub (format raw)
GITHUB_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_FOLDER}/"

async def check_pdf_exists_in_github(PDF_Name: str) -> tuple[bool, str]:
     # Coba berbagai variasi nama file
    test_cases = []
    
     # Nama asli
    test_cases.append(PDF_Name)

    # Tambah ekstensi jika belum ada
    if not PDF_Name.lower().endswith('.pdf'):
        test_cases.append(f"{PDF_Name}.pdf")
        test_cases.append(f"{PDF_Name}.PDF")
    
    # Tambah encoding alternatif
    test_cases.append(PDF_Name.replace(" ", "%20"))
    test_cases.append(PDF_Name.replace(" ", "_"))
    
    logger.info(f"Mencari file: {PDF_Name}")
    logger.info(f"Base URL: {GITHUB_BASE_URL}")

    for filename in test_cases:
        # Encode nama file
        encoded_name = urllib.parse.quote(filename)
        raw_url = f"{GITHUB_BASE_URL}{encoded_name}"
        
        logger.info(f"Mencoba URL: {raw_url}")
    
        try:
            async with httpx.AsyncClient() as client:
                # Gunakan GET untuk cek lebih akurat
                response = await client.get(raw_url, timeout=10.0) 
            
                # Jika response 200, file ditemukan
                if response.status_code == 200:
                    # Cek content type untuk memastikan ini PDF
                    content_type = response.headers.get('content-type', '')
                    if 'application/pdf' in content_type or 'application/octet-stream' in content_type:
                        logger.info(f"✓ FILE PDF DITEMUKAN: {raw_url}")
                        return True, raw_url
                    elif 'text/html' in content_type:
                        # Mungkin halaman 404 atau redirect
                        logger.warning(f"URL mengembalikan HTML, bukan PDF: {raw_url}")
                        continue
                    else:
                        logger.info(f"✓ FILE DITEMUKAN (content-type: {content_type}): {raw_url}")
                        return True, raw_url
                else:
                    logger.debug(f"✗ Status {response.status_code}: {raw_url}")
                    
        except httpx.TimeoutException:
            logger.warning(f"Timeout untuk: {raw_url}")
        except Exception as e:
            logger.error(f"Error: {e} untuk URL: {raw_url}")
    
    logger.error(f"File '{PDF_Name}' tidak ditemukan di semua lokasi yang dicoba")
    return False, ""

@router.post("/quizquestions/", response_model=ResponseQuestionModel, status_code=201)
async def create_quizquestion(quizquestion: QuizQuestion, db: Session = Depends(get_db)):
    # Cek apakah Quiz_ID sudah ada
    existing_quiz = db.query(QuizQuestionsModel).filter(QuizQuestionsModel.Quiz_ID == quizquestion.Quiz_ID).first()
    if existing_quiz:
        raise HTTPException(
            status_code=400, 
            detail=f"Quiz_ID '{quizquestion.Quiz_ID}' sudah terdaftar di database."
        )
    
    # Panggil fungsi validasi PDF
    logger.info(f"Memulai validasi PDF: {quizquestion.PDF_Name}")
    pdf_exists, pdf_url = await check_pdf_exists_in_github(quizquestion.PDF_Name)
    if not pdf_exists:
        # Dapatkan struktur folder dari GitHub untuk pesan error yang informatif
        repo_url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/tree/{GITHUB_BRANCH}/{GITHUB_FOLDER}"
        raise HTTPException(
            status_code=400,
            detail=(
                f"File PDF '{quizquestion.PDF_Name}' tidak ditemukan di repository GitHub"
                f"Silakan periksa struktur folder di: {repo_url}"
                f"Pastikan:"
                f"1. File sudah diupload ke folder '{GITHUB_FOLDER}/'"
                f"2. Nama file persis sama (termasuk kapitalisasi dan ekstensi)"
                f"3. Repository bersifat PUBLIC (bukan private)"
                f"4. Coba akses manual: {GITHUB_BASE_URL}[nama-file-anda].pdf"
            )
        )

    # Gunakan URL yang berhasil ditemukan
    link_question = pdf_url

    # Simpan nama file yang sebenarnya (sesuai yang ditemukan di GitHub)
    # Ekstrak nama file dari URL
    actual_filename = pdf_url.split('/')[-1]
    actual_filename = urllib.parse.unquote(actual_filename)

     # Buat objek baru
    new_quizquestion = QuizQuestionsModel(
        Quiz_ID = quizquestion.Quiz_ID, 
        Course_ID = quizquestion.Course_ID,
        PDF_Name = actual_filename,
        Link_Question = link_question
    )

    db.add(new_quizquestion)
    db.commit()
    db.refresh(new_quizquestion)
    
    logger.info(f"Berhasil membuat record baru: {new_quizquestion.Quiz_ID}")

    return {
        "success": True,
        "message": "New quiz question successfully created",
        "data": {
            "Quiz_ID": new_quizquestion.Quiz_ID,
            "Course_ID": new_quizquestion.Course_ID,
            "PDF_Name": new_quizquestion.PDF_Name,
            "Link_Question": new_quizquestion.Link_Question  # Link akan langsung bisa dibuka
        }
    }