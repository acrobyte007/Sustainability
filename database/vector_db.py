import os
import sys
from pathlib import Path
from dotenv import load_dotenv
CURRENT = Path(__file__).resolve()
PROJECT_ROOT = CURRENT.parents[1]
sys.path.append(str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")
from typing import List, Dict, Any
import asyncio
import logging
from pinecone import Pinecone, PineconeException
import math
import random
from database.utils import get_top_chunks_with_bm25
logger = logging.getLogger(__name__)


pinecone_api_key = os.getenv("PINECONE_API_KEY")
index_name = "index"

if not pinecone_api_key:
    raise RuntimeError("PINECONE_API_KEY not found — check your .env file")

_pc = None
_index = None
_index_lock = asyncio.Lock()

async def get_pinecone_client():
    global _pc
    if _pc is None:
        _pc = Pinecone(api_key=pinecone_api_key)
    return _pc

async def get_index():
    global _index
    async with _index_lock:
        if _index is None:
            pc = await get_pinecone_client()
            index_info = await asyncio.to_thread(pc.describe_index, index_name)
            _index = pc.Index(host=index_info["host"], name=index_name)
    return _index


BATCH_SIZE = 100


async def upsert_document_vectors(namespace: str, document_id: str, vectors: List[List[float]], chunks: List[Dict[str, Any]]):
    vectors_to_upsert = [
        {
            "id": f"{document_id}#p{c['page']}c{c['chunk_index']}",
            "values": vector,
            "metadata": {
                "document_id": document_id,
                "page": c["page"],
                "chunk_index": c["chunk_index"],
                "chunk_text": c["text"],
            },
        }
        for vector, c in zip(vectors, chunks)
    ]

    index = await get_index()
    results = []
    total_batches = math.ceil(len(vectors_to_upsert) / BATCH_SIZE)

    try:
        for batch_num in range(total_batches):
            start = batch_num * BATCH_SIZE
            end = start + BATCH_SIZE
            batch = vectors_to_upsert[start:end]
            result = await asyncio.to_thread(
                index.upsert,
                namespace=namespace,
                vectors=batch
            )
            results.append(result)
        return results

    except Exception as e:
        raise


async def _query_single_doc(index, user_id: str, vector, doc_id: str):
    try:
        return await asyncio.to_thread(
            index.query,
            namespace=user_id,
            vector=vector,
            top_k=5,
            filter={"document_id": {"$eq": doc_id}},
            include_metadata=True,
            include_values=False
        )
    except PineconeException as e:
        return None
    except Exception as e:
        return None


async def query_vector_index(user_id: str, vector, doc_ids: List[str], query: str):
    index = await get_index()
    results = await asyncio.gather(
        *[_query_single_doc(index, user_id, vector, doc_id) for doc_id in doc_ids],
        return_exceptions=True
    )

    all_matches = []

    for r in results:
        if isinstance(r, Exception):
            continue

        if not r:
            continue

        if hasattr(r, "matches"):
            all_matches.extend(r.matches)
        elif isinstance(r, dict) and "matches" in r:
            all_matches.extend(r["matches"])

    candidates = {}

    for match in all_matches or []:
            metadata = getattr(match, "metadata", {}) or {}
            match_id = getattr(match, "id", "").strip()

            candidates[match_id] = {
                "id": match_id,
                "score": getattr(match, "score", 0.0),
                "page": metadata.get("page"),
                "chunk_index": metadata.get("chunk_index"),
                "document_id": metadata.get("document_id"),
                "chunk_text": metadata.get("chunk_text", ""),
            }

    texts = [c["chunk_text"] for c in candidates.values()]
    ids = [c["id"] for c in candidates.values()]
    distances = [c["score"] for c in candidates.values()]

    top_chunks = await get_top_chunks_with_bm25(texts, ids, distances, query)

    if not top_chunks:
        return []

    structured = []

    texts, ids, scores = top_chunks

    for chunk_text, chunk_id_item, score in zip(texts, ids, scores):
        if isinstance(chunk_id_item, list):
            if not chunk_id_item:
                continue
            chunk_id = chunk_id_item[0]
        else:
            chunk_id = chunk_id_item

        chunk_id_clean = chunk_id.strip() if isinstance(chunk_id, str) else str(chunk_id)

        match = candidates.get(chunk_id_clean)
        if not match:
            continue

        structured.append({
            "page": match["page"],
            "chunk_index": match["chunk_index"],
            "text": match["chunk_text"],
            "document_id": match["document_id"],
            "id": match["id"],
            "vector_score": match["score"],
            "bm25_score": score,
        })
    return structured


