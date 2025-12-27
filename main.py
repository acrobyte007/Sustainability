from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import StreamingResponse
import asyncio
from pathlib import Path
import shutil
from src.orchestrator import process_pdf_and_extract
from src.llm_response import get_response

app = FastAPI()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload/")
async def upload_pdf(file: UploadFile, user_id: str = Form(...)):
    save_path = UPLOAD_DIR / file.filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    progress_queue = asyncio.Queue()

    async def streamer():
        task = asyncio.create_task(
            process_pdf_and_extract(save_path, user_id, get_response, progress_queue)
        )
        while True:
            try:
                msg = await asyncio.wait_for(progress_queue.get(), timeout=0.1)
                yield f"data: {msg}\n\n"
            except asyncio.TimeoutError:
                if task.done():
                    break
        esg_result = await task
        yield f"data: Extraction finished!\n\n"
        yield f"data: {esg_result}\n\n"

    return StreamingResponse(streamer(), media_type="text/event-stream")
