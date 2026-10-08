import re

with open('tests/test_orchestrator.py', 'r') as f:
    content = f.read()

content = content.replace('response = client.post("/api/analysis/run", files=files, data=data)', 'headers = {"Authorization": "Bearer mock-instructor-token"}\n    response = client.post("/api/analysis/run", files=files, data=data, headers=headers)')

with open('tests/test_orchestrator.py', 'w') as f:
    f.write(content)
