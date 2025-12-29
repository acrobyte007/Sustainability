from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None
)

class Quantity(BaseModel):
    value: Optional[float] = Field(description="The value of the indicator")
    unit: Optional[str] = Field(description="The unit of the indicator")
    page_reference: Optional[int] = Field(description="Reference to the page where the indicator was found")
    confidence: Optional[float] = Field(description="Confidence of your answer in the range [0, 1]")

model = llm.with_structured_output(Quantity)

SYSTEM_PROMPT = """
You MUST return output only via the Quantity tool in valid JSON format.
Use only the provided chunks. Do not infer or estimate values.
Return one value, preserve the unit exactly, prefer consolidated values and the latest year.
If not found, return null fields and confidence 0.
Do not output text or XML tags. Do not use commas in numbers.
"""
USER_PROMPT = """
Indicator:
{indicator_name}
Question:
{question}
Allowed units:
{allowed_units}
Document Chunks:
{chunk_block}
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "{user_prompt}")
])


async def build_prompt(indicator_name: str, question: str, units: List[str], chunks):
    chunk_block = "\n".join(
        f"\n[PAGE {c.get('page','Unknown')}]\n{c.get('text','')}\n"
        for c in chunks
    )
    return USER_PROMPT.format(
        indicator_name=indicator_name,
        question=question,
        allowed_units=", ".join(units),
        chunk_block=chunk_block,
    )


async def get_response(indicator_name: str, question: str, units: List[str], chunks):
    user_prompt = await build_prompt(indicator_name, question, units, chunks)
    chain = prompt_template | model
    response = await chain.ainvoke({"user_prompt": user_prompt})
    print(f"{indicator_name} -- {response}")
    return response
