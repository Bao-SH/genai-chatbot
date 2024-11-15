from fastapi import APIRouter, HTTPException, Depends
from app.config.settings import settings
from app.models.chat import ChatRequest, ChatResponse
from openai import AzureOpenAI

router = APIRouter()
client = AzureOpenAI(api_key=settings.AZURE_OPENAI_API_KEY,
                     api_version=settings.AZURE_OPENAI_API_VERSION,
                     azure_endpoint=settings.AZURE_OPENAI_API_BASE)


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": request.message,
                }
            ],
            model="gpt-4o",
        )
        chat_response = chat_completion.choices[0].message.content.strip(" \n")
        return {"response": chat_response}
    except openai.error.AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"Authentication Error: {e}")
    except openai.error.APIConnectionError as e:
        raise HTTPException(status_code=502, detail=f"API Connection Error: {e}")
    except openai.error.BadRequestError as e:
        raise HTTPException(status_code=400, detail=f"Bad Request Error: {e}")
    except openai.error.RateLimitError as e:
        raise HTTPException(status_code=429, detail=f"Rate Limit Exceeded: {e}")
    except openai.error.InternalServerError as e:
        raise HTTPException(status_code=503, detail=f"Internal Server Error: {e}")
    except openai.error.Timeout as e:
        raise HTTPException(status_code=504, detail=f"Request Timeout: {e}")
    except openai.error.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
