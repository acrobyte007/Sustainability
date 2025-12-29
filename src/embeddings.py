import asyncio
from sentence_transformers import SentenceTransformer

# Use the all-MiniLM-L6-v2 model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

async def embed_sentences(sentences):
    embeddings = await asyncio.to_thread(
        model.encode,
        sentences,
        convert_to_numpy=True
    )
    return embeddings.tolist()
