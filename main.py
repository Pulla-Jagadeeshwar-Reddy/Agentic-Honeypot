from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import time

from detector import analyze_message
from agent import generate_agent_reply
from extractor import extract_intelligence

app = FastAPI(title="Agentic Honeypot API")

# ---------------- MODELS ----------------

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class IncomingRequest(BaseModel):
    sessionId: str
    message: Message
    conversation: Optional[List[Message]] = []

class HoneypotResponse(BaseModel):
    scamDetected: bool
    confidence: float
    reply: Optional[str]
    intelligence: Dict
    timestamp: int

# ---------------- ROUTES ----------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/message", response_model=HoneypotResponse)
def handle_message(
    payload: IncomingRequest,
    x_api_key: Optional[str] = Header(None)
):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    detection = analyze_message(payload.message.text)

    reply = None
    intelligence = {}

    if detection["scam"]:
        reply = generate_agent_reply(
            payload.message.text,
            payload.conversation
        )
        intelligence = extract_intelligence(payload.message.text)

    return HoneypotResponse(
        scamDetected=detection["scam"],
        confidence=detection["confidence"],
        reply=reply,
        intelligence=intelligence,
        timestamp=int(time.time())
    )
