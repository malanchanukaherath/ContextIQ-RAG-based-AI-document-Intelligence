from google import genai
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
EMBED_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "gemini-embedding-001")
EMBED_DIM = 768

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

def load_and_chunk_pdf(path: str) -> list[str]:
    docs = PDFReader().load_data(file=path)
    texts = [d.text for d in docs if getattr(d, "text", None)]
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks

def embed_texts(texts: list[str]) -> list[list[float]]:
    # Try the configured embedding model first, then known compatible fallbacks.
    candidate_models = list(dict.fromkeys([
        EMBED_MODEL,
        "gemini-embedding-001",
        "text-embedding-004",
        "embedding-001",
    ]))

    embeddings = []
    for text in texts:
        last_error = None
        for model_name in candidate_models:
            try:
                result = client.models.embed_content(
                    model=model_name,
                    contents=text
                )
                embeddings.append(result.embeddings[0].values)
                last_error = None
                break
            except Exception as err:
                last_error = err
        if last_error is not None:
            raise last_error
    return embeddings