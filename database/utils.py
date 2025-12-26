import numpy as np
import asyncio
import spacy
from typing import List
from rank_bm25 import BM25Okapi

_english_nlp = None
_nlp_lock = asyncio.Lock()


async def get_spacy_nlp():
    global _english_nlp
    if _english_nlp is None:
        async with _nlp_lock:
            if _english_nlp is None:
                _english_nlp = await asyncio.to_thread(spacy.load, "en_core_web_sm")
    return _english_nlp


async def get_english_lemmas(text: str) -> List[str]:
    try:
        nlp = await get_spacy_nlp()
        doc = await asyncio.to_thread(nlp, text)
        return [t.lemma_ for t in doc if not t.is_space]
    except Exception:
        return []


async def get_top_chunks_with_bm25(chunk_texts, chunk_ids, distances, query):
    if not chunk_texts:
        return []

    tokenized_chunks = await asyncio.gather(
        *[get_english_lemmas(text or "") for text in chunk_texts]
    )

    query_tokens = await get_english_lemmas(query)

    def _rank(tokenized_chunks, query_tokens):
        bm25 = BM25Okapi(tokenized_chunks)
        bm25_scores = np.array(bm25.get_scores(query_tokens))
        max_score = bm25_scores.max() + 1e-6
        bm25_scores = bm25_scores / max_score
        similarity_scores = 1 - np.array(distances)
        hybrid_scores = 0.7 * similarity_scores + 0.3 * bm25_scores
        results = np.array([
            (text, chunk_id, score)
            for text, chunk_id, score in zip(chunk_texts, chunk_ids, hybrid_scores)
        ], dtype=object)
        unique_indices = np.unique(results[:, 1], return_index=True)[1]
        unique_results = results[unique_indices]
        top_indices = np.argsort(unique_results[:, 2])[::-1][:9]
        top_results = unique_results[top_indices]
        return [text for text, _, _ in top_results]

    return await asyncio.to_thread(_rank, tokenized_chunks, query_tokens)
