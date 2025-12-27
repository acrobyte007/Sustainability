from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
CURRENT = Path(__file__).resolve()
PROJECT_ROOT = CURRENT.parents[1]
sys.path.append(str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")
api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=1,
)

class Quantity(BaseModel):
    value: Optional[float] = Field(description="Numeric value of the requested quantity, if found")
    unit: Optional[str] = Field( description="Unit exactly as written in the source document")
    page_reference: Optional[str] = Field( description="Page number where the value was found")
    confidence: Optional[float] = Field(description="Confidence score between 0 and 1")


model = llm.with_structured_output(Quantity)

RAG_PROMPT = """
You are an ESG data extraction assistant.
Use ONLY the information in the provided document chunks.
Do NOT infer, calculate, interpolate, or estimate values.
Indicator:
{indicator_name}
Question:
{question}
Allowed units:
{allowed_units}
Extraction rules:
- Extract only explicitly reported values
- Prefer consolidated / group-level disclosures
- Prefer the latest reporting year
- Return only one value
- Preserve the unit exactly as written
- If multiple values exist, choose the most clearly labeled one
- If the value is not found in ANY chunk, return null fields
- Do NOT hallucinate missing values
Output fields:
value, unit, page_reference, confidence
Document Chunks:
{chunk_block}
"""

async def format_chunks_async(chunks: Dict[str, str]) -> str:
    formatted = []
    for page, text in chunks.items():
        formatted.append(f"\n[PAGE {page}]\n{text}\n")
    return "\n".join(formatted)


async def build_prompt_async(indicator_name: str,question: str,units: List[str],chunks: Dict[str, str],):
    chunk_block = await format_chunks_async(chunks)
    return RAG_PROMPT.format(
        indicator_name=indicator_name,
        question=question,
        allowed_units=", ".join(units),
        chunk_block=chunk_block,
    )


async def get_response(indicator_name: str,question: str, units: List[str], chunks: Dict[str, str],):
    prompt = await build_prompt_async(
        indicator_name=indicator_name,
        question=question,
        units=units,
        chunks=chunks,
    )

    response = await model.ainvoke(prompt)
    return response


