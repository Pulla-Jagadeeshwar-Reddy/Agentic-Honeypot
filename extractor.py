import re

def extract_intelligence(text: str) -> dict:
    return {
        "phone_numbers": re.findall(r"\b\d{10}\b", text),
        "upi_ids": re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", text),
        "urls": re.findall(r"https?://\S+", text),
        "bank_keywords": [
            w for w in ["sbi", "hdfc", "icici", "axis", "paytm"]
            if w in text.lower()
        ]
    }
