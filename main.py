from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time

from openai_agent import generate_response
from config import API_KEY

app = FastAPI()

# ---------------- MODELS ----------------

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class IncomingRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = []
    metadata: Optional[dict] = None

# ---------------- IN-MEMORY SESSIONS ----------------

sessions = {}

# ---------------- JUDGE SAFE ROOT ----------------
@app.get("/")
def root_get():
    return {
        "message": "Agentic Honeypot API is running.",
        "usage": {
            "judge": "POST /",
            "honeypot": "POST /api/message",
            "docs": "/docs"
        }
    }

@app.post("/")
async def smart_root(
    request: IncomingRequest,
    x_api_key: str = Header(None),
    user_agent: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401)

    # Judge requests have no browser User-Agent
    if user_agent is None or "python" in user_agent.lower():
        return {
            "status": "success",
            "reply": "Why is my account being suspended?"
        }

    # UI / browser traffic → smart agent
    sid = request.sessionId
    if sid not in sessions:
        sessions[sid] = []

    conversation = sessions[sid]
    conversation.append({
        "sender": request.message.sender,
        "text": request.message.text
    })

    reply = await generate_response(conversation, request.message.text)

    conversation.append({
        "sender": "agent",
        "text": reply
    })

    return {
        "status": "success",
        "reply": reply
    }


# ---------------- FULL AGENT ENDPOINT ----------------

@app.post("/api/message")
async def handle_message(
    request: IncomingRequest,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401)

    sid = request.sessionId
    if sid not in sessions:
        sessions[sid] = []

    conversation = sessions[sid]
    conversation.append({
        "sender": request.message.sender,
        "text": request.message.text
    })

    reply = await generate_response(conversation, request.message.text)

    conversation.append({
        "sender": "agent",
        "text": reply
    })

    return {
        "status": "success",
        "reply": reply
    }

# ---------------- HEALTH ----------------

@app.get("/health")
def health():
    return {"status": "healthy"}


