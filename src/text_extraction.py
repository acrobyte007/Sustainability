import asyncio
from pathlib import Path
import fitz
import logging

logger = logging.getLogger(__name__)


async def chunk_words(words, size=500, overlap=75):
    step = size - overlap
    chunk_index = 1

    for start in range(0, len(words), step):
        end = start + size
        yield chunk_index, " ".join(words[start:end])
        chunk_index += 1
        await asyncio.sleep(0)


async def extract_text_from_pdf(
    pdf_path: Path,
    chunk_size: int = 500,
    overlap: int = 75
) -> dict[tuple[int, int], str]:

    logger.info(f"Entering extract_text_from_pdf for file: {pdf_path}")

    async def load_pages():
        def read_pdf():
            with fitz.open(pdf_path) as doc:
                return [(i + 1, page.get_text().strip())
                        for i, page in enumerate(doc)]
        return await asyncio.to_thread(read_pdf)

    try:
        pages = await load_pages()
        results: dict[tuple[int, int], str] = {}

        for page_num, text in pages:
            if not text:
                continue

            words = text.split()

            async for chunk_idx, chunk in chunk_words(words, chunk_size, overlap):
                if not chunk.strip():
                    continue

                # keyed by (page_number, chunk_number)
                results[(page_num, chunk_idx)] = chunk

                logger.debug(
                    f"Page {page_num} — chunk {chunk_idx} "
                    f"({len(chunk.split())} words)"
                )

        logger.info(
            f"Successfully extracted chunks from PDF: {pdf_path}, "
            f"total chunks: {len(results)}"
        )

        return results

    except Exception as e:
        logger.error(f"PDF extraction failed for {pdf_path}: {str(e)}")
        return {}

    finally:
        logger.debug(f"Exiting extract_text_from_pdf for file: {pdf_path}")
