from fastapi.testclient import TestClient
from backend.main import app
import io
import docx

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Academic Integrity API is running"}

def test_upload_txt():
    content = b"Hello world!\nThis is a test document."
    files = {"file": ("test.txt", content, "text/plain")}
    headers = {"Authorization": "Bearer mock-student-token"}
    response = client.post("/api/documents/upload", files=files, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["word_count"] == 7
    assert "Hello world!" in data["extracted_text"]

def test_upload_docx():
    # Create a dummy docx file in memory
    doc = docx.Document()
    doc.add_paragraph("Docx test paragraph.")
    
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    files = {"file": ("test.docx", file_stream, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    headers = {"Authorization": "Bearer mock-student-token"}
    response = client.post("/api/documents/upload", files=files, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.docx"
    assert "Docx test paragraph." in data["extracted_text"]

def test_upload_empty_document():
    files = {"file": ("empty.txt", b"", "text/plain")}
    headers = {"Authorization": "Bearer mock-student-token"}
    response = client.post("/api/documents/upload", files=files, headers=headers)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_upload_invalid_type():
    files = {"file": ("image.png", b"fake image content", "image/png")}
    headers = {"Authorization": "Bearer mock-student-token"}
    response = client.post("/api/documents/upload", files=files, headers=headers)
    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()
