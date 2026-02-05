# Quick Reference Card 🚀

## 📍 Where Final Results Go

```
┌─────────────────────────────────────────┐
│ Final Result Destination                │
├─────────────────────────────────────────┤
│ 1. GUVI Endpoint (for evaluation)       │
│    https://hackathon.guvi.in/api/...    │
│                                          │
│ 2. Local results/ folder (for viewing)  │
│    results/final_result_*.json          │
│                                          │
│ 3. Console output (real-time)           │
│    Prints to terminal                   │
└─────────────────────────────────────────┘
```

## 🎯 What Gets Extracted & Sent

```json
{
  "sessionId": "...",
  "scamDetected": true,
  "totalMessagesExchanged": 12,
  "extractedIntelligence": {
    "upiIds": ["scammer@paytm"],         // ← UPI IDs!
    "phoneNumbers": ["+91987654320"],    // ← Phone numbers!
    "phishingLinks": ["http://fake.com"], // ← Phishing links!
    "bankAccounts": ["1234567890"],      // ← Bank accounts!
    "suspiciousKeywords": ["urgent", "otp"] // ← Keywords!
  }
}
```

## 🏃 Quick Start (3 Steps)

```bash
# Step 1: Start server
python main.py

# Step 2: Run test (new terminal)
python test_client.py

# Step 3: View results
python view_final_results.py list
```

## 👀 How to See Results (Choose One)

### Option 1: Console (Live)
```bash
python main.py
# Watch for: [Session XXX] SENDING FINAL RESULT TO GUVI
```

### Option 2: View Saved Results ⭐ EASIEST
```bash
python view_final_results.py list      # List all
python view_final_results.py view bank-fraud-001  # Details
python view_final_results.py summary   # Summary
```

### Option 3: Use API
```bash
curl -H "x-api-key: your-key" \
  http://localhost:8000/intelligence/bank-fraud-001
```

### Option 4: Check Files
```bash
ls results/
cat results/final_result_bank-fraud-001_*.json
```

## 📊 View Intelligence During Conversation

```bash
# View session intelligence
python simple_viewer.py view bank-fraud-001

# List all sessions  
python simple_viewer.py list

# View only intelligence (no conversation)
python simple_viewer.py intel bank-fraud-001
```

## 🔧 Available Endpoints

```
GET  /health                      # Check if API is running
POST /api/message                 # Send message (main endpoint)
GET  /sessions                    # List all sessions
GET  /session/{session_id}        # Full session details
GET  /intelligence/{session_id}   # Intelligence only
```

## 📁 File Structure

```
scam-honeypot/
├── main.py                    # Main API server ⭐
├── test_client.py             # Test scenarios ⭐
├── view_final_results.py      # View sent results ⭐
├── simple_viewer.py           # View live sessions
├── requirements.txt           # Dependencies
├── README.md                  # Full documentation
├── VIEWING_RESULTS.md         # Detailed guide
└── results/                   # Saved results appear here
    └── final_result_*.json    # Auto-saved results
```

## 🎮 Test Scenarios Included

1. **Bank Fraud** - Account blocking threat
2. **UPI Scam** - Prize/lottery scam  
3. **Phishing** - KYC update phishing

All test scenarios extract real intelligence!

## 🐛 Common Issues

**Q: No results showing?**
```bash
# Make sure test completed (8+ turns)
python test_client.py

# Check results folder
ls results/

# Check console output
# Look for: [Session XXX] Conversation ended
```

**Q: GUVI endpoint returns error?**
```
Normal during development!
Results still saved in results/ folder.
```

**Q: Want to see intelligence as it's extracted?**
```
Watch the console output of python main.py
Intelligence prints after each turn.
```

## 💡 Pro Tips

✅ Run `python main.py` in one terminal (server)
✅ Run `python test_client.py` in another (test)  
✅ Use `python view_final_results.py summary` for overview
✅ Check `results/` folder for all saved data
✅ UPI IDs extracted automatically from text!

## 📞 Example: What You'll See

**Console Output:**
```
[Session bank-fraud-001] Scam detected! Confidence: 0.85
[Session bank-fraud-001] SENDING FINAL RESULT TO GUVI
{
  "upiIds": ["scammer@paytm", "fraud@phonepe"],
  "phoneNumbers": ["+919876543210"],
  ...
}
[Session bank-fraud-001] ✓ Successfully sent to GUVI
[Session bank-fraud-001] ✓ Saved to results/final_result_*.json
```

**View Results:**
```bash
$ python view_final_results.py view bank-fraud-001

Session: bank-fraud-001
💳 UPI IDs (2):
  • scammer@paytm
  • fraud@phonepe

📞 Phone Numbers (1):
  • +919876543210

🔗 Phishing Links (1):
  • http://fake-bank-verify.com
```

## 🎯 Key Commands (Copy-Paste Ready)

```bash
# Setup
cd scam-honeypot
pip install -r requirements.txt

# Run
python main.py                              # Start server
python test_client.py                       # Run tests
python view_final_results.py summary        # See all results

# View specific session
python view_final_results.py view bank-fraud-001

# Interactive mode
python test_client.py interactive           # Test interactively
python simple_viewer.py list                # View live sessions
```

---

**Need help?** Read VIEWING_RESULTS.md for complete guide!