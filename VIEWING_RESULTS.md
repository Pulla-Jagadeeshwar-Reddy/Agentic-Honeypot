# Complete Guide: Where Results Go & How to See Them

## Understanding the Data Flow

```
Scammer Message → Your API → Scam Detection → AI Agent Response
                       ↓
                Intelligence Extraction
                       ↓
                 (After 8+ turns)
                       ↓
           ┌───────────┴───────────┐
           ↓                       ↓
    GUVI Endpoint            Local Storage
(for evaluation)           (for your viewing)
```

---

## Part 1: Where the Final Result Goes

### To GUVI (Official Submission)

**Endpoint:** `https://hackathon.guvi.in/api/updateHoneyPotFinalResult`

**What's sent:**
```json
{
  "sessionId": "bank-fraud-001",
  "scamDetected": true,
  "totalMessagesExchanged": 12,
  "extractedIntelligence": {
    "bankAccounts": ["1234567890"],
    "upiIds": ["scammer@paytm", "fraud@phonepe"],
    "phishingLinks": ["http://fake-bank.com"],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["urgent", "blocked", "otp", "verify"]
  },
  "agentNotes": "Scam detected with 0.85 confidence..."
}
```

**When it's sent:**
- After 8+ conversation turns
- OR when enough intelligence is gathered (5+ keywords)
- OR when scammer becomes suspicious

---

## Part 2: How to See the Results (4 Methods)

### Method 1: Console Output (Real-Time) ⭐ EASIEST

When you run `python main.py`, you'll see:

```bash
================================================================================
[Session bank-fraud-001] SENDING FINAL RESULT TO GUVI
================================================================================
{
  "sessionId": "bank-fraud-001",
  "scamDetected": true,
  "totalMessagesExchanged": 12,
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": [
      "scammer@paytm",
      "fraud@phonepe"
    ],
    "phishingLinks": [
      "http://fake-bank-verify.com"
    ],
    "phoneNumbers": [
      "+919876543210"
    ],
    "suspiciousKeywords": [
      "urgent",
      "blocked",
      "verify",
      "otp"
    ]
  },
  "agentNotes": "Scam detected with 0.85 confidence. Extracted 0 bank accounts, 2 UPI IDs, 1 phishing links, 1 phone numbers."
}
================================================================================

[Session bank-fraud-001] ✓ Saved locally to results/final_result_bank-fraud-001_20260129_120530.json
[Session bank-fraud-001] ✓ Successfully sent to GUVI endpoint
[Session bank-fraud-001] Response: {"status": "success"}
[Session bank-fraud-001] Conversation ended. Final result sent to https://hackathon.guvi.in/api/updateHoneyPotFinalResult
```

---

### Method 2: View Saved Results (After Test) ⭐ RECOMMENDED

All results are automatically saved to the `results/` folder.

**Step 1:** Run your test
```bash
python main.py  # Terminal 1
python test_client.py  # Terminal 2
```

**Step 2:** View the results
```bash
# List all results
python view_final_results.py list

# View specific result
python view_final_results.py view bank-fraud-001

# See summary of all results
python view_final_results.py summary
```

**Example Output:**
```
================================================================================
FINAL RESULT SENT TO GUVI
================================================================================

Session ID: bank-fraud-001
Scam Detected: True
Total Messages: 12

Agent Notes:
Scam detected with 0.85 confidence. Extracted 0 bank accounts, 2 UPI IDs, 1 phishing links, 1 phone numbers.

--------------------------------------------------------------------------------
EXTRACTED INTELLIGENCE
--------------------------------------------------------------------------------

💳 UPI IDs (2):
  • scammer@paytm
  • fraud@phonepe

📞 Phone Numbers (1):
  • +919876543210

🔗 Phishing Links (1):
  • http://fake-bank-verify.com

🚩 Suspicious Keywords (8):
  urgent, blocked, verify, otp, account, immediately, share, details
```

---

### Method 3: Use the API Endpoints

**List all sessions:**
```bash
curl -H "x-api-key: your-secret-api-key-here" \
  http://localhost:8000/sessions
```

**Get intelligence for specific session:**
```bash
curl -H "x-api-key: your-secret-api-key-here" \
  http://localhost:8000/intelligence/bank-fraud-001
```

**Response:**
```json
{
  "sessionId": "bank-fraud-001",
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": ["scammer@paytm", "fraud@phonepe"],
    "phishingLinks": ["http://fake-bank-verify.com"],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["urgent", "blocked", "verify", "otp"]
  },
  "summary": {
    "totalBankAccounts": 0,
    "totalUpiIds": 2,
    "totalPhishingLinks": 1,
    "totalPhoneNumbers": 1,
    "totalSuspiciousKeywords": 4
  }
}
```

---

### Method 4: Check the Saved JSON Files

All results are saved in `results/` directory:

```bash
ls results/
# final_result_bank-fraud-001_20260129_120530.json
# final_result_upi-fraud-002_20260129_120645.json
# ...

# View with any JSON viewer
cat results/final_result_bank-fraud-001_20260129_120530.json | python -m json.tool
```

---

## Part 3: Complete Workflow Example

### Step-by-Step: Run a Test and View Results

**1. Start the server**
```bash
cd scam-honeypot
python main.py
```

**2. In another terminal, run a test**
```bash
python test_client.py
```

You'll see the conversation:
```
================================================================================
Running Scenario: Bank Account Fraud
Session ID: bank-fraud-001
================================================================================

--- Turn 1 ---
Scammer: URGENT: Your bank account will be blocked in 2 hours...
Agent: Oh no! Why would my account be blocked?

--- Turn 2 ---
Scammer: Share your UPI ID to avoid account suspension.
Agent: Wait, why do you need my UPI ID? Which bank are you calling from?
```

**3. Watch the server terminal for the final result**

After 8+ turns, you'll see:
```
================================================================================
[Session bank-fraud-001] SENDING FINAL RESULT TO GUVI
================================================================================
{
  "sessionId": "bank-fraud-001",
  "scamDetected": true,
  ...
}
[Session bank-fraud-001] ✓ Successfully sent to GUVI endpoint
```

**4. View the results**
```bash
# Quick summary
python view_final_results.py summary

# Detailed view
python view_final_results.py view bank-fraud-001
```

---

## Part 4: What to Look For

### Key Intelligence Items:

✅ **UPI IDs** - Payment identifiers like `scammer@paytm`
✅ **Phone Numbers** - Contact numbers like `+919876543210`
✅ **Phishing Links** - Fake websites like `http://fake-bank.com`
✅ **Bank Accounts** - Account numbers (various formats)
✅ **Keywords** - Scam indicators like "urgent", "verify", "blocked"

### Good Session Example:
```
Session: bank-fraud-001
✓ Scam Detected: True
✓ Confidence: 0.85
✓ Messages: 12 turns
✓ Intelligence:
  - 2 UPI IDs
  - 1 Phone Number
  - 1 Phishing Link
  - 8 Suspicious Keywords
```

---

## Part 5: Troubleshooting

### "I don't see any results"

**Solution 1:** Check if test completed
```bash
# The test should run 8+ turns before sending results
python test_client.py  # Wait for it to complete
```

**Solution 2:** Check the results folder
```bash
ls results/
# Should see JSON files
```

**Solution 3:** Check console output
```bash
# Look for this in the server terminal:
[Session XXX] Conversation ended. Final result sent.
```

### "Results folder is empty"

The API only sends final results when:
1. Scam is detected (confidence ≥ 0.3)
2. Conversation reaches 8+ turns
3. Or enough intelligence is gathered

Try running: `python test_client.py` which simulates full scam conversations.

### "GUVI endpoint returns error"

This is normal during development! The results are still saved locally in `results/` folder.

```bash
# Check if saved locally
ls results/

# View the saved result
python view_final_results.py list
```

---

## Part 6: Viewing Intelligence During Conversation

Want to see intelligence AS IT'S BEING EXTRACTED?

Add this to `main.py` after the intelligence extraction:

```python
# After: session["intelligence"] = IntelligenceExtractor.extract(all_messages)

# Add this:
print(f"[Session {session_id}] Current intelligence:")
print(f"  UPI IDs: {session['intelligence'].upiIds}")
print(f"  Phone Numbers: {session['intelligence'].phoneNumbers}")
print(f"  Links: {session['intelligence'].phishingLinks}")
```

Now you'll see real-time updates as intelligence is extracted!

---

## Quick Reference Commands

```bash
# Start server
python main.py

# Run test (new terminal)
python test_client.py

# View all results
python view_final_results.py list

# View specific result
python view_final_results.py view bank-fraud-001

# See summary
python view_final_results.py summary

# Export to CSV
python view_final_results.py export

# View using API
curl -H "x-api-key: your-key" http://localhost:8000/sessions
```

---

## Summary

**Where final results go:**
1. ✅ GUVI evaluation endpoint (for scoring)
2. ✅ Local `results/` folder (for your viewing)
3. ✅ Console output (real-time)

**How to see them:**
1. Watch the console when running `python main.py`
2. Use `python view_final_results.py list`
3. Check the `results/` folder
4. Query the API endpoints

The results contain ALL extracted intelligence: UPI IDs, phone numbers, phishing links, bank accounts, and suspicious keywords!