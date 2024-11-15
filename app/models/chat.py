from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    enable_streaming: bool = False
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
