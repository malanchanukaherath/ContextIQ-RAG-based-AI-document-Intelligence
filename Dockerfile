FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# PDF helpers are included for robustness; drop them if you need a slimmer image.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 poppler-utils fonts-dejavu-core && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir \
    fastapi==0.128.0 \
    google-genai==1.57.0 \
    inngest==0.5.13 \
    llama-index-core==0.14.12 \
    llama-index-readers-file==0.5.6 \
    python-dotenv==1.2.1 \
    python-multipart==0.0.21 \
    qdrant-client==1.16.2 \
    streamlit==1.52.2 \
    uvicorn==0.40.0

# Copy application code
COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
