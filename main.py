from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import StreamingResponse
from pathlib import Path
import shutil
import io

from src.orchestrator import upload_file, extract_indicator
from src.calulation import calculate_esrs_indicators,esrs_to_csv
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
    print(results)
    raw_data= await calculate_esrs_indicators(results)

    csv_bytes =  esrs_to_csv(raw_data)
    csv_stream = io.BytesIO(csv_bytes)
    return StreamingResponse(
        csv_stream,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={doc_id}_indicators.csv"}
    )
