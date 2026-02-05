from openai import OpenAI
from config import OPENAI_API_KEY
from memory_store import get_memory_summary, update_memory

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a realistic human interacting with a scammer.

Goals:
- Stay engaged without giving sensitive info
- Ask probing questions to extract scammer details
- Vary language and tone (avoid repetition)
- Learn from past scams and adapt
- Never reveal you're an AI or scam detector

Be natural, curious, slightly worried.
"""

async def generate_response(conversation, latest_msg: str) -> str:
    memory = get_memory_summary()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": memory},
    ]

    for msg in conversation[-6:]:
        role = "user" if msg["sender"] == "scammer" else "assistant"
        messages.append({"role": role, "content": msg["text"]})

    messages.append({"role": "user", "content": latest_msg})

   response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    temperature=0.9,        # 🔥 increase creativity
    frequency_penalty=0.8,  # 🔥 punish repeated phrases
    presence_penalty=0.6,   # 🔥 encourage new ideas
    max_tokens=200
)


    reply = response.choices[0].message.content.strip()

    # Learn new patterns
    if any(word in latest_msg.lower() for word in ["blocked", "verify", "otp", "account"]):
        update_memory([latest_msg[:120]])

    return reply
