from fastapi import APIRouter
from pydantic import BaseModel
from ml.embeddings.service import generate_embeddings
from ml.embeddings.models import EmbeddingResponse

router = APIRouter()

class EmbeddingRequest(BaseModel):
    text: str

@router.post("/embedding", response_model=EmbeddingResponse)
async def get_embeddings(request: EmbeddingRequest):
    return generate_embeddings(request.text)
