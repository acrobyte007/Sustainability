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


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
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



async def upsert_document_vectors(namespace: str, document_id: str,
                                  vectors: List[List[float]],
                                  chunks: List[str]) -> Dict[str, Any]:

    vectors_to_upsert = [
        {
            "id": f"{document_id}#chunk{chunk_num}",
            "values": vector,
            "metadata": {
                "document_id": document_id,
                "chunk_text": chunk_text
            }
        }
        for chunk_num, (vector, chunk_text)
        in enumerate(zip(vectors, chunks), 1)
    ]

    index = await get_index()

    try:
        return await asyncio.to_thread(
            index.upsert,
            namespace=namespace,
            vectors=vectors_to_upsert
        )

    except Exception as e:
        logger.error(
            f"Upsert failed for document_id={document_id}, namespace={namespace}: {e}"
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


async def query_vector_index(user_id: str, vector, doc_ids: List[str], query: str):

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
        return [], [], []
    chunk_texts, chunk_ids, distances = [], [], []

    for match in all_matches:
        metadata = getattr(match, "metadata", {}) or {}
        chunk_texts.append(metadata.get("chunk_text", ""))
        chunk_ids.append(getattr(match, "id", ""))
        distances.append(getattr(match, "score", 0.0))
    return await get_top_chunks_with_bm25(
        chunk_texts,
        chunk_ids,
        distances,
        query,
    )

async def delete_chunks(user_id: str, doc_id: str):

    index = await get_index()

    try:
        await asyncio.to_thread(
            index.delete,
            namespace=user_id,
            filter={"document_id": {"$eq": doc_id}}
        )

    except Exception as e:
        logger.error(
            f"Failed to delete chunks for document_id={doc_id}, namespace={user_id}: {e}"
        )
        raise



