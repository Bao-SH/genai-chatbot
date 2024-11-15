from fastapi import APIRouter, HTTPException, Response, Header
from fastapi.responses import StreamingResponse
from app.config.settings import settings
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_session import ChatSessionManager
from openai import AzureOpenAI

router = APIRouter()
client = AzureOpenAI(api_key=settings.AZURE_OPENAI_API_KEY,
                     api_version=settings.AZURE_OPENAI_API_VERSION,
                     azure_endpoint=settings.AZURE_OPENAI_API_BASE)

# Create a global session manager
session_manager = ChatSessionManager()

async def create_chat_completion(messages: list, stream: bool = False):
    return client.chat.completions.create(
        messages=messages,
        model="gpt-4",
        stream=stream
    )

async def handle_streaming_chat(request: ChatRequest, session_id: str):
    session = session_manager.get_session(session_id)
    session.messages.append({"role": "user", "content": request.message})
    
    stream = await create_chat_completion(session.messages, stream=True)
    
    async def generate():
        collected_content = []
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                collected_content.append(content)
                yield content
        
        full_response = "".join(collected_content)
        session.messages.append({"role": "assistant", "content": full_response})
                
    return StreamingResponse(generate(), media_type='text/event-stream', headers={"X-Session-ID": session_id})

async def handle_regular_chat(request: ChatRequest, session_id: str) -> ChatResponse:
    session = session_manager.get_session(session_id)
    session.messages.append({"role": "user", "content": request.message})
    
    chat_completion = await create_chat_completion(session.messages)
    chat_response = chat_completion.choices[0].message.content.strip(" \n")
    
    # Save the response to session
    session.messages.append({"role": "assistant", "content": chat_response})
    
    return ChatResponse(
        response=chat_response
    )

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, session_id: str = Header(None, alias="X-Session-ID")) -> ChatResponse:
    try:
        # Get or create session based on header
        if session_id:
            try:
                session_manager.get_session(session_id)
            except ValueError:
                session_id = session_manager.create_session()
        else:
            session_id = session_manager.create_session()
        
        if request.enable_streaming:
            return await handle_streaming_chat(request, session_id)
        else:
            response = await handle_regular_chat(request, session_id)
            # Add session_id to response header
            response_with_header = Response(content=response.model_dump_json(), media_type="application/json")
            response_with_header.headers["X-Session-ID"] = session_id
            return response_with_header
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/session/{session_id}")
async def get_session_status(session_id: str):
    try:
        session = session_manager.get_session(session_id)
        return {
            "session_id": session_id,
            "message_count": len(session.messages),
            "created_at": session.created_at
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")
