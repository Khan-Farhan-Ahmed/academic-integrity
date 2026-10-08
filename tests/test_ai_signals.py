from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_ai_signals_human_like():
    text = "This is a completely normal text. It has varied sentence lengths! Some are short. Others might just drag on for a bit longer to introduce natural variation. Isn't that how humans write?"
    response = client.post("/api/analysis/ai-signals", json={"text": text})
    assert response.status_code == 200
    data = response.json()
    assert "ai_linguistic_signal" in data
    assert len(data["signals"]) > 0

def test_ai_signals_highly_uniform():
    text = "The machine wrote this text. The machine wrote that text. The machine typed some text. The machine sent more text."
    response = client.post("/api/analysis/ai-signals", json={"text": text})
    assert response.status_code == 200
    data = response.json()
    # Find sentence uniformity signal
    sig = next((s for s in data["signals"] if s["name"] == "Sentence Uniformity"), None)
    assert sig is not None
    assert sig["score"] > 80.0

def test_ai_signals_repetitive():
    text = "Repeat repeat repeat repeat repeat repeat repeat repeat repeat repeat repeat."
    response = client.post("/api/analysis/ai-signals", json={"text": text})
    assert response.status_code == 200
    data = response.json()
    sig = next((s for s in data["signals"] if s["name"] == "Repetition Indicators"), None)
    assert sig is not None
    assert sig["score"] > 80.0

def test_ai_signals_short_text():
    response = client.post("/api/analysis/ai-signals", json={"text": "Hello world."})
    assert response.status_code == 200
    data = response.json()
    assert data["ai_linguistic_signal"] == 0.0
    assert data["signals"][0]["name"] == "Insufficient Data"

def test_ai_signals_empty():
    response = client.post("/api/analysis/ai-signals", json={"text": "   "})
    assert response.status_code == 200
    data = response.json()
    assert data["ai_linguistic_signal"] == 0.0
    assert data["signals"][0]["name"] == "Insufficient Data"
