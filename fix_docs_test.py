import re

with open('tests/test_documents_api.py', 'r') as f:
    content = f.read()

# Replace client.post("/api/documents/upload", files=files) with headers included
content = content.replace('response = client.post("/api/documents/upload", files=files)', 
    'headers = {"Authorization": "Bearer mock-student-token"}\n    response = client.post("/api/documents/upload", files=files, headers=headers)')

with open('tests/test_documents_api.py', 'w') as f:
    f.write(content)
