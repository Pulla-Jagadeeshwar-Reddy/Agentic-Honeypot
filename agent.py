import random

def generate_agent_reply(message: str, history=None) -> str:
    """
    Human-like, adaptive responses.
    Does NOT reveal detection.
    """

    if history and len(history) > 1:
        return random.choice([
            "I already shared details earlier. Why do you need them again?",
            "This seems confusing. Can you clarify the issue?",
            "Which department are you calling from?"
        ])

    return random.choice([
        "Why is my account being suspended?",
        "Can you explain the issue clearly?",
        "Which bank is this regarding?",
        "I did not receive any prior notification."
    ])
