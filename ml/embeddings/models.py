from pydantic import BaseModel
from typing import List

class EmbeddingResponse(BaseModel):
    dimension: int
    chunk_count: int
    embeddings_metadata: str  # Summarized metadata for UI/safety
    success: bool
    error: str | None = None
