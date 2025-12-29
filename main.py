from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import StreamingResponse
import asyncio
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

    progress_queue = asyncio.Queue()

    async def streamer():
        task = asyncio.create_task(
            upload_file(save_path, user_id, progress_queue)
        )

        while True:
            try:
                msg = await asyncio.wait_for(progress_queue.get(), timeout=0.1)
                yield f"data: {msg}\n\n"
            except asyncio.TimeoutError:
                if task.done():
                    break

        doc_id, _ = await task

        yield "data: upload_complete\n\n"
        yield f"data: doc_id:{doc_id}\n\n"

    return StreamingResponse(streamer(), media_type="text/event-stream")



@app.post("/extract")
async def extract_indicators(
    user_id: str = Form(...),
    doc_id: str = Form(...)
):
    progress_queue = asyncio.Queue()

    async def streamer():
        task = asyncio.create_task(
            extract_indicator(
                user_id=user_id,
                doc_ids=[doc_id],
                get_response=get_response,
                progress_queue=progress_queue,
            )
        )

        while True:
            try:
                msg = await asyncio.wait_for(progress_queue.get(), timeout=0.1)
                yield f"data: {msg}\n\n"
            except asyncio.TimeoutError:
                if task.done():
                    break

        results = await task

        yield "data: extraction_complete\n\n"
        yield f"data: {results}\n\n"

    return StreamingResponse(streamer(), media_type="text/event-stream")
