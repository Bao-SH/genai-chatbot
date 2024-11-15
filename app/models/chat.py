from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    enable_streaming: bool = False

class ChatResponse(BaseModel):
    response: str
