#Tempat untuk buat soal 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from database import get_db
from modules.quiz.models import QuizQuestionsModel
from modules.quiz.schema.schemas import QuizQuestion, ResponseModel

router = APIRouter()

# Konfigurasi GitHub repository
GITHUB_USER = "agnes7209"
GITHUB_REPO = "kapsel-andat-UAS"
GITHUB_BRANCH = "main"
GITHUB_FOLDER = "quiz_questionaries"  # Folder di repo untuk menyimpan PDF

# Base URL untuk file di GitHub (format raw)
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_FOLDER}/"

@router.post("/quizquestions/", response_model=ResponseModel, status_code=201)
def create_quizquestion(
    quizquestion: QuizQuestion = Depends(),
    pdf_file: UploadFile = File(...),
    db: Session = Depends(get_db)):
    
    # Cek apakah Quiz_ID sudah ada
    existing_quiz = db.query(QuizQuestionsModel).filter(QuizQuestionsModel.Quiz_ID == quizquestion.Quiz_ID).first()
    
    if existing_quiz:
        raise HTTPException(
            status_code=400, 
            detail=f"Quiz_ID '{quizquestion.Quiz_ID}' sudah ada"
        )
    
    # Validasi file PDF
    if not pdf_file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Hanya file PDF yang diperbolehkan"
        )
    
    # 1. Simpan file PDF sementara
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_file_path = os.path.join(temp_dir, quizquestion.Link_Question)
    
    try:
        # Simpan file yang diupload
        with open(temp_file_path, "wb") as buffer:
            content = pdf_file.file.read()
            buffer.write(content)
        
        # 2. DISINI PROSES UPLOAD KE GITHUB
        # Untuk contoh ini, kita asumsikan file sudah diupload ke GitHub
        # Di dunia nyata, Anda perlu menggunakan GitHub API atau git command
        
        # Membuat link GitHub dari nama file
        github_pdf_url = GITHUB_RAW_URL + quizquestion.Link_Question
        
        # Contoh link: 
        # https://raw.githubusercontent.com/username/repo/main/pdfs/quiz1.pdf
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menyimpan file: {str(e)}"
        )
    finally:
        # Hapus file temporary
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
 # Simpan ke database dengan link GitHub
    new_question = QuizQuestionsModel(
        Quiz_ID=quizquestion.Quiz_ID,
        Course_ID=quizquestion.Course_ID,
        Link_Question=github_pdf_url  # Sekarang berisi link GitHub
    )

@router.post("/quizquestions/", response_model=ResponseModel, status_code=201)
def create_quizquestion(quizquestion: QuizQuestion, db: Session = Depends(get_db)):
    new_question = QuizQuestionsModel(
        Quiz_ID = quizquestions.Quiz_ID, 
        Course_ID = quizquestions.Course_ID,
        Link_Question = quizquestions.Link_Question
    )
    
    existing_quiz = db.query(QuizQuestionsModel).filter(QuizQuestionsModel.Quiz_ID == quizquestion.Quiz_ID ).first()
    if existing_quiz:
        raise HTTPException(status_code=400, detail=f"Cannot create quiz. Quiz_ID '{quizquestion.Quiz_ID}' already exists in the database.")
    

    db.add(new_quizquestion)
    db.commit()
    db.refresh(new_quizquestion)
    
    return {
        "success": True,
        "message": "New quiz question successfully created",
        "data": {
            "Quiz_ID": new_quizquestion.Quiz_ID,
            "Course_ID": new_quizquestion.Course_ID
        }
    }