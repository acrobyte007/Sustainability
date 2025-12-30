# ESRS Indicator Extraction API
A FastAPI-based web service for automated extraction of key ESRS (European Sustainability Reporting Standards) indicators from sustainability reports in PDF format.
This tool enables organizations to upload their sustainability reports, process them using Retrieval-Augmented Generation (RAG) with vector embeddings, and receive structured ESRS indicator data in CSV format.
## Features

Organization Onboarding – Register organizations with name and optional country.
PDF Upload – Secure upload of sustainability reports (PDF only).
Automated Indicator Extraction – Uses semantic search over document chunks + LLM validation to extract quantitative and qualitative ESRS indicators.
Confidence Scoring – Only accepts extracted values with sufficient confidence (≥ 0.6).
Fallback Questions – Tries alternative phrasings if initial question fails.
CSV Export – Returns extracted indicators in a downloadable CSV file.

## API Endpoints
### 1. Onboard Organization
textPOST /organizations_onboard
Form Data:

name: string (required) – Organization name
country: string (optional)

Response:
JSON{
  "status": "organization_onboarded",
  "organization_id": "org_12345"
}
## 2. Upload PDF Report
textPOST /upload
Multipart Form Data:

file: PDF file (required)
user_id: string (required) – Identifier for the user/session

Response:
JSON{
  "status": "upload_complete",
  "doc_id": "report_2024.pdf"
}
## 3. Extract ESRS Indicators
textPOST /extract
Form Data:

user_id: string (required)
doc_id: string (required) – Returned from upload
organization_id: string (required) – From onboarding

Response:

Streams a CSV file attachment named <organization_id>_<doc_id>_esrs_indicators.csv
Contains columns for indicator name, value, unit, page reference, confidence, status, source section, and notes.

## Architecture Overview
textPDF Upload
   ↓
Text Extraction & Chunking → Embedding → Vector DB (upsert)
   ↓
For each ESRS indicator:
   → Embed question
   → Retrieve relevant chunks (semantic search)
   → Ask LLM (with context) → Validate confidence & unit
   → Fallback to alternative questions if needed
   ↓
Aggregate results → Calculate/Format → Export to CSV
## Key Components

FastAPI – Async web framework
Vector Database – Stores document embeddings per user (namespaced)
RAG Pipeline – Combines retrieval + LLM generation with confidence thresholding
FUNDAMENTAL_RAG_SPEC – Defines all supported ESRS indicators, their questions, units, and alternatives

## Requirements

Python 3.9+
FastAPI
Uvicorn (for running)
Dependencies for PDF text extraction, embeddings, vector DB, and LLM inference (see project structure)

Local Development

Clone the repository
Install dependencies (typically via requirements.txt or poetry/pyproject.toml)
Start the server:

Bashuvicorn main:app --reload

API will be available at http://localhost:8000
OpenAPI docs: http://localhost:8000/docs

