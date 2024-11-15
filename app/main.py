# app/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interacting with OpenAI API: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
