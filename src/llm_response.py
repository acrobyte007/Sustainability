from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional, List
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


# ---------- MODELS ----------

mistral_primary = ChatMistralAI(
    model="ministral-8b-latest",
    temperature=0,
    max_retries=1,
)

groq_fallback = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
)


# ---------- STRUCTURED RESPONSE ----------

class Quantity(BaseModel):
    value: Optional[float]
    unit: Optional[str]
    page_reference: Optional[int]
    confidence: Optional[float]
    source_section: Optional[str] = Field(
        description="Section, heading, or table name where the value was found"
    )
    notes: Optional[str] = Field(
        description="Short explanation, extraction reasoning, or disambiguation notes"
    )


mistral_model = mistral_primary.with_structured_output(Quantity)
groq_model = groq_fallback.with_structured_output(Quantity)


# ---------- PROMPTS ----------

SYSTEM_PROMPT = """
Return ONLY a JSON structured Quantity tool output.

Use only the provided chunks.
Do NOT infer or estimate values.

Rules:
- Extract only explicitly reported values
- Prefer latest reporting year
- Prefer consolidated / group values
- Preserve the unit exactly as written
- Return exactly one value

If multiple candidates exist:
- choose the clearest and best-labeled one
- explain selection briefly in `notes`
- fill `source_section` with the closest heading or table title

If not found:
- return null fields
- confidence = 0
- notes = "value not found in provided chunks"
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


# ---------- HELPERS ----------

async def build_prompt(indicator_name: str, question: str, units: List[str], chunks):
    chunk_block = "\n".join(
        f"\n[PAGE {c.get('page', 'Unknown')}]\n{c.get('text', '')}\n"
        for c in chunks
    )
    return USER_PROMPT.format(
        indicator_name=indicator_name,
        question=question,
        allowed_units=", ".join(units),
        chunk_block=chunk_block,
    )


async def run_chain(model, user_prompt: str):
    chain = prompt_template | model
    return await chain.ainvoke({"user_prompt": user_prompt})


# ---------- MAIN FUNCTION WITH FALLBACK ----------

async def get_response(indicator_name: str, question: str, units: List[str], chunks):
    user_prompt = await build_prompt(indicator_name, question, units, chunks)

   
        # Try Mistral first
    response = await run_chain(mistral_model, user_prompt)
    print(indicator_name, "--", response)
    return response
 
       
