import re

def extract_intelligence(text: str) -> dict:
    """
    EXACT schema required by GUVI.
    """

    return {
        "bankAccounts": [],
        "upiIds": re.findall(
            r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", text
        ),
        "phishingLinks": re.findall(
            r"https?://\S+", text
        ),
        "phoneNumbers": re.findall(
            r"\b\d{10}\b", text
        ),
        "suspiciousKeywords": [
            k for k in [
                "urgent",
                "verify",
                "account blocked",
                "otp",
                "upi",
                "bank",
                "suspended"
            ]
            if k in text.lower()
        ]
    }
