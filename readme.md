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
- **Database**: PostgreSQL (with vector extension support)
- **Language Model**: Any LLM compatible with your preferred provider
- **Embeddings**: Sentence Transformers / OpenAI / etc.
- **PDF Processing**: (PyMuPDF / pdfplumber / pymupdf expected)
- **Search**: BM25 + Vector similarity hybrid

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/acrobyte007/Sustainability
cd Sustainability

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set PostgreSQL connection string
export CONNECTION_STRING="postgresql://user:password@localhost:5432/esg_db"

# 4. (Optional) Create & initialize database
# python -m database.init_db   # if you have init script

# 5. Run the application
uvicorn main:app --reload


