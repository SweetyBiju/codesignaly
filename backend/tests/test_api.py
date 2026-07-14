from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_stream():
    # Use standard post instead of stream for TestClient since the mock is a simple generator
    response = client.post("/chat/stream")
    assert response.status_code == 200
    
    # Check if we get server-sent events format
    content_type = response.headers.get("content-type")
    assert "text/event-stream" in content_type
    
    # Read the text output and verify it contains our mock data
    text = response.text
    assert "data: Hello!" in text
    assert "data: I am your" in text
    assert "mock AI tutor." in text
