from fastapi import APIRouter, HTTPException
from models import SessionStartRequest, SessionStartResponse, SessionEndRequest, SessionEndResponse
from services.session_service import start_session, end_session

router = APIRouter(prefix="/session", tags=["Session"])

@router.post("/start", response_model=SessionStartResponse)
async def start_session_endpoint(request: SessionStartRequest):
    try:
        session_id, started_at = start_session(request.problem_id, request.pattern)
        return SessionStartResponse(session_id=session_id, started_at=started_at)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end", response_model=SessionEndResponse)
async def end_session_endpoint(request: SessionEndRequest):
    try:
        success = end_session(request.session_id, request.hints_used, request.outcome)
        return SessionEndResponse(success=success)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
