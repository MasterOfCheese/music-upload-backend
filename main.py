from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

app = FastAPI()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.mp3', '.wav')):
        raise HTTPException(status_code=400, detail="Only MP3 or WAV files are allowed")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return JSONResponse(content={"message": f"File {file.filename} uploaded successfully"})

@app.get("/music")
async def get_music_list():
    files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith(('.mp3', '.wav'))]
    return JSONResponse(content={"files": files})