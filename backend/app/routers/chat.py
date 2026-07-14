from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

async def mock_streamer():
    chunks = [
        "Hello! ",
        "I am your ",
        "mock AI tutor. ",
        "How can I ",
        "assist you ",
        "with LeetCode ",
        "today?"
    ]
    for chunk in chunks:
        yield f"data: {chunk}\n\n"
        await asyncio.sleep(0.5)

@router.post("/stream")
async def chat_stream():
    """
    Mock endpoint that returns a Server-Sent Events (SSE) stream.
    Used for verifying routing before connecting the actual AI.
    """
    return StreamingResponse(mock_streamer(), media_type="text/event-stream")
