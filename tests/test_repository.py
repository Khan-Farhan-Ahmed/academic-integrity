import pytest
from unittest.mock import patch, MagicMock
from backend.db.repository import DatabaseRepository
import os

@patch.dict(os.environ, {"SUPABASE_URL": "http://fake-url", "SUPABASE_KEY": "fake-key"})
@patch("backend.db.repository.create_client")
def test_save_submission(mock_create_client):
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.data = [{"id": "sub_123", "status": "pending"}]
    mock_client.table().insert().execute.return_value = mock_response
    
    repo = DatabaseRepository()
    result = repo.save_submission("student_1", "Assignment 1")
    
    assert result is not None
    assert result["id"] == "sub_123"
    mock_client.table.assert_called_with("submissions")

@patch.dict(os.environ, {}, clear=True)
def test_repository_no_credentials():
    repo = DatabaseRepository()
    assert repo._is_active() is False
    assert repo.save_submission("s1", "a1") is None
