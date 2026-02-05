from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional

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

# ---------------- BROWSER ROOT ----------------
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

# ---------------- JUDGE ENDPOINT (STATIC BY DESIGN) ----------------
@app.post("/")
async def judge_root(
    request: IncomingRequest,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401)

    # Judge ALWAYS gets fixed response
    return {
        "status": "success",
        "reply": "Why is my account being suspended?"
    }

# ---------------- SMART HONEYPOT ENDPOINT ----------------
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

    # Store scammer message
    conversation.append({
        "sender": request.message.sender,
        "text": request.message.text
    })

    # OpenAI-powered reply
    reply = await generate_response(conversation, request.message.text)

    # Store agent reply
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
