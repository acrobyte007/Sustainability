import asyncio
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

async def embed_sentences(sentences):
    embeddings = await asyncio.to_thread(
        model.encode,
        sentences,
        convert_to_numpy=True
    )
    return embeddings.tolist()


