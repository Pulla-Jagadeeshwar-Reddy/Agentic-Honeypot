"""
Test Client for Scam Honeypot API
Simulates the evaluation platform sending test messages
"""

import httpx
import asyncio
from datetime import datetime, timezone
import json

API_URL = "http://localhost:8000/api/message"
API_KEY = "your-secret-api-key-here"

class TestScenario:
    """Test scenarios for different scam types"""
    
    BANK_FRAUD_SCENARIO = [
        "Your bank account will be blocked today. Verify immediately.",
        "Share your UPI ID to avoid account suspension.",
        "We need your OTP to verify the transaction.",
        "Click this link to update your KYC: http://fake-bank-link.com",
        "If you don't provide details now, we will close your account permanently."
    ]
    
    UPI_FRAUD_SCENARIO = [
        "Congratulations! You won ₹50,000 in lucky draw.",
        "To claim prize, share your UPI ID.",
        "You need to pay ₹500 processing fee first.",
        "Send money to winner@paytm for verification.",
        "This offer expires in 2 hours. Act fast!"
    ]
    
    PHISHING_SCENARIO = [
        "Dear customer, your KYC needs urgent update.",
        "Click here to verify: http://phishing-site.com/verify",
        "Failure to update will result in service termination.",
        "Enter your card details on the website.",
        "This is your last warning before account freeze."
    ]


async def send_message(session_id: str, message: str, history: list) -> dict:
    """Send a message to the API"""
    
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": message,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        },
        "conversationHistory": history,
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(API_URL, json=payload, headers=headers)
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return None


async def run_scenario(session_id: str, messages: list, scenario_name: str):
    """Run a complete scam scenario"""
    
    print(f"\n{'='*80}")
    print(f"Running Scenario: {scenario_name}")
    print(f"Session ID: {session_id}")
    print(f"{'='*80}\n")
    
    conversation_history = []
    
    for i, scammer_msg in enumerate(messages):
        print(f"\n--- Turn {i+1} ---")
        print(f"Scammer: {scammer_msg}")
        
        # Send scammer message
        response = await send_message(session_id, scammer_msg, conversation_history)
        
        if response and response.get("status") == "success":
            agent_reply = response.get("reply")
            print(f"Agent: {agent_reply}")
            
            # Update conversation history
            conversation_history.append({
                "sender": "scammer",
                "text": scammer_msg,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            })
            conversation_history.append({
                "sender": "user",
                "text": agent_reply,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            })
            
            # Wait a bit between messages
            await asyncio.sleep(2)
        else:
            print(f"Error: {response}")
            break
    
    print(f"\n{'='*80}")
    print(f"Scenario '{scenario_name}' completed!")
    print(f"{'='*80}\n")


async def test_api():
    """Run all test scenarios"""
    
    print("\n" + "="*80)
    print("SCAM HONEYPOT API TESTER")
    print("="*80)
    
    # Test health endpoint
    async with httpx.AsyncClient() as client:
        health = await client.get("http://localhost:8000/health")
        print(f"\nAPI Health: {health.json()}\n")
    
    # Run scenarios
    scenarios = [
        ("bank-fraud-001", TestScenario.BANK_FRAUD_SCENARIO, "Bank Account Fraud"),
        ("upi-fraud-002", TestScenario.UPI_FRAUD_SCENARIO, "UPI Prize Scam"),
        ("phishing-003", TestScenario.PHISHING_SCENARIO, "Phishing Attack")
    ]
    
    for session_id, messages, name in scenarios:
        await run_scenario(session_id, messages, name)
        await asyncio.sleep(3)  # Pause between scenarios
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80 + "\n")


async def interactive_test():
    """Interactive testing mode"""
    
    print("\n" + "="*80)
    print("INTERACTIVE TEST MODE")
    print("="*80 + "\n")
    
    session_id = f"interactive-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    conversation_history = []
    
    print(f"Session ID: {session_id}")
    print("Type scammer messages (or 'quit' to exit):\n")
    
    while True:
        scammer_msg = input("Scammer: ").strip()
        
        if scammer_msg.lower() in ['quit', 'exit', 'q']:
            break
        
        if not scammer_msg:
            continue
        
        response = await send_message(session_id, scammer_msg, conversation_history)
        
        if response and response.get("status") == "success":
            agent_reply = response.get("reply")
            print(f"Agent: {agent_reply}\n")
            
            # Update history
            conversation_history.append({
                "sender": "scammer",
                "text": scammer_msg,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            })
            conversation_history.append({
                "sender": "user",
                "text": agent_reply,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            })
        else:
            print(f"Error: {response}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_test())
    else:
        asyncio.run(test_api())