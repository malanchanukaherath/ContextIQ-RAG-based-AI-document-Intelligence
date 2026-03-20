import logging
import os
import uuid
import traceback
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import inngest
import inngest.fast_api
from dotenv import load_dotenv
from google import genai
from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage
from custom_types import RAGQueryResult, RAGUpsertResult, RAGChunkAndSrc, RAGSearchResult

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ingest_pdf_to_vector_store(pdf_path: str, source_id: str) -> int:
    """Load, chunk, embed, and upsert a PDF into Qdrant. Returns chunk count."""
    chunks = load_and_chunk_pdf(pdf_path)
    vectors = embed_texts(chunks)
    ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}-{i}")) for i in range(len(chunks))]
    payloads = [{"text": chunks[i], "source": source_id} for i in range(len(chunks))]
    QdrantStorage().upsert(ids, vectors, payloads)
    return len(chunks)

inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logger,
    is_production=False,
    serializer=inngest.PydanticSerializer()
)

@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf"),
)
async def rag_ingest_pdf(ctx: inngest.Context):
    try:
        def _load(ctx: inngest.Context):
            pdf_path = ctx.event.data.get("pdf_path", "")
            source_id = ctx.event.data.get("source_id", pdf_path)
            if not pdf_path:
                raise ValueError("pdf_path is required in event data")
            return {"pdf_path": pdf_path, "source_id": source_id}

        def ingest(data: dict):
            ingested_count = ingest_pdf_to_vector_store(data["pdf_path"], data["source_id"])
            return {"ingested": ingested_count}

        job_input = await ctx.step.run("load-event-data", _load, ctx)
        ingested = await ctx.step.run("ingest-pdf", ingest, job_input)
        return ingested
    except Exception as e:
        logger.error(f"Error in rag_ingest_pdf: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai"),
)
async def rag_query_pdf_ai(ctx: inngest.Context):
    def _search(question:  str, top_k: int = 5) -> RAGSearchResult:
        query_vec = embed_texts([question])[0]
        store = QdrantStorage()
        found = store.search(query_vec, top_k)
        return RAGSearchResult(contexts=found["contexts"], scores=found["scores"])
    
    question = ctx.event.data.get("question")
    top_k = ctx.event.data.get("top_k", 5)

    found = await ctx.step.run("embed-and-search", lambda: _search(question, top_k), output_type=RAGSearchResult)

    context_block = "\n\n".join(f"- {c}" for c in found.contexts)
    user_content = (
        "Use the following context to answer the question:\n\n"
        f"context:\n{context_block}\n\n"
        f"Question: {question}\n\n"
        "Answer consicely using the context above."
    )

    def _generate_answer(user_content: str) -> str:
        client = genai.Client(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
        model_name = os.getenv("GOOGLE_GEMINI_MODEL", "gemini-2.5-flash")
        response = client.models.generate_content(
            model=model_name,
            contents=user_content
        )
        return response.text.strip()

    answer = await ctx.step.run("llm-answer", lambda: _generate_answer(user_content))
    return {"answer": answer, "sources": found.sources, "num_contexts": len(found.contexts)}

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document and trigger ingestion"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save file to uploads directory
        file_path = UPLOADS_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Prefer async processing through Inngest, but fall back to direct ingest locally.
        try:
            await inngest_client.send(
                inngest.Event(
                    name="rag/ingest_pdf",
                    data={
                        "pdf_path": str(file_path),
                        "source_id": file.filename
                    }
                )
            )

            return {
                "message": f"Successfully uploaded {file.filename}",
                "filename": file.filename,
                "path": str(file_path),
                "processing": "queued"
            }
        except Exception as inngest_error:
            logger.warning(
                "Inngest unavailable, processing upload synchronously. Error: %s",
                str(inngest_error)
            )
            ingested = ingest_pdf_to_vector_store(str(file_path), file.filename)
            return {
                "message": f"Successfully uploaded and processed {file.filename}",
                "filename": file.filename,
                "path": str(file_path),
                "processing": "synchronous_fallback",
                "ingested_chunks": ingested
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def list_documents():
    """List all uploaded documents (both in uploads folder and vector DB)"""
    try:
        # Get documents from uploads folder
        upload_files = []
        if UPLOADS_DIR.exists():
            upload_files = [f.name for f in UPLOADS_DIR.iterdir() if f.suffix == '.pdf']
        
        # Get documents from vector database
        store = QdrantStorage()
        db_sources = store.get_all_sources()
        
        # Combine and deduplicate
        all_docs = list(set(upload_files + db_sources))
        
        return {
            "documents": sorted(all_docs),
            "count": len(all_docs)
        }
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document from both uploads folder and vector database"""
    try:
        deleted = {"file": False, "vectors": False}
        errors = []
        
        # Delete from uploads folder
        file_path = UPLOADS_DIR / filename
        if file_path.exists():
            try:
                file_path.unlink()
                deleted["file"] = True
                logger.info(f"Deleted file: {filename}")
            except Exception as e:
                errors.append(f"Failed to delete file: {str(e)}")
        
        # Delete from vector database
        try:
            store = QdrantStorage()
            store.delete_by_source(filename)
            deleted["vectors"] = True
            logger.info(f"Deleted vectors for: {filename}")
        except Exception as e:
            errors.append(f"Failed to delete vectors: {str(e)}")
        
        if errors and not any(deleted.values()):
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to delete document: {'; '.join(errors)}"
            )
        
        return {
            "message": f"Successfully deleted {filename}",
            "filename": filename,
            "deleted": deleted,
            "warnings": errors if errors else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_documents(question: str, top_k: int = 5):
    """Query documents with a question - synchronous response"""
    try:
        # Perform search directly
        query_vec = embed_texts([question])[0]
        store = QdrantStorage()
        found = store.search(query_vec, top_k)
        
        # Generate answer
        context_block = "\n\n".join(f"- {c}" for c in found["contexts"])
        user_content = (
            "Use the following context to answer the question:\n\n"
            f"context:\n{context_block}\n\n"
            f"Question: {question}\n\n"
            "Answer consicely using the context above."
        )
        
        client = genai.Client(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
        model_name = os.getenv("GOOGLE_GEMINI_MODEL", "gemini-2.5-flash")
        response = client.models.generate_content(
            model=model_name,
            contents=user_content
        )
        answer = response.text.strip()
        
        # Extract sources from found results
        sources = list(set([item.get("source", "Unknown") for item in found.get("payloads", [])]))
        
        return {
            "answer": answer,
            "sources": sources,
            "num_contexts": len(found["contexts"])
        }
    except Exception as e:
        logger.error(f"Error querying documents: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

inngest.fast_api.serve(app, inngest_client, functions=[rag_ingest_pdf, rag_query_pdf_ai])