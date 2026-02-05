import re

SCAM_KEYWORDS = [
    "otp", "kyc", "upi", "account blocked",
    "verify now", "bank alert", "refund",
    "click link", "urgent", "limited time"
]

def analyze_message(text: str) -> dict:
    text_lower = text.lower()

    score = 0
    for keyword in SCAM_KEYWORDS:
        if keyword in text_lower:
            score += 1

    confidence = min(score / len(SCAM_KEYWORDS), 1.0)

    return {
        "scam": confidence >= 0.25,
        "confidence": round(confidence, 2)
    }
