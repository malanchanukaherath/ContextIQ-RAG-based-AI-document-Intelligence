# ContextIQ - RAG-Based AI Document Intelligence

ContextIQ is a full-stack RAG (Retrieval-Augmented Generation) application that lets you upload PDF documents, embed their content, store vectors in Qdrant, and ask natural-language questions grounded in your own files.

## Ownership

This project is owned and maintained by Malan Chanuka Herath, Chanith Adikari.

## Features

- Upload and process PDF documents
- Chunk and embed text with Google Gemini embeddings
- Store and search vectors using local Qdrant storage
- Ask questions and get context-based answers from Gemini
- React frontend for document upload, listing, delete, and query workflows
- Inngest event pipeline with automatic local synchronous fallback

## Tech Stack

- Backend: FastAPI, Inngest, Google GenAI SDK, Qdrant Client
- Frontend: React, Axios, Lucide icons
- Document processing: LlamaIndex PDF reader + sentence chunking
- Runtime: Python 3.12+, Node.js 16+

## Project Structure

```text
.
|- main.py                 # FastAPI app and API routes
|- data_loader.py          # PDF load/chunk + embedding logic
|- vector_db.py            # Qdrant collection and vector operations
|- custom_types.py         # Typed models
|- start.bat               # One-click Windows startup
|- start.sh                # One-click Linux/macOS startup
|- frontend/
|  |- src/                 # React source
|  |- public/
|  |- package.json
|- uploads/                # Uploaded PDFs (runtime)
|- qdrant_storage/         # Local vector DB files (runtime)
```

## Prerequisites

- Python 3.12+
- Node.js 16+
- npm
- uv (recommended Python package manager)
- Google Gemini API key

## Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_GEMINI_API_KEY=your_google_api_key
GOOGLE_GEMINI_MODEL=gemini-2.5-flash
GOOGLE_EMBEDDING_MODEL=gemini-embedding-001
```

Notes:

- `GOOGLE_API_KEY` is used for embeddings.
- `GOOGLE_GEMINI_API_KEY` is used for answer generation.
- You can use the same valid Gemini key for both.

## Setup and Run

### Option A: One-click startup

Windows:

```powershell
start.bat
```

Linux/macOS:

```bash
chmod +x start.sh
./start.sh
```

### Option B: Manual startup

1. Install backend dependencies:

```bash
uv sync
```

2. Start backend:

```bash
uv run uvicorn main:app --reload
```

3. Start frontend (new terminal):

```bash
cd frontend
npm install
npm start
```

## Local URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- FastAPI docs: http://localhost:8000/docs

## API Endpoints

- `POST /api/upload`
  - Upload PDF via multipart form (`file`)
- `GET /api/documents`
  - List documents from uploads and vector store
- `DELETE /api/documents/{filename}`
  - Delete file and associated vectors
- `POST /api/query?question=...&top_k=5`
  - Query across embedded document chunks

### Optional Inngest Dev Server

If you want full async event processing locally:

```bash
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest
```

If Inngest is not running, uploads still work through synchronous fallback processing.

## Troubleshooting

### Upload fails with embedding model 404

- Set `GOOGLE_EMBEDDING_MODEL=gemini-embedding-001` in `.env`
- Restart backend after changing env vars

### Vector dimension mismatch errors

- The app now auto-checks embedding dimension and recreates the local Qdrant collection if needed.
- Recreating the collection clears previous vectors in that collection.

### Frontend cannot reach backend

- Ensure backend is running on port 8000
- Confirm frontend `package.json` proxy is `http://localhost:8000`

### CORS errors

- Backend allows `http://localhost:3000` by default
- Ensure frontend is served from that origin in local development

## Security Notes

- Never commit real API keys to GitHub.
- If a key was exposed, rotate it immediately in Google AI Studio.

## License

This project is licensed under the terms in [LICENSE](LICENSE).
