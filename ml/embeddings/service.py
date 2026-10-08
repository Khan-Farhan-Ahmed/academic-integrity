import os
from google import genai
from google.genai import types
from fastapi import HTTPException
from ml.embeddings.models import EmbeddingResponse

def generate_embeddings(text: str) -> EmbeddingResponse:
    if not text or not text.strip():
        return EmbeddingResponse(
            dimension=0,
            chunk_count=0,
            embeddings_metadata="No text provided",
            success=False,
            error="Empty text"
        )
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return EmbeddingResponse(
            dimension=0,
            chunk_count=0,
            embeddings_metadata="Configuration error",
            success=False,
            error="GEMINI_API_KEY is not set."
        )
        
    client = genai.Client(api_key=api_key)
    
    # Split text into sensible chunks (simple character-based chunking for now)
    # Gemini embedding models can take up to ~8k tokens (which is roughly ~32k chars).
    # We will chunk at 20000 characters to be safe.
    CHUNK_SIZE = 20000
    chunks = [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
    
    try:
        response = client.models.embed_content(
            model="gemini-embedding-2",
            contents=chunks,
            config=types.EmbedContentConfig(output_dimensionality=768)
        )
        
        # response.embeddings is a list of EmbedContentResponse objects or dicts depending on SDK version
        embeds = response.embeddings
        dim = len(embeds[0].values) if embeds and embeds[0].values else 768
        
        return EmbeddingResponse(
            dimension=dim,
            chunk_count=len(chunks),
            embeddings_metadata=f"Successfully generated {len(chunks)} chunk embeddings.",
            success=True,
            error=None
        )
    except Exception as e:
        return EmbeddingResponse(
            dimension=0,
            chunk_count=len(chunks),
            embeddings_metadata="Failed to generate embeddings.",
            success=False,
            error=str(e)
        )

def get_raw_embeddings(chunks: list[str]) -> list[list[float]]:
    if not chunks:
        return []
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")
        
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.embed_content(
            model="gemini-embedding-2",
            contents=chunks,
            config=types.EmbedContentConfig(output_dimensionality=768)
        )
        return [e.values for e in response.embeddings]
    except Exception as e:
        raise ValueError(f"Failed to generate embeddings: {str(e)}")
