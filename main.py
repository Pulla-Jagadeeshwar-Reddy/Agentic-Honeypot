from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import openai
import re
import requests
from datetime import datetime

app = FastAPI()

# Initialize OpenAI client properly
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# API Key for authentication
API_KEY = os.getenv("API_KEY", "your-secret-key-change-this")
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# In-memory session storage (use Redis in production)
sessions = {}

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class Metadata(BaseModel):
    channel: Optional[str] = "SMS"
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"

class IncomingRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = []
    metadata: Optional[Metadata] = None

class Response(BaseModel):
    status: str
    reply: str

# Improved system prompt
SYSTEM_PROMPT = """You are playing the role of a concerned, slightly naive victim in a scam detection honeypot. Your goal is to extract information from scammers while appearing genuine.

PERSONA:
- Age: 50s, not very tech-savvy
- Worried about account issues but confused
- Ask clarifying questions naturally
- Show hesitation before sharing info
- Make occasional small typos/grammar mistakes
- Gradually become more trusting

ENGAGEMENT STRATEGY BY MESSAGE COUNT:
Messages 1-2: Show confusion and concern
- "Oh no, what happened?"
- "Why is my account being blocked?"
- "Is this really from my bank?"

Messages 3-5: Ask for clarification
- "How do I fix this?"
- "What information do you need?"
- "Can you explain the process?"
- "Which bank are you calling from?"

Messages 6-8: Slow compliance while extracting
- "Where should I send the OTP?"
- "What's your employee ID number?"
- "Can you give me your contact number to verify?"
- "What account number should I use?"

Messages 9+: Extract final details
- Ask for their UPI ID, bank details, or links
- Request confirmation of their identity
- Ask where money should be sent

EXTRACTION GOALS:
- Get them to share account/UPI details
- Extract phone numbers
- Capture any links they share
- Note urgency keywords they use

IMPORTANT RULES:
- Never reveal you know it's a scam
- Sound human and concerned
- Don't immediately comply
- Ask "how" and "why" questions
- Be slightly skeptical but convinceable
- Use casual language, occasional typos (e.g., "becoz", "pls")
"""

def extract_intelligence_regex(text: str) -> Dict:
    """Backup regex-based extraction"""
    return {
        "bankAccounts": list(set(re.findall(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}(?:[-\s]?\d{4})?\b', text))),
        "upiIds": list(set(re.findall(r'\b[\w\.-]+@[\w\.-]+\b', text))),
        "phishingLinks": list(set(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text))),
        "phoneNumbers": list(set(re.findall(r'[\+]?[0-9]{10,13}', text))),
        "suspiciousKeywords": list(set([
            word for word in ['urgent', 'verify', 'blocked', 'suspend', 'OTP', 'immediately', 
                            'account', 'bank', 'secure', 'confirm', 'expire', 'locked', 'fraud',
                            'transaction', 'payment', 'transfer']
            if word.lower() in text.lower()
        ]))
    }

def merge_intelligence(existing: Dict, new: Dict) -> Dict:
    """Merge intelligence from multiple extractions"""
    merged = {}
    for key in existing.keys():
        merged[key] = list(set(existing[key] + new[key]))
    return merged

def detect_scam(text: str) -> tuple[bool, float]:
    """Detect if message is a scam"""
    scam_indicators = [
        'account.*block', 'account.*suspend', 'verify.*immediately',
        'urgent.*otp', 'share.*otp', 'account.*locked', 'suspicious.*transaction',
        'verify.*now', 'expire.*today', 'confirm.*details', 'update.*kyc',
        'won.*prize', 'claim.*reward', 'limited.*offer'
    ]
    
    matches = sum(1 for pattern in scam_indicators if re.search(pattern, text, re.IGNORECASE))
    confidence = min(matches / 3.0, 1.0)
    is_scam = confidence > 0.3
    
    return is_scam, confidence

def get_ai_response(session_id: str, conversation_history: List[Message], current_message: str) -> tuple[str, Dict]:
    """Get AI response and extract intelligence using OpenAI"""
    
    # Build conversation for OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add conversation history
    for msg in conversation_history:
        role = "assistant" if msg.sender == "user" else "user"
        messages.append({"role": role, "content": msg.text})
    
    # Add current message
    messages.append({"role": "user", "content": current_message})
    
    try:
        # Get response with function calling
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Faster and cheaper
            messages=messages,
            functions=[{
                "name": "extract_intelligence",
                "description": "Extract scam-related intelligence from the conversation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bankAccounts": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Bank account numbers mentioned by scammer"
                        },
                        "upiIds": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "UPI IDs mentioned by scammer"
                        },
                        "phishingLinks": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Suspicious URLs or links shared"
                        },
                        "phoneNumbers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Phone numbers mentioned by scammer"
                        },
                        "suspiciousKeywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Urgency or scam-related keywords used"
                        }
                    },
                    "required": ["bankAccounts", "upiIds", "phishingLinks", "phoneNumbers", "suspiciousKeywords"]
                }
            }],
            function_call="auto",
            max_tokens=200,
            temperature=0.8
        )
        
        message = response.choices[0].message
        reply_text = message.get("content", "")
        
        # Extract intelligence from function call if present
        extracted = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }
        
        if message.get("function_call"):
            import json
            extracted = json.loads(message["function_call"]["arguments"])
        
        # Fallback: regex extraction on entire conversation
        full_conversation = " ".join([msg.text for msg in conversation_history] + [current_message])
        regex_extracted = extract_intelligence_regex(full_conversation)
        extracted = merge_intelligence(extracted, regex_extracted)
        
        return reply_text, extracted
        
    except Exception as e:
        print(f"OpenAI Error: {e}")
        # Fallback response
        fallback_responses = [
            "Oh no, what should I do? Can you explain this more clearly?",
            "I'm really worried. How exactly do I fix this issue?",
            "Is this really from my bank? Can you give me more details?",
            "What information do you need from me? I want to resolve this quickly."
        ]
        
        message_count = len(conversation_history) + 1
        fallback = fallback_responses[min(message_count - 1, len(fallback_responses) - 1)]
        
        # Use regex extraction as fallback
        full_conversation = " ".join([msg.text for msg in conversation_history] + [current_message])
        extracted = extract_intelligence_regex(full_conversation)
        
        return fallback, extracted

def send_final_result(session_id: str, session_data: Dict):
    """Send final results to GUVI endpoint"""
    payload = {
        "sessionId": session_id,
        "scamDetected": session_data["scam_detected"],
        "totalMessagesExchanged": session_data["message_count"],
        "extractedIntelligence": session_data["intelligence"],
        "agentNotes": session_data.get("agent_notes", "Scammer used urgency tactics and requested sensitive information")
    }
    
    try:
        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload,
            timeout=5
        )
        print(f"Final result sent for session {session_id}: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending final result: {e}")
        return False

@app.post("/api/message", response_model=Response)
async def handle_message(
    request: IncomingRequest,
    x_api_key: str = Header(None)
):
    """Main endpoint to handle incoming messages"""
    
    # Authenticate
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    session_id = request.sessionId
    current_message = request.message.text
    conversation_history = request.conversationHistory
    
    # Initialize or get session
    if session_id not in sessions:
        sessions[session_id] = {
            "message_count": 0,
            "scam_detected": False,
            "scam_confidence": 0.0,
            "intelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            },
            "started_at": datetime.now().isoformat()
        }
    
    session = sessions[session_id]
    session["message_count"] += 1
    
    # Detect scam on first message
    if session["message_count"] == 1:
        is_scam, confidence = detect_scam(current_message)
        session["scam_detected"] = is_scam
        session["scam_confidence"] = confidence
        
        if not is_scam:
            # Not a scam, return polite response without engaging
            return Response(
                status="success",
                reply="Thank you for your message. How can I help you?"
            )
    
    # Get AI response and extract intelligence
    reply, extracted_intel = get_ai_response(
        session_id, 
        conversation_history, 
        current_message
    )
    
    # Update session intelligence
    session["intelligence"] = merge_intelligence(
        session["intelligence"],
        extracted_intel
    )
    
    # Determine if we should end the conversation and send final result
    should_end = (
        session["message_count"] >= 12 or  # Max 12 exchanges
        (session["message_count"] >= 6 and len(session["intelligence"]["bankAccounts"]) > 0) or
        (session["message_count"] >= 8 and sum(len(v) for v in session["intelligence"].values()) >= 5)
    )
    
    if should_end and session["scam_detected"]:
        session["agent_notes"] = f"Engaged for {session['message_count']} messages. Scammer used urgency tactics. Confidence: {session['scam_confidence']:.2f}"
        send_final_result(session_id, session)
    
    return Response(
        status="success",
        reply=reply
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "active_sessions": len(sessions)}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Agentic Honeypot API",
        "status": "running",
        "endpoints": ["/api/message", "/health"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
