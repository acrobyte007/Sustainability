import numpy as np
import asyncio
import spacy
from typing import List, Tuple
from rank_bm25 import BM25Okapi


_english_nlp = None
_nlp_lock = asyncio.Lock()



async def get_spacy_nlp():
    global _english_nlp
    if _english_nlp is None:
        async with _nlp_lock:
            if _english_nlp is None:
                _english_nlp = await asyncio.to_thread(
                    spacy.load, "en_core_web_sm"
                )
    return _english_nlp


async def get_english_lemmas(text: str) -> List[str]:
    if not text:
        return []

    try:
        nlp = await get_spacy_nlp()
        doc = await asyncio.to_thread(nlp, text)
        return [t.lemma_ for t in doc if not t.is_space]
    except Exception:
        return []


async def get_top_chunks_with_bm25(chunk_texts,chunk_ids,distances,query) -> Tuple[List[str], List[str], List[float]]:
    if not chunk_texts:
        return [], [], []
    n = min(len(chunk_texts), len(chunk_ids), len(distances))
    chunk_texts = chunk_texts[:n]
    chunk_ids = chunk_ids[:n]
    distances = distances[:n]

    tokenized_chunks = await asyncio.gather(
        *[get_english_lemmas(text or "") for text in chunk_texts]
    )
    query_tokens = await get_english_lemmas(query or "")

    def _rank(tokenized_chunks, query_tokens):
        if not any(tokenized_chunks):
            similarity_scores = 1 - np.array(distances, dtype=float)
            return chunk_texts, chunk_ids, similarity_scores.tolist()

        bm25 = BM25Okapi(tokenized_chunks)

        bm25_scores = np.array(bm25.get_scores(query_tokens), dtype=float)
        max_score = max(float(bm25_scores.max()), 1e-6)
        bm25_scores = bm25_scores / max_score

        similarity_scores = 1 - np.array(distances, dtype=float)
        hybrid_scores = 0.7 * similarity_scores + 0.3 * bm25_scores

        results = np.array([
            (text, cid, float(score))
            for text, cid, score in zip(chunk_texts, chunk_ids, hybrid_scores)
        ], dtype=object)

        _, unique_indices = np.unique(results[:, 1], return_index=True)
        results = results[sorted(unique_indices)]
        results = results[np.argsort(results[:, 2])[::-1]]
        results = results[:5]

        ranked_chunks = [r[0] for r in results]
        ranked_ids = [r[1] for r in results]
        ranked_scores = [float(r[2]) for r in results]
        print(f"ranked chunks: {ranked_chunks}")
        return ranked_chunks, ranked_ids, ranked_scores

    return await asyncio.to_thread(_rank, tokenized_chunks, query_tokens)
