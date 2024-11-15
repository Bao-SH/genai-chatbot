from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    enable_streaming: bool = False
class ChatResponse(BaseModel):
    response: str