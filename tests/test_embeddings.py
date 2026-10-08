from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch, MagicMock
import os

client = TestClient(app)

class DummyEmbedding:
    def __init__(self):
        self.values = [0.1] * 768

class DummyResponse:
    def __init__(self, chunks_count):
        self.embeddings = [DummyEmbedding() for _ in range(chunks_count)]

@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
@patch("ml.embeddings.service.genai.Client")
def test_embedding_success(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    # We pass a text that would form exactly 1 chunk (under 20000 chars)
    mock_client.models.embed_content.return_value = DummyResponse(chunks_count=1)
    
    response = client.post("/api/analysis/embedding", json={"text": "This is a test document."})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["dimension"] == 768
    assert data["chunk_count"] == 1
    assert data["error"] is None

@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
@patch("ml.embeddings.service.genai.Client")
def test_embedding_long_text(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    # 25000 chars should be 2 chunks (since chunk size is 20000)
    text = "A" * 25000
    mock_client.models.embed_content.return_value = DummyResponse(chunks_count=2)
    
    response = client.post("/api/analysis/embedding", json={"text": text})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["dimension"] == 768
    assert data["chunk_count"] == 2

@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
@patch("ml.embeddings.service.genai.Client")
def test_embedding_api_failure(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.models.embed_content.side_effect = Exception("API rate limit exceeded")
    
    response = client.post("/api/analysis/embedding", json={"text": "This is a test."})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["dimension"] == 0
    assert "rate limit" in data["error"].lower()

@patch.dict(os.environ, {}, clear=True)
def test_embedding_missing_api_key():
    response = client.post("/api/analysis/embedding", json={"text": "This is a test."})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "GEMINI_API_KEY" in data["error"]

def test_embedding_empty_text():
    response = client.post("/api/analysis/embedding", json={"text": "   "})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "Empty text" in data["error"]
    assert data["chunk_count"] == 0
