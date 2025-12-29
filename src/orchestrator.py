import asyncio
from pathlib import Path
from src.text_extraction import extract_text_from_pdf
from src.embeddings import embed_sentences
from database.vector_db import upsert_document_vectors, query_vector_index
from src.prompts.questions import FUNDAMENTAL_RAG_SPEC


async def upload_file(file_path, user_id, progress_queue=None):
    if progress_queue:
        await progress_queue.put("Extracting chunks from PDF...")

    chunks_dict = await extract_text_from_pdf(file_path)

    records = [
        {"page": page, "chunk_index": chunk_idx, "text": text}
        for (page, chunk_idx), text in sorted(chunks_dict.items())
    ]

    if progress_queue:
        await progress_queue.put(f"Embedding {len(records)} chunks...")

    vectors = await embed_sentences([r["text"] for r in records])

    if progress_queue:
        await progress_queue.put("Upserting vectors to database...")

    await upsert_document_vectors(
        namespace=user_id,
        document_id=file_path.name,
        vectors=vectors,
        chunks=records,
    )

    if progress_queue:
        await progress_queue.put("Upload + vectorization complete.")

    return file_path.name, records


async def extract_indicator(user_id, doc_ids, get_response, progress_queue=None):
    results = {}

    async def ask_indicator(indicator_key, spec, chunks):
        async def ask(question):
            return await get_response(
                indicator_name=spec["indicator_name"],
                question=question,
                units=spec["units"],
                chunks=chunks,
            )

        response = await ask(spec["question"])

        if response.value is not None and (response.confidence or 0) >= 0.6:
            return response

        for alt_q in spec.get("alt_questions", []):
            alt_resp = await ask(alt_q)
            if alt_resp.value is not None and (alt_resp.confidence or 0) >= 0.6:
                return alt_resp

        return response

    for indicator_key, spec in FUNDAMENTAL_RAG_SPEC.items():
        if progress_queue:
            await progress_queue.put(f"Extracting {indicator_key}...")

        query_text = spec["question"]
        vector = (await embed_sentences([query_text]))[0]

        chunks = await query_vector_index(
            user_id=user_id,
            vector=vector,
            doc_ids=doc_ids,
            query=query_text,
        )

        if not chunks:
            results[indicator_key] = {
                "indicator_name": spec["indicator_name"],
                "value": None,
                "unit": None,
                "page": None,
                "confidence": 0.0,
                "status": "no_chunks_found",
            }
            continue

        response = await ask_indicator(indicator_key, spec, chunks)

        results[indicator_key] = {
            "indicator_name": spec["indicator_name"],
            "value": response.value,
            "unit": response.unit if response.unit in spec["units"] else None,
            "page": response.page_reference,
            "confidence": response.confidence or 0.0,
            "status": "ok" if response.value else "not_found",
        }

    if progress_queue:
        await progress_queue.put("Indicator extraction complete.")

    return results
