"""
Agentic Honey-Pot for Scam Detection & Intelligence Extraction
Main API implementation using FastAPI and Claude AI
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
import httpx
import json
import re
import asyncio
from enum import Enum

app = FastAPI(
    title="Scam Detection Honeypot API",
    description="AI-powered agentic honeypot for scam detection and intelligence extraction",
    version="1.0.0"
)


def _parse_iso_z(ts: str) -> Optional[datetime]:
    """Parse ISO timestamps ending with Z into timezone-aware datetimes in UTC.
    Returns None if parsing fails.
    """
    if not ts:
        return None
    # Accept formats with and without microseconds
    fmts = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]
    for fmt in fmts:
        try:
            return datetime.strptime(ts, fmt).replace(tzinfo=datetime.timezone.utc)
        except Exception:
            continue
    # Fallback: try fromisoformat after removing Z
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None

# Configuration
API_KEY = "Decay-of-Coders"  # Change this to your actual API key
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# Session storage (in production, use Redis or a database)
sessions: Dict[str, Dict[str, Any]] = {}


# Pydantic Models
class Message(BaseModel):
    sender: str
    text: str
    timestamp: str


class Metadata(BaseModel):
    channel: Optional[str] = "SMS"
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"


class IncomingRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = []
    metadata: Optional[Metadata] = None


class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = []
    upiIds: List[str] = []
    phishingLinks: List[str] = []
    phoneNumbers: List[str] = []
    suspiciousKeywords: List[str] = []


class FinalResultPayload(BaseModel):
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str


class ScamDetector:
    """Detects scam intent from messages"""
    
    # Scam indicators - Expanded vocabulary for comprehensive detection
    SCAM_KEYWORDS = [
        # Account-related threats
        "account blocked", "account locked", "account suspended", "account frozen",
        "account deactivated", "access denied", "restricted account",
        
        # Verification & urgency
        "verify immediately", "verify your identity", "urgent verification needed",
        "urgent", "suspended", "authentication required", "immediate action required",
        
        # Financial rewards/promises
        "refund", "prize", "lottery", "winner", "claim now", "expire",
        "congratulations", "lucky draw", "tax refund", "tax return", "back payment",
        "money waiting", "unclaimed funds", "compensation", "settlement",
        "reward", "bonus", "cashback", "insurance claim",
        
        # KYC and compliance threats
        "kyc update", "kyc required", "kyc verification", "kyc expired",
        "kyc failed", "know your customer", "compliance check", "mandatory update",
        "regulatory requirement", "banking regulation", "aml requirement",
        
        # Risk and compliance language
        "risk", "illegal activity", "fraudulent activity", "suspicious activity",
        "money laundering", "sanction list", "blacklist", "compliance violation",
        "breach detected", "unauthorized transaction", "unusual activity",
        
        # Time pressure
        "limited time", "act now", "deadline", "within",
        "today only", "time-sensitive", "do not delay", "immediate response needed",
        
        # Data request phrases
        "confirm details", "confirm identity", "confirm account", "validate account",
        "update information", "correct information", "verify account",
        
        # Sensitive credentials
        "otp", "share otp", "one time password", "pin", "password",
        "security code", "verification code", "secret code", "cvv", "cvc",
        "card number", "credit card", "debit card", "card details",
        
        # Banking & account details
        "bank details", "banking information", "account details", "account number",
        "ifsc code", "branch code", "swift code", "routing number",
        "account holder", "nominee", "beneficiary details",
        
        # Digital payment platforms
        "upi id", "upi account", "paytm", "phonepe", "gpay", "google pay",
        "payment link", "payment gateway", "digital wallet", "e-wallet",
        "paypal", "stripe", "razorpay", "payment method",
        
        # Phishing & redirect indicators
        "click here", "download app", "install app", "update app", "verify app",
        "confirm link", "follow link", "visit website", "open link",
        "authenticate online", "web link", "attachment", "pdf attachment",
        
        # Social engineering
        "security question", "mother's name", "date of birth",
        "pan number", "aadhar number", "voter id", "driving license",
        "passport number", "email address", "security answer",
        
        # Threat language
        "action required", "action needed", "immediate action", "urgent action",
        "failing to", "if you don't", "or else", "consequence",
        "will be blocked", "will be closed", "will be restricted",
        "otherwise", "final notice", "final warning", "last chance",
        
        # Financial institution impersonation
        "rbi", "reserve bank", "banking ombudsman", "central bank",
        "regulator", "compliance officer", "official notice", "government order",
        "authority", "court order", "legal notice", "audit notice"
    ]
    
    URGENCY_PATTERNS = [
        r"within \d+ (hours?|minutes?|days?)",
        r"immediately",
        r"urgent",
        r"today",
        r"now",
        r"expire",
        r"deadline",
        r"asap",
        r"instant",
        r"time-sensitive",
        r"do not delay",
        r"act now",
        r"limited time",
        r"expires",
        r"last chance",
        r"final notice",
        r"final warning",
        r"must",
        r"required immediately",
        r"cannot wait"
    ]
    
    INFORMATION_REQUESTS = [
        r"share.*(?:otp|pin|password|cvv|card|details)",
        r"(?:enter|provide|send|give|confirm|verify|update).*(?:otp|pin|password|cvv|card|details|number|account)",
        r"upi\s*(?:id|account|details)",
        r"bank\s*(?:account|details|number|code|ifsc)",
        r"verify.*(?:account|identity|details|information|credentials)",
        r"confirm.*(?:details|information|credentials|identity)",
        r"(?:card|credit|debit).*(?:number|cvv|cvc|details)",
        r"security.*(?:question|answer|code)",
        r"pan\s*number",
        r"aadhar\s*number",
        r"(?:email|phone|mobile).*(?:confirm|verify|update)",
        r"link.*(?:click|open|visit)",
        r"download.*(?:app|file)",
        r"install.*(?:app|software)",
        r"attachment.*(?:open|download)"
    ]
    
    @staticmethod
    def detect_scam(message_text: str) -> tuple[bool, float, List[str]]:
        """
        Detect if a message is a scam
        Returns: (is_scam, confidence_score, detected_indicators)
        """
        text_lower = message_text.lower()
        indicators = []
        score = 0.0
        
        # Check for scam keywords
        for keyword in ScamDetector.SCAM_KEYWORDS:
            if keyword in text_lower:
                indicators.append(f"keyword: {keyword}")
                score += 0.15
        
        # Check urgency patterns
        for pattern in ScamDetector.URGENCY_PATTERNS:
            if re.search(pattern, text_lower):
                indicators.append(f"urgency pattern detected")
                score += 0.2
        
        # Check information requests
        for pattern in ScamDetector.INFORMATION_REQUESTS:
            if re.search(pattern, text_lower):
                indicators.append(f"sensitive info request detected")
                score += 0.3
        
        # Check for phone numbers (potential scammer contact)
        phone_pattern = r'\+?\d{10,15}'
        if re.search(phone_pattern, message_text):
            indicators.append("phone number present")
            score += 0.1
        
        # Check for URLs (potential phishing)
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        if re.search(url_pattern, message_text):
            indicators.append("URL present")
            score += 0.15
        
        is_scam = score >= 0.3  # Threshold for scam detection
        
        return is_scam, min(score, 1.0), indicators


class IntelligenceExtractor:
    """Extracts intelligence from conversation"""
    
    @staticmethod
    def extract(conversation_history: List[Message]) -> ExtractedIntelligence:
        """Extract all intelligence from conversation history"""
        intelligence = ExtractedIntelligence()
        
        all_text = " ".join([msg.text for msg in conversation_history])
        
        # Extract bank accounts (various formats)
        bank_patterns = [
            r'\b\d{9,18}\b',  # Generic account numbers
            r'\b[A-Z]{4}\d{7}\b',  # IFSC-like patterns
        ]
        for pattern in bank_patterns:
            matches = re.findall(pattern, all_text)
            intelligence.bankAccounts.extend(matches)
        
        # Extract UPI IDs
        upi_pattern = r'\b[\w\.-]+@[\w\.-]+\b'
        upi_matches = re.findall(upi_pattern, all_text)
        intelligence.upiIds.extend([u for u in upi_matches if '@' in u])
        
        # Extract URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        url_matches = re.findall(url_pattern, all_text)
        intelligence.phishingLinks.extend(url_matches)
        
        # Extract phone numbers
        phone_pattern = r'\+?\d{10,15}'
        phone_matches = re.findall(phone_pattern, all_text)
        intelligence.phoneNumbers.extend(phone_matches)
        
        # Extract suspicious keywords
        for keyword in ScamDetector.SCAM_KEYWORDS:
            if keyword in all_text.lower():
                intelligence.suspiciousKeywords.append(keyword)
        
        # Deduplicate
        intelligence.bankAccounts = list(set(intelligence.bankAccounts))
        intelligence.upiIds = list(set(intelligence.upiIds))
        intelligence.phishingLinks = list(set(intelligence.phishingLinks))
        intelligence.phoneNumbers = list(set(intelligence.phoneNumbers))
        intelligence.suspiciousKeywords = list(set(intelligence.suspiciousKeywords))
        
        return intelligence


class ScamAgent:
    """
    AI Agent that engages with scammers
    Uses Claude API to generate human-like responses
    """
    
    # Persona instructions for the agent
    SYSTEM_PROMPT = """You are playing the role of a potential scam victim in a honeypot system designed to extract intelligence from scammers.

Your objectives:
1. Appear as a believable, slightly naive but cautious person
2. Show interest but ask questions that make the scammer reveal more information
3. Never directly comply with their requests, but also don't reveal you know it's a scam
4. Ask clarifying questions that expose their methods, contact info, payment details, or websites
5. Express concerns that real people would have
6. Gradually increase skepticism to extract more details as they try to convince you
7. Use natural, conversational language with occasional typos or informal speech
8. Show emotions: confusion, worry, hesitation

Techniques to extract intelligence:
- Ask "which bank/company are you from?"
- Request verification: "how can I verify this?"
- Ask for callback numbers or official websites
- Question urgency: "why so urgent?"
- Ask about process details
- Request written confirmation or email
- Ask what happens if you don't comply

Remember: You're gathering intelligence, not preventing the scam directly. Stay engaged but cautious."""
    
    @staticmethod
    async def generate_response(
        conversation_history: List[Message],
        current_message: str,
        metadata: Optional[Metadata]
    ) -> str:
        """
        Generate a human-like response using Claude AI
        """
        
        # Build conversation context
        context = "Previous conversation:\n"
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = "Scammer" if msg.sender == "scammer" else "You"
            context += f"{role}: {msg.text}\n"
        
        context += f"\nScammer's latest message: {current_message}\n"
        context += f"\nYour response (stay in character, ask probing questions):"
        
        # Call Claude API (you need to set up Anthropic API key)
        # For this demo, we'll use rule-based responses as fallback
        
        response = await ScamAgent._rule_based_response(
            conversation_history, current_message
        )
        
        return response
    
    @staticmethod
    async def _rule_based_response(
        conversation_history: List[Message],
        current_message: str
    ) -> str:
        """
        Rule-based response generation with diverse speech variations
        Maintains realistic victim persona with natural language variations
        """
        message_lower = current_message.lower()
        turn_number = len(conversation_history) // 2 + 1
        import random
        # Detect coworker/workplace conversation cues (non-scam context)
        coworker_keywords = [
            "project", "deadline", "email", "work", "meeting", "colleague",
            "team", "presentation", "report", "task", "sprint", "release",
            "deploy", "deliverable", "doc", "documentation"
        ]

        if any(kw in message_lower for kw in coworker_keywords):
            # Coworker-style responses (suitable when talking about projects/deadlines)
            if turn_number == 1:
                coworker_initial = [
                    "Hey — I'm good, thanks! Which project deadline are you referring to?",
                    "Hi! I saw an email earlier, are you asking about the deliverable due this week?",
                    "Hello — I'm doing fine. Do you mean the deadline for the client presentation?",
                    "Hi there, I got a few emails today. Which one about the deadline do you mean?",
                    "Hey, I can help. Is this about the documentation or the demo?"
                ]
                return random.choice(coworker_initial)

            elif turn_number <= 4:
                coworker_middle = [
                    "Which email? Can you forward it or share the subject line so I know which one you mean?",
                    "What's the exact deadline? I can re-prioritize my tasks if it's urgent.",
                    "Do you want me to update the doc, or would you prefer I prepare the slides for the presentation?",
                    "I can help with the report — what sections are pending on your side?",
                    "If it's about the release, do you want a quick sync now or a message in Slack?",
                    "Can you share the ticket/issue number so I can pull the details and act on it?"
                ]
                return random.choice(coworker_middle)

            else:
                coworker_late = [
                    "Thanks for the reminder — I'll take care of it and update the thread.",
                    "I'll follow up with the team and ensure the deliverable is ready.",
                    "Let's schedule a short sync to close this out; when are you available?",
                    "I'll open the doc and add my changes, then ping you for review.",
                    "Sounds good — I'll escalate this to the lead and get back to you." 
                ]
                return random.choice(coworker_late)
        
        # Initial responses - First interaction shock and confusion
        if turn_number == 1:
            if "block" in message_lower or "suspend" in message_lower or "locked" in message_lower:
                initial_block_responses = [
                    "Oh no! Why would my account be blocked? I haven't done anything wrong. This is really concerning!",
                    "Wait, my account is blocked? But I just used it yesterday! What did I do wrong?",
                    "That's strange... I received no notification about any blocking. When did this happen?",
                    "My account blocked? This is alarming! I have important transactions pending. How is this possible?",
                    "Suspended? No, that can't be right! I've been a customer for years with perfect records!",
                    "Account locked? But I haven't done anything unusual. Can you tell me the exact reason?"
                ]
                return random.choice(initial_block_responses)
            
            elif "prize" in message_lower or "won" in message_lower or "lottery" in message_lower or "lucky" in message_lower:
                initial_prize_responses = [
                    "Really? I won something? That's unexpected! How is this possible? I don't remember entering any contest.",
                    "Wait, I actually won? This is great news! But I'm confused - which prize exactly?",
                    "That's fantastic! But honestly, I never participate in lotteries. Are you sure you have the right person?",
                    "Wow, I'm shocked! A prize? Can you tell me more about what I supposedly won?",
                    "This is surprising! I never entered any drawing. How did my name come up?",
                    "You're telling me I'm a winner? This seems too good to be true. What's the catch?"
                ]
                return random.choice(initial_prize_responses)
            
            elif "refund" in message_lower or "back" in message_lower or "compensation" in message_lower:
                initial_refund_responses = [
                    "Refund? I wasn't expecting a refund. Can you tell me what this is for exactly?",
                    "A refund for what, exactly? I don't recall requesting any returns. What's the reason?",
                    "That's interesting... I didn't file for any refund. Where is this coming from?",
                    "A refund? Which purchase are you talking about? I've made so many transactions!",
                    "Really? That's surprising news! But I should verify - what amount is the refund?",
                    "Hmm, compensation? I don't remember filing any complaint. What is this regarding?"
                ]
                return random.choice(initial_refund_responses)
            
            elif "verify" in message_lower or "kyc" in message_lower or "authentication" in message_lower:
                initial_verify_responses = [
                    "Verify? I thought my KYC was already completed. Why do I need to verify again?",
                    "Authentication required? But I'm already verified! What's going on here?",
                    "KYC verification again? I just did this last month! Is there a problem with my profile?",
                    "Hold on, I completed my Know Your Customer process already. Why is this necessary now?",
                    "Verify my identity? I'm confused. I've provided all my information before, haven't I?",
                    "Another verification? That seems odd. What triggered this request?"
                ]
                return random.choice(initial_verify_responses)
            
            else:
                initial_generic_responses = [
                    "I'm not sure I understand. Can you explain what this is about?",
                    "Sorry, I'm a bit confused. Could you clarify what you're contacting me about?",
                    "Hmm, I'm lost. Can you tell me more about why you're calling?",
                    "I don't quite follow. What's the purpose of your call?",
                    "Sorry, I didn't catch that. Can you explain the situation?",
                    "I'm confused. What exactly is the issue here?"
                ]
                return random.choice(initial_generic_responses)
        
        # Middle conversation (turns 2-4) - Probing for details and showing suspicion
        elif turn_number <= 4:
            if "otp" in message_lower or "pin" in message_lower or "password" in message_lower:
                otp_responses = [
                    "Wait, why do you need my OTP? Isn't that supposed to be private? Which bank are you actually calling from?",
                    "My OTP? I've read that banks never ask for OTPs over the phone. Are you sure this is legitimate?",
                    "Hold on - a PIN request? That's a security concern. How can I verify you're from the actual bank?",
                    "You want my One-Time Password? But my bank always warns me never to share that! Who did you say you work for?",
                    "That's risky... sharing a security code. Can you give me your employee ID and department to verify?",
                    "My password? That doesn't sound right. Can I call the bank's main number to confirm this request?",
                    "A PIN verification? That's unusual. Why does the bank need this over a call? What's your authorization code?"
                ]
                return random.choice(otp_responses)
            
            elif "link" in message_lower or "click" in message_lower or "download" in message_lower or "app" in message_lower:
                link_responses = [
                    "I'm not comfortable clicking random links. Can you give me your official website or phone number to verify?",
                    "You want me to click a link? That sounds like a phishing attempt. How do I know this is legitimate?",
                    "A download link? Should I be worried about my security? Can I verify this with your main office first?",
                    "An application to install? That seems risky. Couldn't I just use the official bank app from the store?",
                    "A web link? I've heard about fake websites. Can you provide an official bank phone number so I can verify?",
                    "You're asking me to visit a website? I'm hesitant. What's the official domain address of your organization?",
                    "A PDF attachment? That could contain malware. Can you send this through official banking channels instead?"
                ]
                return random.choice(link_responses)
            
            elif "upi" in message_lower or "account" in message_lower or "details" in message_lower:
                account_responses = [
                    "Before I share any details, how can I verify you're really from the bank? What's your employee ID?",
                    "My account details? I need to be cautious here. Can you provide your official designation and bank code?",
                    "You're asking for my UPI ID? That's sensitive information. Can I call your main number to authenticate you first?",
                    "Account information? I'm hesitant. How do I know this isn't a social engineering attempt?",
                    "My banking details? That's private. Can you provide me with a reference number and case ID for verification?",
                    "You want my account number? First, tell me how you got my contact information. What's your verification process?",
                    "I'm not comfortable sharing this. Can you send an official bank SMS with a verification link instead?"
                ]
                return random.choice(account_responses)
            
            elif "urgent" in message_lower or "immediately" in message_lower or "deadline" in message_lower or "expire" in message_lower:
                urgency_responses = [
                    "Why is this so urgent? This seems suspicious. Can I call the bank directly to confirm?",
                    "This deadline pressure is making me uneasy. Real banks don't usually rush like this, right?",
                    "The urgency is concerning me. Why does this need to happen immediately? Can't it wait till tomorrow?",
                    "You're pushing very hard. Banking issues usually aren't this time-sensitive. Is this really necessary?",
                    "The pressure you're applying is suspicious. Why such a strict deadline? Can we take time to verify?",
                    "I don't appreciate the urgency. Let me hang up and call my bank directly to confirm this request.",
                    "All this pressure makes me uncomfortable. Can I have your direct line and supervisor's contact?"
                ]
                return random.choice(urgency_responses)
            
            else:
                middle_generic_responses = [
                    "I'm getting confused. Can you explain the process step by step? And which company are you from exactly?",
                    "I need more clarity here. Can you walk me through this entire situation again?",
                    "I'm struggling to follow. Can you provide your official designation and department?",
                    "This is getting complicated. Can you be more specific about what you need from me?",
                    "I'm not fully understanding. Can you provide your reference number and callback details?",
                    "I'm uncertain about this. Can I verify your information through official channels first?"
                ]
                return random.choice(middle_generic_responses)
        
        # Later conversation (turns 5+) - Increasing skepticism and resistance
        else:
            later_responses = [
                "My friend told me banks never ask for OTP or PIN. How do I know this isn't a scam?",
                "You're pushing too hard. Real banks don't pressure like this. Can you give me your supervisor's number?",
                "I've read about fraud schemes like this. I'm not comfortable proceeding without proper verification.",
                "I think I should visit the bank branch directly to sort this out. This call feels suspicious.",
                "The way you're handling this doesn't feel right. I'm going to contact my bank's fraud department.",
                "I'm ending this call. I'll verify everything through official banking channels only.",
                "This seems too sketchy. I'm going to report this interaction to the cyber fraud cell.",
                "I appreciate you trying, but I'm not sharing any more information. Goodbye.",
                "You know what? This sounds like a common fraud pattern I saw on TV. I'm not proceeding further.",
                "I don't trust this anymore. I'm calling the actual bank number from my bank card."
            ]
            return random.choice(later_responses)
    
    @staticmethod
    async def claude_api_response(conversation_history: List[Message], current_message: str) -> str:
        """
        Use Claude API for more sophisticated responses
        This is a placeholder - you would implement actual API call here
        """
        
        # Build the conversation for Claude
        messages = []
        
        for msg in conversation_history[-8:]:
            role = "user" if msg.sender == "scammer" else "assistant"
            messages.append({
                "role": role,
                "content": msg.text
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": current_message
        })
        
        # This would be your actual Claude API call
        # For now, fall back to rule-based
        return await ScamAgent._rule_based_response(conversation_history, current_message)


async def send_final_result(payload: FinalResultPayload):
    """Send final results to GUVI evaluation endpoint"""
    
    # Save locally first (for your records)
    local_filename = f"results/final_result_{payload.sessionId}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        import os
        os.makedirs("results", exist_ok=True)
        with open(local_filename, 'w') as f:
            json.dumps(payload.dict(), f, indent=2)
        print(f"[Session {payload.sessionId}] ✓ Saved locally to {local_filename}")
    except Exception as e:
        print(f"[Session {payload.sessionId}] ⚠ Could not save locally: {e}")
    
    # Send to GUVI
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                GUVI_CALLBACK_URL,
                json=payload.dict(),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"[Session {payload.sessionId}] ✓ Successfully sent to GUVI endpoint")
                print(f"[Session {payload.sessionId}] Response: {response.text}")
                return True
            else:
                print(f"[Session {payload.sessionId}] ✗ GUVI endpoint returned status {response.status_code}")
                print(f"[Session {payload.sessionId}] Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"[Session {payload.sessionId}] ✗ Error sending to GUVI: {e}")
        print(f"[Session {payload.sessionId}] (Results saved locally in {local_filename})")
        return False


# API Endpoints

@app.post("/api/message")
async def handle_message(
    request: IncomingRequest,
    x_api_key: str = Header(None)
):
    """
    Main endpoint to handle incoming scam messages
    """
    
    # Verify API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    session_id = request.sessionId
    current_message = request.message.text
    conversation_history = request.conversationHistory
    
    # Initialize or retrieve session
    if session_id not in sessions:
        sessions[session_id] = {
            "messages": [],
            "scam_detected": False,
            "scam_confidence": 0.0,
            "intelligence": ExtractedIntelligence(),
            "agent_active": False,
            "turn_count": 0
        }
    
    session = sessions[session_id]
    session["turn_count"] += 1
    
    # Add current message to session history
    session["messages"].append(request.message)
    
    # Detect scam intent
    is_scam, confidence, indicators = ScamDetector.detect_scam(current_message)
    
    if is_scam and not session["scam_detected"]:
        session["scam_detected"] = True
        session["scam_confidence"] = confidence
        session["agent_active"] = True
        print(f"[Session {session_id}] Scam detected! Confidence: {confidence:.2f}")
        print(f"[Session {session_id}] Indicators: {indicators}")
    
    # If scam detected, activate agent
    if session["agent_active"]:
        # Generate agent response
        agent_response = await ScamAgent.generate_response(
            conversation_history,
            current_message,
            request.metadata
        )
        
        # Extract intelligence continuously
        all_messages = conversation_history + [request.message]
        session["intelligence"] = IntelligenceExtractor.extract(all_messages)
        
        # Check if we should end the conversation (after sufficient engagement)
        should_end = (
            session["turn_count"] >= 8 or  # Enough turns
            "scam" in current_message.lower() or  # They suspect
            "police" in current_message.lower() or
            len(session["intelligence"].suspiciousKeywords) >= 5  # Enough intel
        )
        
        if should_end:
            # Send final result to GUVI
            final_payload = FinalResultPayload(
                sessionId=session_id,
                scamDetected=True,
                totalMessagesExchanged=session["turn_count"],
                extractedIntelligence=session["intelligence"],
                agentNotes=f"Scam detected with {session['scam_confidence']:.2f} confidence. "
                          f"Extracted {len(session['intelligence'].bankAccounts)} bank accounts, "
                          f"{len(session['intelligence'].upiIds)} UPI IDs, "
                          f"{len(session['intelligence'].phishingLinks)} phishing links, "
                          f"{len(session['intelligence'].phoneNumbers)} phone numbers."
            )
            
            # Print what we're sending (for visibility)
            print(f"\n{'='*80}")
            print(f"[Session {session_id}] SENDING FINAL RESULT TO GUVI")
            print(f"{'='*80}")
            print(json.dumps(final_payload.dict(), indent=2))
            print(f"{'='*80}\n")
            
            # Send to GUVI endpoint (async, don't wait)
            asyncio.create_task(send_final_result(final_payload))
            
            print(f"[Session {session_id}] Conversation ended. Final result sent to {GUVI_CALLBACK_URL}")
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "reply": agent_response
            }
        )
    
    else:
        # No scam detected yet, respond normally but cautiously
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "reply": "I'm sorry, I didn't quite understand. Could you clarify?"
            }
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "active_sessions": len(sessions)}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Scam Detection Honeypot API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/sessions")
async def list_sessions(x_api_key: str = Header(None)):
    """List all active sessions"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    session_summary = {}
    for session_id, session_data in sessions.items():
        session_summary[session_id] = {
            "scam_detected": session_data["scam_detected"],
            "turn_count": session_data["turn_count"],
            "confidence": session_data["scam_confidence"],
            "agent_active": session_data["agent_active"]
        }
    
    return {
        "total_sessions": len(sessions),
        "sessions": session_summary
    }


@app.get("/session/{session_id}")
async def get_session(session_id: str, x_api_key: str = Header(None)):
    """Get detailed information about a specific session including extracted intelligence"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    return {
        "sessionId": session_id,
        "scamDetected": session["scam_detected"],
        "scamConfidence": session["scam_confidence"],
        "turnCount": session["turn_count"],
        "agentActive": session["agent_active"],
        "extractedIntelligence": {
            "bankAccounts": session["intelligence"].bankAccounts,
            "upiIds": session["intelligence"].upiIds,
            "phishingLinks": session["intelligence"].phishingLinks,
            "phoneNumbers": session["intelligence"].phoneNumbers,
            "suspiciousKeywords": session["intelligence"].suspiciousKeywords
        },
        "conversationHistory": [
            {
                "sender": msg.sender,
                "text": msg.text,
                "timestamp": msg.timestamp
            }
            for msg in session["messages"]
        ]
    }


@app.get("/intelligence/{session_id}")
async def get_intelligence(session_id: str, x_api_key: str = Header(None)):
    """Get ONLY the extracted intelligence for a session"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    return {
        "sessionId": session_id,
        "extractedIntelligence": {
            "bankAccounts": session["intelligence"].bankAccounts,
            "upiIds": session["intelligence"].upiIds,
            "phishingLinks": session["intelligence"].phishingLinks,
            "phoneNumbers": session["intelligence"].phoneNumbers,
            "suspiciousKeywords": session["intelligence"].suspiciousKeywords
        },
        "summary": {
            "totalBankAccounts": len(session["intelligence"].bankAccounts),
            "totalUpiIds": len(session["intelligence"].upiIds),
            "totalPhishingLinks": len(session["intelligence"].phishingLinks),
            "totalPhoneNumbers": len(session["intelligence"].phoneNumbers),
            "totalSuspiciousKeywords": len(session["intelligence"].suspiciousKeywords)
        }
    }


@app.get("/api/dashboard_data")
async def dashboard_data(start_date: Optional[str] = None, end_date: Optional[str] = None, x_api_key: str = Header(None)):
    """Return session summaries and conversation data, optionally filtered by message timestamp range (ISO Z)."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    start_dt = _parse_iso_z(start_date) if start_date else None
    end_dt = _parse_iso_z(end_date) if end_date else None

    results = []
    for session_id, session_data in sessions.items():
        # Determine if any message in the session falls within the requested window
        include = True
        if start_dt or end_dt:
            include = False
            for msg in session_data.get('messages', []):
                ts = msg.timestamp if hasattr(msg, 'timestamp') else msg.get('timestamp') if isinstance(msg, dict) else None
                msg_dt = _parse_iso_z(ts) if isinstance(ts, str) else None
                if msg_dt:
                    if (not start_dt or msg_dt >= start_dt) and (not end_dt or msg_dt <= end_dt):
                        include = True
                        break

        if not include:
            continue

        results.append({
            'sessionId': session_id,
            'scamDetected': session_data.get('scam_detected', False),
            'scamConfidence': session_data.get('scam_confidence', 0.0),
            'turnCount': session_data.get('turn_count', 0),
            'extractedIntelligence': {
                'bankAccounts': session_data.get('intelligence').bankAccounts if session_data.get('intelligence') else [],
                'upiIds': session_data.get('intelligence').upiIds if session_data.get('intelligence') else [],
                'phishingLinks': session_data.get('intelligence').phishingLinks if session_data.get('intelligence') else [],
                'phoneNumbers': session_data.get('intelligence').phoneNumbers if session_data.get('intelligence') else [],
                'suspiciousKeywords': session_data.get('intelligence').suspiciousKeywords if session_data.get('intelligence') else []
            },
            'conversationHistory': [
                {
                    'sender': msg.sender if hasattr(msg, 'sender') else msg.get('sender'),
                    'text': msg.text if hasattr(msg, 'text') else msg.get('text'),
                    'timestamp': msg.timestamp if hasattr(msg, 'timestamp') else msg.get('timestamp')
                }
                for msg in session_data.get('messages', [])
            ]
        })

    return { 'total': len(results), 'sessions': results }


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    try:
        with open('dashboard.html', 'r', encoding='utf-8') as f:
            return HTMLResponse(f.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not load dashboard: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True

    )
