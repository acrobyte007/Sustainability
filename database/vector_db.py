import os
import sys
from pathlib import Path
from dotenv import load_dotenv
CURRENT = Path(__file__).resolve()
PROJECT_ROOT = CURRENT.parents[1]
sys.path.append(str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")
from typing import List, Dict, Any, Tuple
from pinecone import Pinecone, PineconeException
import asyncio
import logging
from database.utils import get_top_chunks_with_bm25


import asyncio
import logging
from typing import List, Dict, Any

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
        logger.info("Creating Pinecone client (lazy initialization)")
        _pc = Pinecone(api_key=pinecone_api_key)
        logger.info("Pinecone client initialized")
    return _pc


async def get_index():
    global _index
    async with _index_lock:
        if _index is None:
            logger.info(f"Initializing Pinecone index '{index_name}'")
            pc = await get_pinecone_client()

            index_info = await asyncio.to_thread(pc.describe_index, index_name)
            _index = pc.Index(host=index_info["host"], name=index_name)

            logger.info(f"Connected to index '{index_name}'")
    return _index





async def upsert_document_vectors(namespace: str,document_id: str,vectors: List[List[float]],chunks: List[Dict[str, Any]]):
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

    try:
        result = await asyncio.to_thread(
            index.upsert,
            namespace=namespace,
            vectors=vectors_to_upsert
        )
        logger.debug(
            "Upserted %d vectors for document_id=%s in namespace=%s",
            len(vectors_to_upsert),
            document_id,
            namespace
        )
        return result

    except Exception as e:
        logger.error(
            "Upsert failed for document_id=%s, namespace=%s: %s",
            document_id,
            namespace,
            e
        )
        raise




async def _query_single_doc(index, user_id: str, vector, doc_id: str):
    try:
        return await asyncio.to_thread(
            index.query,
            namespace=user_id,
            vector=vector,
            top_k=50,
            filter={"document_id": {"$eq": doc_id}},
            include_metadata=True,
            include_values=False
        )

    except PineconeException as e:
        logger.error(f"PineconeException for user_id={user_id}, doc_id={doc_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected exception for user_id={user_id}, doc_id={doc_id}: {e}")
        return None


async def query_vector_index( user_id: str,vector,doc_ids: List[str],query: str):
    index = await get_index()
    results = await asyncio.gather(
        *[_query_single_doc(index, user_id, vector, doc_id) for doc_id in doc_ids]
    )

    all_matches = []
    for result in results:
        if not result:
            continue
        if hasattr(result, "matches"):
            all_matches.extend(result.matches)
        elif isinstance(result, dict) and "matches" in result:
            all_matches.extend(result["matches"])

    if not all_matches:
        logger.debug("No matches returned from Pinecone")
        return []

    candidates = {}
    for match in all_matches:
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

    if not candidates:
        logger.debug("No valid candidates found")
        return []
    # ---------- BM25 re-ranking ----------
    texts = [c["chunk_text"] for c in candidates.values()]
    ids = [c["id"] for c in candidates.values()]
    distances = [c["score"] for c in candidates.values()]

    top_chunks = await get_top_chunks_with_bm25(
        texts,
        ids,
        distances,
        query,
    )
    print(f"Top chunks: {top_chunks}")
    if not top_chunks:
        logger.debug("BM25 returned no top chunks")
        return []

    # ---------- convert back to structured chunks ----------
    structured = []

    for item in top_chunks:
        if len(item) < 2:
            continue
        chunk_id = item[1]  # the second element is the ID
        chunk_id_clean = chunk_id.strip()  # now this works
        match = candidates.get(chunk_id_clean)
        if not match:
            logger.debug("Chunk ID %r not found in candidates", chunk_id_clean)
            continue

        structured.append({
            "page": match["page"],
            "chunk_index": match["chunk_index"],
            "text": match["chunk_text"],
            "document_id": match["document_id"],
            "id": match["id"],
            "score": match["score"],
        })


        print("Structured chunks: %s", structured)
    return structured
