from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Academic Integrity API")

# Configure CORS
origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Academic Integrity API is running"}

from backend.api import documents, analysis, ai_signals, embeddings, fingerprint, source_similarity, paraphrase, evidence, explanation, orchestrator
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(ai_signals.router, prefix="/api/analysis", tags=["AI Signals"])
app.include_router(embeddings.router, prefix="/api/analysis", tags=["Embeddings"])
app.include_router(fingerprint.router, prefix="/api/fingerprint", tags=["Fingerprint"])
app.include_router(source_similarity.router, prefix="/api/analysis", tags=["Source Similarity"])
app.include_router(paraphrase.router, prefix="/api/analysis", tags=["Paraphrasing"])
app.include_router(evidence.router, prefix="/api/analysis", tags=["Evidence Engine"])
app.include_router(explanation.router, prefix="/api/analysis", tags=["Explanation"])
app.include_router(orchestrator.router, prefix="/api/analysis", tags=["Orchestrator"])

