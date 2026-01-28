# ESG Indicator Extractor

Automated extraction of **ESG** (Environmental, Social, and Governance) indicators from PDF sustainability reports, annual reports, and other corporate documents.

Using semantic search + modern language models to find, extract and structure ESG metrics efficiently.

Perfect for sustainability analysts, ESG rating agencies, compliance teams, and anyone who needs to process large volumes of ESG reports quickly.

## ✨ Features

- Upload PDF reports → automatic text extraction & chunking
- Semantic + BM25 hybrid search for relevant passages
- LLM-powered structured extraction of ESG indicators
- Pre-defined professional ESG question templates
- Results returned in clean, analysis-ready CSV format
- FastAPI backend with async PostgreSQL support
- Vector embeddings for semantic retrieval

## 🛠 Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Vector Database**:Pinecone
- **Language Model**: Mistral
- **Embeddings**: Sentence Transformers
- **PDF Processing**: PyMuPDF 
- **Search**: BM25 + Vector similarity hybrid

## Workflow
![Alt text](Architecture.png)

## Project Structure
```bash
Sustainability/
├── main.py                     # FastAPI app entry point & route definitions
├── src/
│   ├── orchestrator.py         # Core pipeline: upload → extraction → processing
│   ├── calculation.py          # ESG metric calculations & CSV export logic
│   ├── llm_response.py         # LLM prompt engineering & response parsing
│   ├── embeddings.py           # Text embedding generation utilities
│   ├── text_extraction.py      # PDF parsing, cleaning & chunking logic
│   └── prompts/
│       └── questions.py        # ESG indicators definitions + question templates
├── database/
│   ├── database.py             # Async SQLAlchemy models & CRUD operations
│   ├── utils.py                # Text preprocessing, BM25 ranking helpers
│   └── vector_db.py            # Vector storage & hybrid retrieval logic
├── requirements.txt            # Project dependencies
├── .gitignore                  # Git ignore patterns
└── README.md                   # This file
```
## Setup
``` bash
# 1. Clone the repository
git clone https://github.com/acrobyte007/Sustainability
cd Sustainability

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set PostgreSQL connection string in env file
 CONNECTION_STRING="postgresql://user:password@localhost:5432/esg_db"
 MISTRAL_API_KEY="your_mistral_api_key"
 PINCONE_API_KEY="your_pincere_api_key"

# 4. Create the database tables
python database/database.py
# 4. Run the application
uvicorn main:app --reload










