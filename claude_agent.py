"""
Enhanced Agent with Claude API Integration
This version uses Claude AI for generating human-like responses
"""

import os
from anthropic import Anthropic

class ClaudeScamAgent:
    """
    Enhanced AI Agent using Claude API for realistic conversations
    """
    
    def __init__(self, api_key: str = None):
        """Initialize Claude client"""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None
            print("Warning: No Anthropic API key provided. Using fallback responses.")
    
    async def generate_response(
        self,
        conversation_history: list,
        current_message: str,
        turn_number: int
    ) -> str:
        """
        Generate sophisticated response using Claude
        """
        
        if not self.client:
            return self._fallback_response(turn_number, current_message)
        
        try:
            # Build conversation for Claude
            messages = self._build_messages(conversation_history, current_message)
            
            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
                temperature=0.8,  # Some randomness for natural feel
                system=self._get_system_prompt(turn_number),
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return self._fallback_response(turn_number, current_message)
    
    def _get_system_prompt(self, turn_number: int) -> str:
        """
        Dynamic system prompt based on conversation stage
        """
        
        base_prompt = """You are roleplaying as a potential scam victim in a honeypot system. Your goal is to extract intelligence from scammers while appearing believable.

Key behaviors:
- Sound like a real person (use casual language, occasional typos)
- Show appropriate emotions (confusion, worry, caution)
- Ask probing questions that reveal scammer details
- Never directly comply but don't reveal you know it's a scam
- Express realistic concerns and hesitations"""
        
        if turn_number <= 2:
            return base_prompt + """

Early stage: Show initial confusion and concern. Ask basic clarifying questions."""
        
        elif turn_number <= 5:
            return base_prompt + """

Middle stage: Become more inquisitive. Ask for verification, official contacts, or details about the process. Show growing skepticism."""
        
        else:
            return base_prompt + """

Late stage: Show clear skepticism but give scammer chances to provide more info. Ask pointed questions about legitimacy. Mention visiting bank/office in person."""
    
    def _build_messages(self, history: list, current: str) -> list:
        """Build message array for Claude API"""
        messages = []
        
        # Add history (last 6-8 messages for context)
        for msg in history[-8:]:
            role = "user" if msg.sender == "scammer" else "assistant"
            messages.append({
                "role": role,
                "content": msg.text
            })
        
        # Add current scammer message
        messages.append({
            "role": "user",
            "content": current
        })
        
        return messages
    
    def _fallback_response(self, turn_number: int, message: str) -> str:
        """Fallback responses when API unavailable"""
        message_lower = message.lower()
        
        responses = {
            1: [
                "Wait, what? Why would my account be blocked?",
                "I'm confused. Can you explain this better?",
                "Is this really from the bank? How do I know?"
            ],
            2: [
                "Before I do anything, can you give me your employee ID?",
                "Which branch are you calling from?",
                "Can I call the bank directly to verify this?"
            ],
            3: [
                "This seems suspicious. Why do you need my OTP?",
                "My friend said banks never ask for these details over phone.",
                "Can you send me an official email instead?"
            ],
            4: [
                "I think I should visit the branch in person.",
                "You're being very pushy. Real banks don't work like this.",
                "I'm going to call the customer care number on the back of my card."
            ]
        }
        
        stage = min(turn_number, 4)
        import random
        return random.choice(responses.get(stage, responses[4]))


# Example usage in main.py:
"""
# Initialize at startup
claude_agent = ClaudeScamAgent(api_key="your-anthropic-api-key")

# In handle_message function:
if session["agent_active"]:
    agent_response = await claude_agent.generate_response(
        conversation_history,
        current_message,
        session["turn_count"]
    )
"""