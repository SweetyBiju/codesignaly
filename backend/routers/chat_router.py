from fastapi import APIRouter, HTTPException
from models import ChatRequest, ChatResponse
from services.ai_service import get_chat_response

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        reply = await get_chat_response(request.message, request.history, request.problem_context)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
