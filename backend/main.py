import os
import json
from typing import List, Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Streaming Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

AVAILABLE_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]


class Message(BaseModel):
    role: Literal["user", "assistant", "system", "tool", "developer"]
    content: str


class ChatRequest(BaseModel):
    messages: List[Message] = Field(
        examples=[[{"role": "user", "content": "Hello!"}]]
    )
    model: str = "gpt-4o"
    # api_key: Optional[str] — removed from request body; key is read from OPENAI_API_KEY in backend/.env


@app.get("/")
async def health():
    return {"status": "ok", "message": "Streaming Chat API is running"}


@app.get("/models")
async def list_models():
    return {"models": AVAILABLE_MODELS}


@app.post("/chat")
async def chat(body: ChatRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="No API key provided. Pass api_key in the body or set OPENAI_API_KEY in .env.",
        )

    if body.model not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Unknown model '{body.model}'")

    if not body.messages:
        raise HTTPException(status_code=400, detail="messages must not be empty")

    client = AsyncOpenAI(api_key=api_key)
    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    async def event_stream():
        try:
            stream = await client.chat.completions.create(
                model=body.model,
                messages=messages,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield f"data: {json.dumps({'content': delta.content})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
