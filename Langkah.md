#Catatan environment
Proses koneksi Visual Studio Code dengan GitHub:
    Pada terminal Visual Studio Code:
        Tambah Git Bash
            git config --global username "Agnes Yohana"
            git config --global user.email "youremail@mail.com"
                #harus sama dengan email yang terdaftar di GitHub
            ssh-keygen -t ed25519 -C "youremail@mail.com" 
                #SSH key tersimpan di C:\Users \<username>\.ssh\id ed25519.pub
    Pada akun GitHub:
        setting > SSH and GPG keys > New SSH key (ada di ed25519.pub)
    Kembali ke terminal Visual Studio Code:
        ssh -T git@github.com #enter terus
        Ketik yes

Pembuatan Folder:
    mkdir #perintah untuk membuat folder
    -> jika sudah membuat repository di GitHub, tidak perlu buat folder
    -> cukup ketik 
        git clone git@github.com:agnes7209/Kapsel_Analitika_Data-Tugas_1.git
        agar terbentuk folder yang berhubungan dengan repository github

Update file ke GitHub:
    git status #Memberi informasi tentang status git
    lakukan save pada file

    git add . #Menambahkan ke staging area 
        surat masuk ke amplop
    git commit -m "komentar atau catatan yang kita berikan untuk orang lain saat melakukan update"
        amplop masuk ke kotak pos
    git push origin main
        amplop sampai ke tujuan


#Instalasi FastAPI:
    Buat virtual environment (buat di folder Kapsel-Analitika Data).
        python -m venv .venv
    Hanya berlaku jika posisi file python satu level dengan envi

    Aktifkan virtual environment:
        • Windows Bash: source .venv/Scripts/activate
    Cek virtual environment sudah aktif:
        Windows Bash: which python
    Tambahkan file .gitignore di root folder, ketik: 
        .venv/

Bentuk file bahasa python, misal main.py
Jalankan server (development mode): 
    fastapi dev main.py
    Output:
        • Akses server: 
            http://127.0.0.1:8000
        • Akses dokumentasi:
            Swagger UI: http://127.0.0.1:8000/docs
            ReDoc: http://127.0.0.1:8000/redoc
    Terminate Ctrl-C

#Open folder
cd /c/Users/Asus/kapsel-analitika-data/kapsel-andat-UAS/app

pip install -r requirements.txt
python -m app.init_db --email admin@example.com --name "Admin" --password admin123

pip install pandas

source .venv/Scripts/activate
which python
pip install "fastapi[standard]"
pip show fastapi
pip install sqlalchemy pymysql python-dotenv

fastapi dev main.py