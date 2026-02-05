import requests
import time
import json

# CONFIGURE THESE
API_URL = "http://localhost:8000/api/message"  # Change to your deployed URL
API_KEY = "your-secret-key-change-this"  # Must match your API_KEY in .env

def test_scam_detection():
    """Test the honeypot with sample scam messages"""
    
    session_id = f"test-{int(time.time())}"
    
    # Test message 1: Initial scam
    print("=" * 60)
    print("TEST 1: Initial scam message")
    print("=" * 60)
    
    response1 = requests.post(
        API_URL,
        json={
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": "Your bank account will be blocked today. Verify immediately by sharing OTP.",
                "timestamp": int(time.time() * 1000)
            },
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        },
        headers={
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        }
    )
    
    print(f"Status Code: {response1.status_code}")
    print(f"Response: {json.dumps(response1.json(), indent=2)}\n")
    
    if response1.status_code != 200:
        print("❌ TEST FAILED - Check your API_KEY and URL")
        return
    
    reply1 = response1.json()["reply"]
    
    # Test message 2: Scammer provides account number
    print("=" * 60)
    print("TEST 2: Scammer provides account number")
    print("=" * 60)
    
    time.sleep(1)  # Small delay
    
    response2 = requests.post(
        API_URL,
        json={
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": "Send your OTP to this account: 1234567890123456 or UPI: scammer@paytm",
                "timestamp": int(time.time() * 1000)
            },
            "conversationHistory": [
                {
                    "sender": "scammer",
                    "text": "Your bank account will be blocked today. Verify immediately.",
                    "timestamp": int(time.time() * 1000) - 5000
                },
                {
                    "sender": "user",
                    "text": reply1,
                    "timestamp": int(time.time() * 1000) - 3000
                }
            ],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        },
        headers={
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        }
    )
    
    print(f"Status Code: {response2.status_code}")
    print(f"Response: {json.dumps(response2.json(), indent=2)}\n")
    
    # Test message 3: More details
    print("=" * 60)
    print("TEST 3: Extracting phone number")
    print("=" * 60)
    
    time.sleep(1)
    
    response3 = requests.post(
        API_URL,
        json={
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": "Call me urgently at +919876543210 or visit http://fake-bank.com/verify",
                "timestamp": int(time.time() * 1000)
            },
            "conversationHistory": [
                {
                    "sender": "scammer",
                    "text": "Your bank account will be blocked today.",
                    "timestamp": int(time.time() * 1000) - 10000
                },
                {
                    "sender": "user",
                    "text": reply1,
                    "timestamp": int(time.time() * 1000) - 8000
                },
                {
                    "sender": "scammer",
                    "text": "Send OTP to 1234567890123456",
                    "timestamp": int(time.time() * 1000) - 5000
                },
                {
                    "sender": "user",
                    "text": response2.json()["reply"],
                    "timestamp": int(time.time() * 1000) - 3000
                }
            ],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        },
        headers={
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        }
    )
    
    print(f"Status Code: {response3.status_code}")
    print(f"Response: {json.dumps(response3.json(), indent=2)}\n")
    
    print("=" * 60)
    print("✅ TESTS COMPLETED")
    print("=" * 60)
    print("\nExpected intelligence extraction:")
    print("- Bank Accounts: ['1234567890123456']")
    print("- UPI IDs: ['scammer@paytm']")
    print("- Phone Numbers: ['+919876543210']")
    print("- Phishing Links: ['http://fake-bank.com/verify']")
    print("- Keywords: ['urgent', 'verify', 'blocked', 'OTP', etc.]")
    print("\nCheck your terminal logs to see if final callback was sent!")

def test_non_scam():
    """Test with a non-scam message"""
    print("\n" + "=" * 60)
    print("TEST: Non-scam message (should not engage)")
    print("=" * 60)
    
    response = requests.post(
        API_URL,
        json={
            "sessionId": f"test-normal-{int(time.time())}",
            "message": {
                "sender": "scammer",
                "text": "Hello, how are you today?",
                "timestamp": int(time.time() * 1000)
            },
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        },
        headers={
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("Expected: Generic polite response (no scam engagement)\n")

if __name__ == "__main__":
    print("\n🧪 AGENTIC HONEYPOT TEST SUITE")
    print("=" * 60)
    print(f"Testing API at: {API_URL}")
    print("=" * 60)
    
    # Test health endpoint
    try:
        health = requests.get(API_URL.replace("/api/message", "/health"))
        print(f"✅ Health Check: {health.json()}\n")
    except:
        print("❌ Cannot connect to API. Make sure it's running!\n")
        exit(1)
    
    # Run tests
    test_scam_detection()
    test_non_scam()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("=" * 60)
    print("1. Check if extraction is working (see output above)")
    print("2. Verify final callback was sent (check terminal logs)")
    print("3. Test with GUVI's test interface")
    print("4. Deploy to production!")
