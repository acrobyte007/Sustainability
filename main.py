from fastapi import FastAPI, UploadFile, Form
from pathlib import Path
import shutil

from src.orchestrator import upload_file, extract_indicator
from src.llm_response import get_response

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.post("/upload")
async def upload_pdf(file: UploadFile, user_id: str = Form(...)):
    save_path = UPLOAD_DIR / file.filename

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc_id, _ = await upload_file(save_path, user_id)

    return {
        "status": "upload_complete",
        "doc_id": doc_id
    }


@app.post("/extract")
async def extract_indicators(
    user_id: str = Form(...),
    doc_id: str = Form(...)
):
    results = await extract_indicator(
        user_id=user_id,
        doc_ids=[doc_id],
        get_response=get_response
    )

    return {
        "status": "extraction_complete",
        "results": results
    }
