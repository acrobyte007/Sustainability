from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import StreamingResponse
from pathlib import Path
import shutil
import io

from src.orchestrator import upload_file, extract_indicator,results_to_csv_bytes
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
    csv_bytes = await results_to_csv_bytes(results)
    csv_stream = io.BytesIO(csv_bytes)
    return StreamingResponse(
        csv_stream,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={doc_id}_indicators.csv"}
    )
