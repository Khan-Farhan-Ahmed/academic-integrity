from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_feature_extraction_normal_text():
    text = "This is a normal academic sentence. Here is another one, which is slightly longer! And a third sentence."
    response = client.post("/api/analysis/features", json={"text": text})
    assert response.status_code == 200
    data = response.json()
    
    assert data["basic"]["word_count"] > 10
    assert data["basic"]["sentence_count"] == 3
    assert data["basic"]["paragraph_count"] == 1
    
    assert data["punctuation"]["comma_count"] == 1
    assert data["punctuation"]["period_count"] == 2
    assert data["punctuation"]["exclamation_mark_count"] == 1
    
    assert data["sentence"]["sentence_length_min"] > 0
    assert data["sentence"]["sentence_length_max"] > 0

def test_feature_extraction_empty_text():
    response = client.post("/api/analysis/features", json={"text": ""})
    assert response.status_code == 200
    data = response.json()
    
    assert data["basic"]["word_count"] == 0
    assert data["basic"]["character_count"] == 0
    assert data["basic"]["sentence_count"] == 0

def test_feature_extraction_whitespace_only():
    response = client.post("/api/analysis/features", json={"text": "   \\n\\n  \\t "})
    assert response.status_code == 200
    data = response.json()
    
    assert data["basic"]["word_count"] == 0
    assert data["basic"]["sentence_count"] == 0

def test_feature_extraction_short_text():
    response = client.post("/api/analysis/features", json={"text": "Short."})
    assert response.status_code == 200
    data = response.json()
    
    assert data["basic"]["word_count"] == 1
    assert data["basic"]["sentence_count"] == 1
    assert data["punctuation"]["period_count"] == 1
