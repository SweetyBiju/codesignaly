from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_stream():
    """
    Test the chat/stream endpoint with a real request payload.
    Note: This test requires Ollama to be running locally.
    If Ollama is offline, the endpoint should return an SSE error gracefully.
    """
    payload = {
        "session_id": "test-session-001",
        "message": "What is a two-pointer technique?",
        "problem_context": None,
    }
    response = client.post("/chat/stream", json=payload)
    assert response.status_code == 200

    content_type = response.headers.get("content-type")
    assert "text/event-stream" in content_type

    # The response should contain SSE-formatted data lines
    text = response.text
    assert "data:" in text


def test_clear_session():
    """Test that the /clear endpoint successfully deletes a session and cascade-deletes messages."""
    from app.database import SessionLocal
    from app.models import Session, Message

    # Prepare database with a dummy session and message
    db = SessionLocal()
    session_id = "test-clear-session-id"
    db.query(Session).filter(Session.session_id == session_id).delete()
    db.commit()

    dummy_session = Session(session_id=session_id, problem_slug="two-sum")
    db.add(dummy_session)
    db.commit()

    dummy_message = Message(session_id=session_id, role="user", content="hello")
    db.add(dummy_message)
    db.commit()
    db.close()

    # Call /chat/clear endpoint
    payload = {"session_id": session_id}
    response = client.post("/chat/clear", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Conversation history cleared"}

    # Verify that both session and message were deleted
    db = SessionLocal()
    session_in_db = db.query(Session).filter(Session.session_id == session_id).first()
    assert session_in_db is None
    message_in_db = db.query(Message).filter(Message.session_id == session_id).first()
    assert message_in_db is None
    db.close()


def test_chat_clear_endpoint():
    """Test that /chat/clear works for a non-existent session by returning a successful status."""
    payload = {"session_id": "non-existent-session-id"}
    response = client.post("/chat/clear", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Session not found, nothing to clear"}

