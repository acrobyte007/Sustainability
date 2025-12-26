import os
from typing import List, Dict, Any, Tuple
from pinecone import Pinecone, PineconeException
import asyncio
import time
import logging
from database.utils import get_top_chunks_with_bm25

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

pinecone_api_key = os.getenv("PINECONE_API_KEY")
index_name = "index"

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


async def upsert_document_vectors( namespace: str, document_id: str, vectors: List[List[float]], chunks: List[str]) -> Dict[str, Any]:
    vectors_to_upsert = [
        {
            "id": f"{document_id}#chunk{chunk_num}",
            "values": vector,
            "metadata": {
                "document_id": document_id,
                "chunk_text": chunk_text
            }
        }
        for chunk_num, (vector, chunk_text) in enumerate(zip(vectors, chunks), 1)
    ]

    index = await get_index()
    try:
        response = await asyncio.to_thread(
            index.upsert,
            namespace=namespace,
            vectors=vectors_to_upsert
        )
        return response

    except Exception as e:
        logger.error(
            f"Upsert failed for document_id={document_id}, namespace={namespace}: {e}"
        )
        raise


async def _query_single_doc(index, user_id: str, vector: List[float], doc_id: str):
    try:
        result = await asyncio.to_thread(
            index.query,
            namespace=user_id,
            vector=vector,
            top_k=30,
            filter={"document_id": {"$eq": doc_id}},
            include_metadata=True,
            include_values=False
        )
        return result

    except PineconeException as e:
        logger.error(f"PineconeException for user_id={user_id}, doc_id={doc_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected exception for user_id={user_id}, doc_id={doc_id}: {e}")
        return None


async def query_vector_index( user_id: str, vector: List[float], doc_ids: List[str], query: str) -> Tuple[List[str], List[str], List[float]]:

    if not user_id:
        logger.error("query_vector_index: user_id is empty")
        return [], [], []
    if not doc_ids:
        logger.error("query_vector_index: doc_ids list is empty")
        return [], [], []
    if not vector:
        logger.error("query_vector_index: query vector is empty")
        return [], [], []

    index = await get_index()

    tasks = [
        _query_single_doc(index, user_id, vector, doc_id)
        for doc_id in doc_ids
    ]

    results = await asyncio.gather(*tasks)

    all_matches = []
    for result in results:
        if result and "matches" in result:
            all_matches.extend(result["matches"])

    if not all_matches:
        logger.debug("No matches returned from Pinecone")
        return [], [], []

    chunk_texts = []
    chunk_ids = []
    distances = []

    for match in all_matches:
        metadata = match.get("metadata", {})
        chunk_texts.append(metadata.get("chunk_text", ""))
        chunk_ids.append(match.get("id", ""))
        distances.append(match.get("score", 0.0))

    ranked_chunks, ranked_ids, ranked_scores = get_top_chunks_with_bm25(
        chunk_texts,
        chunk_ids,
        distances,
        query,
    )
    return ranked_chunks, ranked_ids, ranked_scores


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
