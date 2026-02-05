import json
import os
from typing import List

MEMORY_FILE = "scam_memory.json"

def load_memory() -> List[str]:
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory: List[str]):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def update_memory(new_patterns: List[str]):
    memory = load_memory()
    for p in new_patterns:
        if p not in memory:
            memory.append(p)
    save_memory(memory)

def get_memory_summary() -> str:
    memory = load_memory()
    if not memory:
        return "No known scam patterns yet."
    return "Previously observed scam tactics:\n" + "\n".join(f"- {m}" for m in memory)
