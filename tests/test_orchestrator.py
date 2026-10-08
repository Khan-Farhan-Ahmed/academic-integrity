import json
from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch, MagicMock
import os

client = TestClient(app)

def fake_get_raw_embeddings_orch(texts):
    embeds = []
    for text in texts:
        embeds.append([1.0, 0.0, 0.0])
    return embeds

class DummyInteraction:
    def __init__(self, output_text):
        self.output_text = output_text

@patch.dict(os.environ, {"SUPABASE_URL": "http://fake-url", "SUPABASE_KEY": "fake-key", "GEMINI_API_KEY": "fake-key"})
@patch("ml.source_analysis.service.get_raw_embeddings", side_effect=fake_get_raw_embeddings_orch)
@patch("ml.paraphrase.service.get_raw_embeddings", side_effect=fake_get_raw_embeddings_orch)
@patch("ml.explanation.service.genai.Client")
@patch("backend.db.repository.create_client")
def test_orchestrator_pipeline_success(mock_supabase, mock_gemini, mock_embed_para, mock_embed_source):
    # Mock Gemini Explanation
    mock_gemini_client = MagicMock()
    mock_gemini.return_value = mock_gemini_client
    mock_gemini_client.interactions.create.return_value = DummyInteraction(
        output_text=json.dumps({
            "executive_summary": "Summary",
            "main_evidence_findings": ["Finding"],
            "why_each_finding_matters": ["Why"],
            "conflicting_weak_evidence": [],
            "limitations": [],
            "recommended_instructor_action": "Review"
        })
    )
    
    # Mock Supabase
    mock_sb_client = MagicMock()
    mock_supabase.return_value = mock_sb_client
    
    # Mock insert/update
    mock_insert_response = MagicMock()
    mock_insert_response.data = [{"id": "db_id"}]
    mock_sb_client.table().insert().execute.return_value = mock_insert_response
    mock_sb_client.table().update().eq().execute.return_value = mock_insert_response
    
    # Mock select for auth validation
    mock_select_response = MagicMock()
    mock_select_response.data = [{"user_id": "inst_1"}]
    mock_sb_client.table().select().eq().execute.return_value = mock_select_response

    # Prepare file upload
    file_content = b"This is a sample document for testing the end-to-end pipeline. It needs to have a few words so the extraction works correctly and doesn't fail the minimum word count check."
    
    files = {
        "file": ("test.txt", file_content, "text/plain")
    }
    data = {
        "student_id": "student123",
        "assignment_name": "Final Essay",
        "reference_sources_json": json.dumps([{"id": "source1", "text": "This is a reference text."}])
    }
    
    headers = {"Authorization": "Bearer mock-instructor-token"}
    response = client.post("/api/analysis/run", files=files, data=data, headers=headers)
    assert response.status_code == 200
    
    res_data = response.json()
    assert res_data["student_id"] == "student123"
    assert "word_count" in res_data["document_statistics"]
    assert res_data["linguistic_features"] is not None
    assert res_data["ai_linguistic_signals"] is not None
    # Fingerprint and others should execute and not be None (or return their respective models)
    
    # We expect exactly one "error" because we pass None for baseline: "Fingerprint info: No baseline provided"
    expected_errors = [e for e in res_data["errors"] if "baseline" not in e.lower()]
    assert len(expected_errors) == 0, f"Unexpected errors: {expected_errors}"
    assert res_data["gemini_explanation"] is not None
    assert res_data["gemini_explanation"] is not None

def test_orchestrator_short_text():
    file_content = b"Too short"
    files = {
        "file": ("test.txt", file_content, "text/plain")
    }
    data = {
        "student_id": "student123",
        "assignment_name": "Final Essay"
    }
    
    headers = {"Authorization": "Bearer mock-instructor-token"}
    response = client.post("/api/analysis/run", files=files, data=data, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data["errors"]) == 1
    assert "too short" in res_data["errors"][0].lower()
