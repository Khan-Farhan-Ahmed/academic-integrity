from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_fingerprint_create():
    texts = [
        "This is the first example of the student's writing style. It has some normal punctuation.",
        "Here is a second example. The sentence lengths might vary a bit."
    ]
    response = client.post("/api/fingerprint/create", json={"texts": texts})
    assert response.status_code == 200
    data = response.json()
    assert "avg_sentence_length" in data
    assert data["document_count"] == 2

def test_fingerprint_create_empty():
    response = client.post("/api/fingerprint/create", json={"texts": ["   ", ""]})
    assert response.status_code == 200
    data = response.json()
    assert data["document_count"] == 1
    assert data["avg_sentence_length"] == 0

def test_fingerprint_compare_similar():
    baseline_response = client.post("/api/fingerprint/create", json={"texts": ["This is how I usually write. I use short sentences. It is very simple."]})
    baseline = baseline_response.json()
    
    new_text = "This is another text I wrote. It uses short sentences. It is also simple."
    response = client.post("/api/fingerprint/compare", json={"baseline": baseline, "new_text": new_text})
    assert response.status_code == 200
    data = response.json()
    assert data["style_similarity"] > 70.0  # Should be highly similar
    assert data["error"] is None

def test_fingerprint_compare_different():
    baseline_response = client.post("/api/fingerprint/create", json={"texts": ["This is how I usually write. I use short sentences. It is very simple."]})
    baseline = baseline_response.json()
    
    new_text = "However, in stark contrast to the preceding compositions, this particular manifestation of linguistic expression utilizes significantly expanded vocabulary alongside complex, winding syntactic structures that definitively diverge from previous stylistic norms!"
    response = client.post("/api/fingerprint/compare", json={"baseline": baseline, "new_text": new_text})
    assert response.status_code == 200
    data = response.json()
    assert data["style_similarity"] < 70.0  # Should be much lower
    assert len(data["top_style_changes"]) > 0

def test_fingerprint_compare_short_text():
    baseline_response = client.post("/api/fingerprint/create", json={"texts": ["Normal baseline text goes here."]})
    baseline = baseline_response.json()
    
    response = client.post("/api/fingerprint/compare", json={"baseline": baseline, "new_text": "   "})
    assert response.status_code == 400
    assert "empty or too short" in response.json()["detail"]
