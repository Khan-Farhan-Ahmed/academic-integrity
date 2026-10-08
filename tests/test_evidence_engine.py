from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_evidence_engine_mostly_normal():
    payload = {
        "word_count": 300,
        "ai_signals": {
            "signals": [{"name": "Sentence Uniformity", "score": 10.0, "explanation": ""}],
            "ai_linguistic_signal": 15.0
        },
        "fingerprint_comparison": {
            "style_similarity": 90.0,
            "deviation_score": 10.0,
            "per_feature_deviations": [],
            "top_style_changes": []
        }
    }
    response = client.post("/api/analysis/evidence", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "LOW"
    assert data["evidence_strength"] == "LOW"
    assert "Low investigation risk" in data["conclusion"]
    assert len(data["evidence_items"]) == 2

def test_evidence_engine_suspicious_signals():
    payload = {
        "word_count": 500,
        "ai_signals": {
            "signals": [{"name": "Sentence Uniformity", "score": 90.0, "explanation": ""}],
            "ai_linguistic_signal": 85.0
        },
        "source_similarity": {
            "overall_similarity_score": 90.0,
            "strong_match_percentage": 100.0,
            "top_matches": [
                {
                    "submission_chunk": "test",
                    "reference_id": "doc1",
                    "reference_chunk": "test",
                    "similarity_score": 0.95
                }
            ]
        }
    }
    response = client.post("/api/analysis/evidence", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "HIGH"
    assert "High investigation risk" in data["conclusion"]
    assert len(data["evidence_items"]) == 2
    for item in data["evidence_items"]:
        assert item["severity"] == "HIGH"

def test_evidence_engine_conflicting_signals():
    payload = {
        "word_count": 400,
        "ai_signals": {
            "signals": [],
            "ai_linguistic_signal": 5.0
        },
        "fingerprint_comparison": {
            "style_similarity": 10.0,
            "deviation_score": 90.0,
            "per_feature_deviations": [],
            "top_style_changes": []
        }
    }
    response = client.post("/api/analysis/evidence", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Std dev of [5.0, 90.0] is ~42.5 > 40
    assert any("Conflicting signals detected" in w for w in data["safeguard_warnings"])

def test_evidence_engine_insufficient_evidence():
    payload = {
        "word_count": 0
    }
    response = client.post("/api/analysis/evidence", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_risk_score"] == 0.0
    assert len(data["evidence_items"]) == 0
    assert "Insufficient evidence" in data["safeguard_warnings"][0] or "Submission is very short" in data["safeguard_warnings"][0]

def test_evidence_engine_short_submission():
    payload = {
        "word_count": 30,
        "ai_signals": {
            "signals": [],
            "ai_linguistic_signal": 95.0
        }
    }
    response = client.post("/api/analysis/evidence", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert any("very short" in w for w in data["safeguard_warnings"])
    
def test_evidence_engine_style_deviation_only():
    payload = {
        "word_count": 300,
        "fingerprint_comparison": {
            "style_similarity": 20.0,
            "deviation_score": 80.0,
            "per_feature_deviations": [],
            "top_style_changes": []
        }
    }
    response = client.post("/api/analysis/evidence", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["evidence_items"]) == 1
    assert data["evidence_items"][0]["category"] == "Writing style deviation"
    assert data["overall_risk_score"] == 80.0

def test_evidence_engine_source_similarity_only():
    payload = {
        "word_count": 250,
        "source_similarity": {
            "overall_similarity_score": 50.0,
            "strong_match_percentage": 50.0,
            "top_matches": [
                {
                    "submission_chunk": "test",
                    "reference_id": "doc1",
                    "reference_chunk": "test",
                    "similarity_score": 0.85
                }
            ]
        }
    }
    response = client.post("/api/analysis/evidence", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["evidence_items"]) == 1
    assert data["evidence_items"][0]["category"] == "Source similarity"
    assert data["evidence_items"][0]["score"] == 60.0 # 50 + (50 * 0.2)
