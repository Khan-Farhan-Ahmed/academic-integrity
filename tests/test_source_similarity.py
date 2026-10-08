from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch
import numpy as np

client = TestClient(app)

# A fake get_raw_embeddings that returns deterministic vectors based on text content
# We want 'identical' text to have cosine similarity 1.0, and completely different to have 0.0.
# For simplicity, if a chunk contains "plagiarized", we output vector A, else vector B.
def fake_get_raw_embeddings(chunks):
    embeds = []
    for chunk in chunks:
        if "plagiarized" in chunk.lower() or "copied" in chunk.lower():
            embeds.append([1.0, 0.0, 0.0])
        else:
            embeds.append([0.0, 1.0, 0.0])
    return embeds

@patch("ml.source_analysis.service.get_raw_embeddings", side_effect=fake_get_raw_embeddings)
def test_source_similarity_high_match(mock_embed):
    payload = {
        "submission_text": "This is entirely plagiarized content copied from somewhere.",
        "reference_documents": [
            {"id": "doc1", "text": "Some completely original unrelated text."},
            {"id": "doc2", "text": "This is plagiarized content from the original source."}
        ],
        "threshold": 0.85
    }
    
    response = client.post("/api/analysis/source-similarity", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["strong_match_percentage"] == 100.0
    assert len(data["top_matches"]) > 0
    assert data["top_matches"][0]["reference_id"] == "doc2"

@patch("ml.source_analysis.service.get_raw_embeddings", side_effect=fake_get_raw_embeddings)
def test_source_similarity_no_match(mock_embed):
    payload = {
        "submission_text": "This is completely original text written by me.",
        "reference_documents": [
            {"id": "doc1", "text": "This is plagiarized content from the original source."}
        ],
        "threshold": 0.85
    }
    
    response = client.post("/api/analysis/source-similarity", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["strong_match_percentage"] == 0.0
    assert len(data["top_matches"]) == 0

@patch("ml.source_analysis.service.get_raw_embeddings", side_effect=fake_get_raw_embeddings)
def test_source_similarity_empty(mock_embed):
    payload = {
        "submission_text": "   ",
        "reference_documents": [
            {"id": "doc1", "text": "Some text."}
        ],
        "threshold": 0.85
    }
    
    response = client.post("/api/analysis/source-similarity", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["strong_match_percentage"] == 0.0
    assert data["overall_similarity_score"] == 0.0
