SCAM_KEYWORDS = [
    "urgent",
    "verify",
    "account blocked",
    "otp",
    "upi",
    "bank",
    "suspended",
    "click link"
]

def analyze_message(text: str) -> dict:
    text_lower = text.lower()

    hits = sum(1 for k in SCAM_KEYWORDS if k in text_lower)
    confidence = min(hits / len(SCAM_KEYWORDS), 1.0)

    return {
        "scam": confidence >= 0.25,
        "confidence": round(confidence, 2)
    }
