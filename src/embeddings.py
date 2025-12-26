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


async def main():
    sentences = [
        "This is an example sentence",
        "Each sentence is converted"
    ]

    vectors = await embed_sentences(sentences)

    print("Number of sentences:", len(vectors))
    print("Embedding dimension:", len(vectors[0]))
    print("First vector sample:", vectors[0][:5])

asyncio.run(main())
