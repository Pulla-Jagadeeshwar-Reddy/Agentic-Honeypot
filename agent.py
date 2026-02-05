import os
import random

def generate_agent_reply(message: str, history=None) -> str:
    """
    Engages scammer without revealing detection.
    Falls back safely if no LLM key is present.
    """

    if os.getenv("ANTHROPIC_API_KEY"):
        return (
            "Hi, I got your message. "
            "Can you please explain the issue clearly? "
            "Which bank and what transaction is this about?"
        )

    # Rule-based fallback (NO hallucination risk)
    return random.choice([
        "I am not sure I understand. Which bank are you referring to?",
        "Can you tell me the exact issue with my account?",
        "I recently changed phones. What details do you need?",
        "Is this related to UPI or net banking?"
    ])
