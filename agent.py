import os
import random
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a normal bank customer.
You are talking to a customer support executive.
You must sound confused but cooperative.
Never reveal that you know this is a scam.
Ask questions to make them continue.
"""

def generate_agent_reply(message: str, history=None) -> str:
    # 🔹 Fallback if no key
    if not os.getenv("OPENAI_API_KEY"):
        return random.choice([
            "Why is my account being suspended?",
            "Can you explain what the issue is?",
            "Which bank is this regarding?"
        ])

    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        for msg in history:
            role = "assistant" if msg.sender == "user" else "user"
            conversation.append({
                "role": role,
                "content": msg.text
            })

    conversation.append({
        "role": "user",
        "content": message
    })

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception:
        # safety fallback
        return "Can you please explain the issue once again?"
