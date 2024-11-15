# app/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import AzureOpenAI
from pydantic import BaseModel

app = FastAPI()

load_dotenv()
client = AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                     api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                     azure_endpoint=os.getenv("AZURE_OPENAI_API_BASE"))


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat(request: ChatRequest):
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
    except openai.AuthenticationError as e:
        # Handle Authentication error here, e.g. invalid API key
        print(f"OpenAI API returned an Authentication Error: {e}")

    except openai.APIConnectionError as e:
        # Handle connection error here
        print(f"Failed to connect to OpenAI API: {e}")

    except openai.BadRequestError as e:
        # Handle connection error here
        print(f"Invalid Request Error: {e}")

    except openai.RateLimitError as e:
        # Handle rate limit error
        print(f"OpenAI API request exceeded rate limit: {e}")

    except openai.InternalServerError as e:
        # Handle Service Unavailable error
        print(f"Service Unavailable: {e}")

    except openai.APITimeoutError as e:
        # Handle request timeout
        print(f"Request timed out: {e}")

    except openai.APIError as e:
        # Handle API error here, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")

    except:
        # Handles all other exceptions
        print("An exception has occured.")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
