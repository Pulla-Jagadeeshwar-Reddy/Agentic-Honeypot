import requests

GUVI_ENDPOINT = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

def send_final_result(
    session_id: str,
    scam_detected: bool,
    total_messages: int,
    intelligence: dict,
    agent_notes: str
):
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": {
            "bankAccounts": intelligence.get("bankAccounts", []),
            "upiIds": intelligence.get("upiIds", []),
            "phishingLinks": intelligence.get("phishingLinks", []),
            "phoneNumbers": intelligence.get("phoneNumbers", []),
            "suspiciousKeywords": intelligence.get("suspiciousKeywords", [])
        },
        "agentNotes": agent_notes
    }

    try:
        requests.post(GUVI_ENDPOINT, json=payload, timeout=5)
    except Exception:
        # Never crash honeypot because of callback
        pass
