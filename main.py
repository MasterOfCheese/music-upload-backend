from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

app = FastAPI()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://68208ad7f162b6574cac4c87--music-app-np.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Đọc API_KEY từ file .env
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in .env file")

# Hàm kiểm tra API Key
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.mp3', '.wav')):
        raise HTTPException(status_code=400, detail="Only MP3 or WAV files are allowed")
    total_size = sum(os.path.getsize(os.path.join(UPLOAD_DIR, f)) for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f)))
    if total_size > 400 * 1024 * 1024:  # 400 MB threshold
        oldest_file = min(os.listdir(UPLOAD_DIR), key=lambda f: os.path.getctime(os.path.join(UPLOAD_DIR, f)))
        os.remove(os.path.join(UPLOAD_DIR, oldest_file))
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail=f"File {file.filename} already exists")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return JSONResponse(content={"message": f"File {file.filename} uploaded successfully"})

@app.get("/music")
async def get_music_list():
    files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith(('.mp3', '.wav'))]
    return JSONResponse(content={"files": files})

# Endpoint xóa file (chỉ bạn được phép gọi)
@app.delete("/delete/{filename}")
async def delete_file(filename: str, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return JSONResponse(content={"message": f"File {filename} deleted successfully"})
