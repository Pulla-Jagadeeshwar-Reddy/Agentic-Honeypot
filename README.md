# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

An AI-powered honeypot system that detects scam messages, autonomously engages scammers, and extracts intelligence without revealing detection.

## 🎯 Features

- **Intelligent Scam Detection**: Multi-layered detection using keyword analysis, urgency patterns, and information request identification
- **Autonomous AI Agent**: Engages scammers with human-like responses while gathering intelligence
- **Intelligence Extraction**: Automatically extracts bank accounts, UPI IDs, phone numbers, phishing links, and suspicious keywords
- **Multi-turn Conversations**: Handles complex, adaptive scammer tactics across multiple conversation turns
- **REST API**: Clean, documented API endpoints for easy integration
- **GUVI Integration**: Automatic callback to evaluation endpoint with extracted intelligence

## 🏗️ Architecture

```
┌─────────────────┐
│  Incoming Msg   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Scam Detection  │ ◄── Keyword Analysis
│     Engine      │ ◄── Pattern Matching
└────────┬────────┘ ◄── Confidence Scoring
         │
         ▼
    Is Scam?
         │
    ┌────┴────┐
    │   YES   │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│   AI Agent      │ ◄── Claude API (optional)
│  Engagement     │ ◄── Rule-based fallback
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Intelligence   │ ◄── Extract Bank Info
│   Extraction    │ ◄── Extract UPI IDs
└────────┬────────┘ ◄── Extract URLs
         │          ◄── Extract Phone Numbers
         ▼
┌─────────────────┐
│ Send to GUVI    │
│   Evaluation    │
└─────────────────┘
```

## 📋 Requirements

- Python 3.8+
- FastAPI
- httpx
- Anthropic API key (optional, for enhanced responses)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or create the project directory
cd scam-honeypot

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Edit `config.py` or set environment variables:

```bash
# Required
export HONEYPOT_API_KEY="your-secret-api-key"

# Optional (for enhanced AI responses)
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Optional settings
export API_PORT="8000"
export ENVIRONMENT="development"
```

### 3. Run the Server

```bash
# Start the API server
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 4. Test the API

```bash
# Run automated tests
python test_client.py

# Or interactive mode
python test_client.py interactive
```

## 📡 API Documentation

### Authentication

All requests require an API key in the header:

```
x-api-key: your-secret-api-key
Content-Type: application/json
```

### Endpoint: POST `/api/message`

Main endpoint for processing incoming messages.

**Request Body:**

```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": "2026-01-21T10:15:30Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**

```json
{
  "status": "success",
  "reply": "Oh no! Why would my account be blocked? I haven't done anything wrong."
}
```

### Endpoint: GET `/health`

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "active_sessions": 3
}
```

## 🧠 How It Works

### 1. Scam Detection

The system uses multiple detection mechanisms:

- **Keyword Analysis**: Identifies scam-related terms (urgent, verify, blocked, OTP, etc.)
- **Pattern Matching**: Detects urgency patterns and sensitive information requests
- **URL Detection**: Identifies potential phishing links
- **Confidence Scoring**: Assigns a confidence score based on detected indicators

**Detection Threshold**: Messages with confidence ≥ 0.3 are flagged as scams

### 2. AI Agent Engagement

Once a scam is detected, the AI agent activates with specific objectives:

- **Appear believable**: Uses natural, slightly naive language
- **Extract intelligence**: Asks probing questions to reveal scammer details
- **Maintain engagement**: Shows interest but raises realistic concerns
- **Adapt responses**: Changes strategy based on conversation stage

**Agent Strategies by Stage:**

| Stage | Turns | Strategy |
|-------|-------|----------|
| Early | 1-2 | Show confusion, ask basic questions |
| Middle | 3-5 | Request verification, probe for details |
| Late | 6+ | Express skepticism, suggest in-person visit |

### 3. Intelligence Extraction

The system continuously extracts:

- **Bank Accounts**: Account numbers and IFSC codes
- **UPI IDs**: Payment identifiers (user@bank format)
- **Phishing Links**: Suspicious URLs
- **Phone Numbers**: Contact information
- **Keywords**: Scam-related terminology

### 4. Final Result Callback

After sufficient engagement (8+ turns or enough intelligence), the system automatically sends results to the GUVI evaluation endpoint:

```json
{
  "sessionId": "session-id",
  "scamDetected": true,
  "totalMessagesExchanged": 12,
  "extractedIntelligence": {
    "bankAccounts": ["1234567890"],
    "upiIds": ["scammer@paytm"],
    "phishingLinks": ["http://fake-site.com"],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["urgent", "verify", "blocked"]
  },
  "agentNotes": "Scam detected with 0.85 confidence..."
}
```

## 🎨 Customization

### Adding Custom Scam Patterns

Edit `main.py` in the `ScamDetector` class:

```python
SCAM_KEYWORDS = [
    # Add your keywords here
    "new_scam_keyword",
    "another_pattern"
]
```

### Customizing Agent Responses

For rule-based responses, edit the `_rule_based_response` method in `ScamAgent` class.

For AI-powered responses, configure the system prompt in `claude_agent.py`.

### Adjusting Thresholds

Edit `config.py`:

```python
SCAM_DETECTION_THRESHOLD = 0.3  # Lower = more sensitive
MIN_TURNS_BEFORE_END = 5        # Minimum engagement
MAX_TURNS_BEFORE_END = 12       # Maximum engagement
```

## 🔒 Security & Ethics

### Ethical Guidelines

✅ **Do:**
- Use for legitimate scam detection and research
- Protect extracted data appropriately
- Follow responsible disclosure practices

❌ **Don't:**
- Impersonate real individuals
- Use for harassment
- Share extracted data publicly without sanitization

### Data Handling

- Session data is stored in memory (use Redis/DB for production)
- Sensitive information should be encrypted
- Implement data retention policies
- Ensure GDPR/privacy compliance

## 📊 Evaluation Criteria

The system is evaluated on:

1. **Scam Detection Accuracy** (30%)
   - True positive rate
   - False positive rate
   - Detection speed

2. **Agent Engagement Quality** (30%)
   - Human-likeness of responses
   - Conversation continuity
   - Adaptive behavior

3. **Intelligence Extraction** (25%)
   - Quantity of extracted data
   - Quality and accuracy
   - Data categorization

4. **API Performance** (15%)
   - Response time
   - Stability
   - Error handling

## 🚧 Production Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t scam-honeypot .
docker run -p 8000:8000 -e HONEYPOT_API_KEY=your-key scam-honeypot
```

### Using Cloud Platforms

**AWS EC2 / Azure VM:**
```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# Setup application
pip3 install -r requirements.txt

# Run with systemd or supervisor
```

**Heroku / Railway:**
```bash
# Add Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Monitoring

Add logging and monitoring:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scam_honeypot.log'),
        logging.StreamHandler()
    ]
)
```

## 🧪 Testing

### Unit Tests

```bash
# Run with pytest
pytest tests/
```

### Load Testing

```bash
# Using locust
locust -f locustfile.py --host=http://localhost:8000
```

### Example Test Scenarios

The `test_client.py` includes:

1. **Bank Fraud Scenario**: Account blocking threat
2. **UPI Fraud Scenario**: Prize/lottery scam
3. **Phishing Scenario**: KYC update phishing

## 📈 Performance Optimization

### Tips for Better Performance

1. **Use Redis for session storage** instead of in-memory dict
2. **Implement connection pooling** for GUVI callbacks
3. **Add caching** for repeated pattern matching
4. **Use async operations** throughout
5. **Enable rate limiting** per session

### Scaling

For high traffic:

- Deploy multiple instances behind a load balancer
- Use distributed session storage (Redis Cluster)
- Implement message queues (RabbitMQ/Kafka) for async processing
- Add database for persistent storage

## 🐛 Troubleshooting

### Common Issues

**Issue: API returns 401 Unauthorized**
- Solution: Check x-api-key header matches configuration

**Issue: Slow response times**
- Solution: Reduce conversation history size, optimize pattern matching

**Issue: Agent responses don't seem natural**
- Solution: Add Anthropic API key for Claude-powered responses

**Issue: Final callback fails**
- Solution: Check GUVI endpoint URL and network connectivity

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Scam Detection Patterns](https://www.fraudwatch.com/scam-types/)

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional scam detection patterns
- More sophisticated agent personalities
- Multi-language support
- Enhanced intelligence extraction
- Machine learning-based detection

## 📄 License

This project is for educational and hackathon purposes.

## 👥 Authors

Created for GUVI Hackathon - Agentic Honey-Pot Challenge

---

**Note**: Remember to never use this system to harass or impersonate individuals. Always follow ethical guidelines and local laws regarding automated communication systems.