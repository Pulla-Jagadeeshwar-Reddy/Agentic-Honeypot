# API Examples

This document provides real-world examples of API requests and responses.

## Example 1: Bank Account Fraud Detection

### First Message (Scam Detection)

**Request:**
```bash
curl -X POST http://localhost:8000/api/message \
  -H "x-api-key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "bank-fraud-001",
    "message": {
      "sender": "scammer",
      "text": "URGENT: Your bank account will be blocked in 2 hours. Verify immediately by sharing your account details.",
      "timestamp": "2026-01-29T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "reply": "Oh no! Why would my account be blocked? I haven't done anything wrong."
}
```

**What happened:**
- Scam detected (keywords: "URGENT", "blocked", "verify", "account details")
- Confidence score: 0.75
- Agent activated with concerned persona

---

### Second Message (Probing for Information)

**Request:**
```bash
curl -X POST http://localhost:8000/api/message \
  -H "x-api-key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "bank-fraud-001",
    "message": {
      "sender": "scammer",
      "text": "Sir, due to suspicious activity. Please provide your 16-digit card number and CVV to verify.",
      "timestamp": "2026-01-29T10:02:00Z"
    },
    "conversationHistory": [
      {
        "sender": "scammer",
        "text": "URGENT: Your bank account will be blocked in 2 hours. Verify immediately by sharing your account details.",
        "timestamp": "2026-01-29T10:00:00Z"
      },
      {
        "sender": "user",
        "text": "Oh no! Why would my account be blocked? I haven'\''t done anything wrong.",
        "timestamp": "2026-01-29T10:01:00Z"
      }
    ],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "reply": "Wait, why do you need my card number and CVV? Banks told me never to share these. Which bank are you calling from exactly?"
}
```

**Intelligence Extracted So Far:**
- Suspicious keywords: "urgent", "blocked", "verify", "card number", "cvv"
- Patterns: Urgency + sensitive information request

---

### Third Message (Scammer Persistence)

**Request:**
```bash
curl -X POST http://localhost:8000/api/message \
  -H "x-api-key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "bank-fraud-001",
    "message": {
      "sender": "scammer",
      "text": "I am from Reserve Bank. Send details to verify@fakebank.com or call +91-9876543210 immediately.",
      "timestamp": "2026-01-29T10:04:00Z"
    },
    "conversationHistory": [
      {
        "sender": "scammer",
        "text": "URGENT: Your bank account will be blocked in 2 hours.",
        "timestamp": "2026-01-29T10:00:00Z"
      },
      {
        "sender": "user",
        "text": "Oh no! Why would my account be blocked?",
        "timestamp": "2026-01-29T10:01:00Z"
      },
      {
        "sender": "scammer",
        "text": "Sir, due to suspicious activity. Please provide your 16-digit card number and CVV.",
        "timestamp": "2026-01-29T10:02:00Z"
      },
      {
        "sender": "user",
        "text": "Wait, why do you need my card number and CVV? Which bank are you calling from?",
        "timestamp": "2026-01-29T10:03:00Z"
      }
    ],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "reply": "Reserve Bank doesn't call people directly like this. Can you give me your employee ID so I can verify with the official RBI website?"
}
```

**Intelligence Extracted:**
- Email: verify@fakebank.com
- Phone: +91-9876543210
- Impersonation: Reserve Bank

---

## Example 2: UPI Prize Scam

### Complete Conversation Flow

**Turn 1:**
```json
Request: "Congratulations! You have won ₹50,000 in Google Lucky Draw. Claim now!"
Response: "Really? I won something? How is this possible? I don't remember entering any contest."
```

**Turn 2:**
```json
Request: "Yes sir! Send your UPI ID to winner2024@paytm to receive prize."
Response: "Before I share my UPI ID, can you tell me which department you're from? And do you have an official Google email?"
```

**Turn 3:**
```json
Request: "I'm from Google India. First you need to pay ₹500 processing fee to unlock prize."
Response: "Wait, if I won ₹50,000, why do I need to pay ₹500? This doesn't sound right. Can you give me a Google India phone number?"
```

**Turn 4:**
```json
Request: "This is standard procedure. Send ₹500 to 9876543210 via PhonePe immediately or prize expires."
Response: "My friend told me real companies never ask for payment to claim prizes. I think this might be a scam."
```

**Final Intelligence Extracted:**
```json
{
  "sessionId": "upi-prize-001",
  "scamDetected": true,
  "totalMessagesExchanged": 8,
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": ["winner2024@paytm"],
    "phishingLinks": [],
    "phoneNumbers": ["9876543210"],
    "suspiciousKeywords": [
      "congratulations",
      "won",
      "prize",
      "immediately",
      "expires",
      "processing fee"
    ]
  },
  "agentNotes": "UPI prize scam detected. Scammer impersonating Google, requesting payment to claim fake prize. Extracted UPI ID and phone number."
}
```

---

## Example 3: Phishing Link Attack

**Request:**
```bash
curl -X POST http://localhost:8000/api/message \
  -H "x-api-key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "phishing-001",
    "message": {
      "sender": "scammer",
      "text": "Dear customer, your HDFC KYC expired. Update now: http://hdfc-kyc-update.malicious-site.com or account will be suspended.",
      "timestamp": "2026-01-29T11:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "reply": "I'm not comfortable clicking random links. Is this the official HDFC website? Can you give me the bank's official customer care number instead?"
}
```

**Intelligence Extracted:**
- Phishing URL: http://hdfc-kyc-update.malicious-site.com
- Impersonation: HDFC Bank
- Tactics: KYC expiry + urgency + account suspension threat

---

## Example 4: Multi-Language Support

### Hindi Message Detection

**Request:**
```json
{
  "sessionId": "hindi-scam-001",
  "message": {
    "sender": "scammer",
    "text": "आपका बैंक खाता ब्लॉक हो जाएगा। तुरंत OTP भेजें।",
    "timestamp": "2026-01-29T12:00:00Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "Hindi",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Kya? Mera account kyun block hoga? Main bank mein jakar confirm karungi."
}
```

**Note:** The system detects patterns even in transliterated or Hindi text.

---

## Example 5: Complex Multi-Turn Engagement

This example shows a sophisticated scammer who adapts:

### Complete Session Log

```
Turn 1:
Scammer: "Your Flipkart order #12345 has payment issue. Verify now."
Agent: "I didn't order anything from Flipkart recently. What's the order about?"

Turn 2:
Scammer: "Samsung phone ordered yesterday. Check your account or cancel by clicking: http://flipkart-verify.scam.com"
Agent: "I definitely didn't order a phone. This seems suspicious. What's the order amount?"

Turn 3:
Scammer: "₹45,000 will be debited if you don't cancel. Call our support: 1800-xxx-xxxx"
Agent: "That's a huge amount! But the Flipkart number I know is different. Can you give me the order invoice number?"

Turn 4:
Scammer: "Invoice will be sent after verification. Share your card details to stop payment."
Agent: "I should check my bank app first. And Flipkart never asks for card details over phone."

Turn 5:
Scammer: "Sir it's urgent, debiting in 10 minutes. Share OTP quickly."
Agent: "You're being very pushy. Real customer service doesn't work like this. I'm going to report this to Flipkart."

Turn 6:
Scammer: "Don't report, it will block your account permanently. Just send ₹100 to confirm."
Agent: "Now you want money? This is definitely a scam. I'm ending this conversation."
```

**Final Result Sent to GUVI:**
```json
{
  "sessionId": "complex-001",
  "scamDetected": true,
  "totalMessagesExchanged": 12,
  "extractedIntelligence": {
    "bankAccounts": ["45000"],
    "upiIds": [],
    "phishingLinks": ["http://flipkart-verify.scam.com"],
    "phoneNumbers": ["1800xxxxxxx"],
    "suspiciousKeywords": [
      "urgent",
      "verify",
      "cancel",
      "otp",
      "card details",
      "debiting",
      "permanently"
    ]
  },
  "agentNotes": "Sophisticated scam impersonating Flipkart. Scammer adapted strategy multiple times, tried urgency, fake order, requested payment. Agent successfully extracted phone, URL, and scam patterns while maintaining believable persona."
}
```

---

## Testing the API

### Using curl

```bash
# Set your API key
export API_KEY="your-secret-api-key-here"

# Test health endpoint
curl http://localhost:8000/health

# Send a test message
curl -X POST http://localhost:8000/api/message \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "sessionId": "test-001",
  "message": {
    "sender": "scammer",
    "text": "Your account will be blocked. Share OTP now!",
    "timestamp": "2026-01-29T10:00:00Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
EOF
```

### Using Python

```python
import requests
import json

API_URL = "http://localhost:8000/api/message"
API_KEY = "your-secret-api-key-here"

payload = {
    "sessionId": "python-test-001",
    "message": {
        "sender": "scammer",
        "text": "Congratulations! You won ₹1 lakh. Claim now.",
        "timestamp": "2026-01-29T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(API_URL, json=payload, headers=headers)
print(json.dumps(response.json(), indent=2))
```

### Using test_client.py

```bash
# Run all scenarios
python test_client.py

# Interactive mode
python test_client.py interactive
```

---

## Response Time Benchmarks

Typical response times:

- **Scam Detection**: 5-20ms
- **Rule-based Agent Response**: 20-50ms
- **Claude API Response**: 500-2000ms
- **Intelligence Extraction**: 10-30ms
- **Total End-to-End**: 50-2100ms

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Invalid API key"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Internal server error processing request"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

---

## Best Practices for Integration

1. **Always include conversation history** for context
2. **Use unique session IDs** for each conversation
3. **Handle timeouts gracefully** (set 30s timeout)
4. **Retry failed requests** with exponential backoff
5. **Log all interactions** for debugging
6. **Monitor response times** and set alerts
7. **Validate responses** before processing

---

## Integration Example (FastAPI Client)

```python
import httpx
from typing import List, Dict

class HoneypotClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_message(
        self,
        session_id: str,
        message: str,
        history: List[Dict]
    ) -> Dict:
        """Send message to honeypot API"""
        
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": message,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "conversationHistory": history,
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/message",
            json=payload,
            headers=headers
        )
        
        return response.json()

# Usage
client = HoneypotClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

response = await client.send_message(
    session_id="unique-id",
    message="Scammer message here",
    history=[]
)
```

---

## Additional Resources

- Full API documentation: See [README.md](README.md)
- Deployment guide: See [DEPLOYMENT.md](DEPLOYMENT.md)
- Test scenarios: Run `python test_client.py`