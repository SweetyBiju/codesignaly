"""
Chat router for CodeSignaly.

Handles the POST /chat/stream endpoint that bridges the frontend
to the local Ollama LLM via Server-Sent Events (SSE).
"""

from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession
import httpx
import json

from ..database import get_db
from ..models import Session, Message
from ..prompt_engine import build_context

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3:8b"

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


class ChatRequest(BaseModel):
    """Request body for the chat/stream endpoint."""
    session_id: str
    message: str
    problem_context: Optional[str] = None


async def stream_ollama_response(
    messages: list[dict],
    db: DBSession,
    session_id: str,
    user_message: str,
):
    """
    Streams the Ollama response as Server-Sent Events.

    Sends the full message context to Ollama's /api/chat endpoint,
    streams the response token by token as SSE, and persists both
    the user message and the full assistant response to the database.
    """
    # Save the user message to the database
    db_user_msg = Message(
        session_id=session_id,
        role="user",
        content=user_message,
    )
    db.add(db_user_msg)
    db.commit()

    full_response = ""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": True,
                },
            ) as response:
                if response.status_code != 200:
                    error_msg = f"Ollama returned status {response.status_code}"
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
                    return

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            full_response += token
                            yield f"data: {json.dumps({'token': token})}\n\n"

                        # Check if this is the final chunk
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

    except httpx.ConnectError:
        yield f"data: {json.dumps({'error': 'Cannot connect to Ollama. Is it running on localhost:11434?'})}\n\n"
        return
    except httpx.ReadTimeout:
        yield f"data: {json.dumps({'error': 'Ollama response timed out.'})}\n\n"
        return

    # Save the full assistant response to the database
    if full_response:
        db_assistant_msg = Message(
            session_id=session_id,
            role="assistant",
            content=full_response,
        )
        db.add(db_assistant_msg)
        db.commit()

    # Send a final done event
    yield f"data: {json.dumps({'done': True})}\n\n"


@router.post("/stream")
async def chat_stream(request: ChatRequest, db: DBSession = Depends(get_db)):
    """
    Streams an AI-generated response from Ollama as Server-Sent Events.

    Accepts a JSON body with session_id, message, and optional problem_context.
    Creates a new session if one doesn't exist. Builds the conversation context
    from the database history, sends it to Ollama, and streams the response.
    """
    # Create session if it doesn't exist
    existing_session = db.query(Session).filter(
        Session.session_id == request.session_id
    ).first()

    if not existing_session:
        new_session = Session(
            session_id=request.session_id,
            problem_slug=request.problem_context or "unknown",
        )
        db.add(new_session)
        db.commit()

    # Build the context with conversation history
    messages = build_context(
        db=db,
        session_id=request.session_id,
        user_message=request.message,
        problem_context=request.problem_context,
    )

    return StreamingResponse(
        stream_ollama_response(messages, db, request.session_id, request.message),
        media_type="text/event-stream",
    )


class ClearRequest(BaseModel):
    """Request body for clearing a chat session."""
    session_id: str


@router.post("/clear")
async def clear_chat(request: ClearRequest, db: DBSession = Depends(get_db)):
    """Deletes the session and all its associated messages from the database."""
    session = db.query(Session).filter(Session.session_id == request.session_id).first()
    if not session:
        return {"status": "ok", "message": "Session not found, nothing to clear"}
    
    db.delete(session)
    db.commit()
    return {"status": "ok", "message": "Conversation history cleared"}

