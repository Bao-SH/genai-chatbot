from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.config.settings import settings
from app.models.chat import ChatRequest, ChatResponse
from openai import AzureOpenAI

router = APIRouter()
client = AzureOpenAI(api_key=settings.AZURE_OPENAI_API_KEY,
                     api_version=settings.AZURE_OPENAI_API_VERSION,
                     azure_endpoint=settings.AZURE_OPENAI_API_BASE)


async def create_chat_completion(request: ChatRequest, stream: bool = False):
    return client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": request.message,
            }
        ],
        model="gpt-4",
        stream=stream
    )

async def handle_streaming_chat(request: ChatRequest):
    stream = await create_chat_completion(request, stream=True)
    
    async def generate():
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
                
    return StreamingResponse(generate(), media_type='text/event-stream')

async def handle_regular_chat(request: ChatRequest):
    chat_completion = await create_chat_completion(request)
    chat_response = chat_completion.choices[0].message.content.strip(" \n")
    return {"response": chat_response}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        if request.enable_streaming:
            return await handle_streaming_chat(request)
        else:
            return await handle_regular_chat(request)
            
    except AzureOpenAI.error.AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"Authentication Error: {e}")
    except AzureOpenAI.error.APIConnectionError as e:
        raise HTTPException(status_code=502, detail=f"API Connection Error: {e}")
    except AzureOpenAI.error.BadRequestError as e:
        raise HTTPException(status_code=400, detail=f"Bad Request Error: {e}")
    except AzureOpenAI.error.RateLimitError as e:
        raise HTTPException(status_code=429, detail=f"Rate Limit Exceeded: {e}")
    except AzureOpenAI.error.InternalServerError as e:
        raise HTTPException(status_code=503, detail=f"Internal Server Error: {e}")
    except AzureOpenAI.error.Timeout as e:
        raise HTTPException(status_code=504, detail=f"Request Timeout: {e}")
    except AzureOpenAI.error.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
