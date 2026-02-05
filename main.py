from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import time

from detector import analyze_message
from agent import generate_agent_reply
from extractor import extract_intelligence
from guvi_callback import send_final_result

app = FastAPI(title="Agentic Honeypot API")

# ---------- MODELS ----------

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class IncomingRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: Optional[List[Message]] = []
    metadata: Optional[Dict] = {}

# ---------- ROUTES ----------

@app.get("/")
def root():
    return {
        "message": "Agentic Honeypot API running",
        "endpoints": ["/health", "/api/message"]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/message")
def handle_message(
    payload: IncomingRequest,
    x_api_key: Optional[str] = Header(None)
):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    detection = analyze_message(payload.message.text)

    reply = None
    intelligence = {}
    total_messages = len(payload.conversationHistory) + 1

    if detection["scam"]:
        reply = generate_agent_reply(
            payload.message.text,
            payload.conversationHistory
        )
        intelligence = extract_intelligence(payload.message.text)

        # ✅ FINAL CALLBACK (MANDATORY)
        if len(payload.conversationHistory) >= 2:
            send_final_result(
                session_id=payload.sessionId,
                scam_detected=True,
                total_messages=total_messages,
                intelligence=intelligence,
                agent_notes="Scammer used urgency and payment redirection tactics"
            )

    return {
        "status": "success",
        "reply": reply
    }
