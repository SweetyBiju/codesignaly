from pydantic import BaseModel
from typing import List

class ChatHistoryMessage(BaseModel):
    role: str
    content: str

class ProblemContext(BaseModel):
    title: str
    difficulty: str
    pattern: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatHistoryMessage]
    problem_context: ProblemContext

class ChatResponse(BaseModel):
    reply: str

class SessionStartRequest(BaseModel):
    problem_id: int
    pattern: str

class SessionStartResponse(BaseModel):
    session_id: int
    started_at: str

class SessionEndRequest(BaseModel):
    session_id: int
    hints_used: int
    outcome: str

class SessionEndResponse(BaseModel):
    success: bool
