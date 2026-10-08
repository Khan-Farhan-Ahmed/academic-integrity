from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch
import numpy as np

client = TestClient(app)

def fake_get_raw_embeddings_paraphrase(texts):
    # Determine semantics based on text content
    embeds = []
    for text in texts:
        if "dog" in text.lower() or "canine" in text.lower():
            # Highly similar semantic space
            embeds.append([1.0, 0.0, 0.0])
        else:
            embeds.append([0.0, 1.0, 0.0])
    return embeds

@patch("ml.paraphrase.service.get_raw_embeddings", side_effect=fake_get_raw_embeddings_paraphrase)
def test_paraphrase_heavily_rewritten(mock_embed):
    # Lexically different, semantically same (both have dog/canine)
    payload = {
        "source_text": "The quick brown dog jumps over the lazy fence.",
        "submitted_text": "A speedy auburn canine leaps across the sluggish barrier."
    }
    
    response = client.post("/api/analysis/paraphrase", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["semantic_similarity"] > 90.0
    assert data["lexical_similarity"] < 40.0
    assert data["paraphrase_signal"] > 40.0
    assert "heavy synonym replacement" in data["evidence_explanation"].lower() or "paraphrasing-like" in data["evidence_explanation"].lower()
    assert len(data["transformation_indicators"]) > 0

@patch("ml.paraphrase.service.get_raw_embeddings", side_effect=fake_get_raw_embeddings_paraphrase)
def test_paraphrase_lightly_rewritten(mock_embed):
    # Lexically very similar
    payload = {
        "source_text": "The quick brown dog jumps over the lazy fence.",
        "submitted_text": "The quick brown dog jumps over the lazy barrier."
    }
    
    response = client.post("/api/analysis/paraphrase", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["semantic_similarity"] > 90.0
    assert data["lexical_similarity"] > 50.0 # High overlap
    assert data["paraphrase_signal"] < 50.0

@patch("ml.paraphrase.service.get_raw_embeddings", side_effect=fake_get_raw_embeddings_paraphrase)
def test_paraphrase_unrelated(mock_embed):
    # One has dog, one doesn't
    payload = {
        "source_text": "The quick brown dog jumps over the lazy fence.",
        "submitted_text": "Space exploration is a fascinating subject of science."
    }
    
    response = client.post("/api/analysis/paraphrase", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["semantic_similarity"] < 10.0
    assert data["paraphrase_signal"] == 0.0

@patch("ml.paraphrase.service.get_raw_embeddings", side_effect=fake_get_raw_embeddings_paraphrase)
def test_paraphrase_missing_source(mock_embed):
    payload = {
        "source_text": "  ",
        "submitted_text": "Space exploration is a fascinating subject of science."
    }
    
    response = client.post("/api/analysis/paraphrase", json=payload)
    assert response.status_code == 400
    assert "Missing source text" in response.json()["detail"]

@patch("ml.paraphrase.service.get_raw_embeddings", side_effect=fake_get_raw_embeddings_paraphrase)
def test_paraphrase_short_text(mock_embed):
    payload = {
        "source_text": "The dog.",
        "submitted_text": "A canine."
    }
    
    response = client.post("/api/analysis/paraphrase", json=payload)
    assert response.status_code == 400
    assert "too short" in response.json()["detail"].lower()
