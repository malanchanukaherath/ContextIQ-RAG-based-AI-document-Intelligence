# Quick Start Guide - RAG Application

## Overview
This is a full-stack RAG (Retrieval-Augmented Generation) application with:
- **Backend**: FastAPI + Inngest + Qdrant + Google Gemini
- **Frontend**: React with modern UI

## Prerequisites
- Python 3.12+
- Node.js 16+
- uv (Python package manager)
- Google Gemini API key

## Setup Instructions

### 1. Backend Setup

```bash
# Install dependencies
uv sync

# Create .env file
echo "GOOGLE_GEMINI_API_KEY=your_api_key_here" > .env
echo "GOOGLE_API_KEY=your_api_key_here" >> .env
echo "GOOGLE_GEMINI_MODEL=gemini-1.5-flash" >> .env

# Start the backend server
uv run uvicorn main:app --reload
```

Backend will run on: http://localhost:8000

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the React app
npm start
```

Frontend will run on: http://localhost:3000

### 3. Start Inngest Dev Server (Optional for local testing)

```bash
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest
```

## Usage

1. **Upload Documents**:
   - Open http://localhost:3000
   - Click "Upload Documents" tab
   - Drag & drop or select PDF files
   - Click "Upload & Process"

2. **Ask Questions**:
   - Click "Ask Questions" tab
   - Type your question
   - Get AI-powered answers based on your documents

## Features

### Backend
- PDF ingestion with chunking
- Vector embeddings with Google Gemini
- Qdrant vector database for storage
- AI-powered question answering
- Inngest for workflow orchestration

### Frontend
- Modern, responsive React UI
- Drag & drop file upload
- Real-time chat interface
- Document management sidebar
- Beautiful gradient design
- Example questions for quick start

## API Endpoints

- `POST /api/inngest` - Inngest event endpoint
- Events:
  - `rag/ingest_pdf` - Upload and process PDF
  - `rag/query_pdf_ai` - Query documents with AI

## Troubleshooting

### Backend not starting?
- Check if port 8000 is available
- Verify Google API key in .env file
- Run `uv sync` to install dependencies

### Frontend not loading?
- Check if port 3000 is available
- Verify backend is running on port 8000
- Clear browser cache and restart

### CORS errors?
- Make sure backend has CORS middleware configured
- Check frontend proxy settings in package.json

## Project Structure

```
RAG-Production-App/
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── main.py               # FastAPI backend
├── data_loader.py        # PDF processing
├── vector_db.py          # Qdrant operations
├── custom_types.py       # Type definitions
└── pyproject.toml        # Python dependencies
```

## Next Steps

- Add user authentication
- Implement document deletion
- Add support for more file types
- Deploy to production
- Add persistent storage for uploaded files
