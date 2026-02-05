# Deployment Guide

This guide covers various deployment options for the Scam Honeypot API.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Considerations](#production-considerations)

---

## Local Development

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) Virtual environment tool

### Steps

1. **Clone/Download the project**

```bash
cd scam-honeypot
```

2. **Create virtual environment** (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.template .env
# Edit .env with your values
```

5. **Run the server**

```bash
python main.py
```

Or using uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. **Test the API**

```bash
# In a new terminal
python test_client.py
```

The API will be available at `http://localhost:8000`

### Development Tips

- Use `--reload` flag for auto-reloading on code changes
- Check logs in console for debugging
- Use interactive test mode: `python test_client.py interactive`

---

## Docker Deployment

### Prerequisites

- Docker installed
- Docker Compose (optional but recommended)

### Option 1: Using Docker Compose (Recommended)

1. **Configure environment**

```bash
cp .env.template .env
# Edit .env with your values
```

2. **Build and run**

```bash
docker-compose up --build
```

To run in background:

```bash
docker-compose up -d
```

3. **Check status**

```bash
docker-compose ps
docker-compose logs -f scam-honeypot
```

4. **Stop services**

```bash
docker-compose down
```

### Option 2: Using Docker directly

1. **Build the image**

```bash
docker build -t scam-honeypot:latest .
```

2. **Run the container**

```bash
docker run -d \
  --name scam-honeypot \
  -p 8000:8000 \
  -e HONEYPOT_API_KEY="your-secret-key" \
  -e ANTHROPIC_API_KEY="your-anthropic-key" \
  scam-honeypot:latest
```

3. **View logs**

```bash
docker logs -f scam-honeypot
```

4. **Stop container**

```bash
docker stop scam-honeypot
docker rm scam-honeypot
```

---

## Cloud Deployment

### AWS EC2

1. **Launch EC2 Instance**
   - Ubuntu 22.04 LTS
   - t2.micro or larger
   - Security group: Allow port 8000

2. **Connect and setup**

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv -y

# Clone your project
git clone <your-repo-url>
cd scam-honeypot

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure environment**

```bash
cp .env.template .env
nano .env  # Edit with your values
```

4. **Run with systemd (for production)**

Create service file:

```bash
sudo nano /etc/systemd/system/scam-honeypot.service
```

Add content:

```ini
[Unit]
Description=Scam Honeypot API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/scam-honeypot
Environment="PATH=/home/ubuntu/scam-honeypot/venv/bin"
EnvironmentFile=/home/ubuntu/scam-honeypot/.env
ExecStart=/home/ubuntu/scam-honeypot/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable scam-honeypot
sudo systemctl start scam-honeypot
sudo systemctl status scam-honeypot
```

5. **Setup Nginx (optional, for HTTPS)**

```bash
sudo apt install nginx certbot python3-certbot-nginx -y

# Configure Nginx
sudo nano /etc/nginx/sites-available/scam-honeypot
```

Add:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/scam-honeypot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### Heroku

1. **Install Heroku CLI**

```bash
# Follow instructions at https://devcenter.heroku.com/articles/heroku-cli
```

2. **Create Procfile**

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

3. **Deploy**

```bash
heroku login
heroku create your-app-name
heroku config:set HONEYPOT_API_KEY=your-key
heroku config:set ANTHROPIC_API_KEY=your-anthropic-key
git push heroku main
```

### Railway

1. **Install Railway CLI**

```bash
npm i -g @railway/cli
```

2. **Deploy**

```bash
railway login
railway init
railway up
```

3. **Set environment variables**

```bash
railway variables set HONEYPOT_API_KEY=your-key
railway variables set ANTHROPIC_API_KEY=your-anthropic-key
```

### Google Cloud Run

1. **Build and push to Container Registry**

```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/scam-honeypot
```

2. **Deploy to Cloud Run**

```bash
gcloud run deploy scam-honeypot \
  --image gcr.io/PROJECT-ID/scam-honeypot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars HONEYPOT_API_KEY=your-key,ANTHROPIC_API_KEY=your-key
```

---

## Production Considerations

### 1. Security

**API Key Management**
```bash
# Never commit API keys to git
# Use environment variables or secret management services

# AWS Secrets Manager
aws secretsmanager create-secret --name honeypot-api-key --secret-string "your-key"

# Or use .env files with proper permissions
chmod 600 .env
```

**HTTPS**
- Always use HTTPS in production
- Use Let's Encrypt for free SSL certificates
- Configure proper CORS policies

**Rate Limiting**
```python
# Add to main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/message")
@limiter.limit("10/minute")
async def handle_message(...):
    ...
```

### 2. Monitoring & Logging

**Structured Logging**
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'session_id': getattr(record, 'session_id', None)
        }
        return json.dumps(log_data)
```

**Health Checks**
- Monitor `/health` endpoint
- Set up alerting for downtime
- Track response times

**Recommended Tools**
- **Monitoring**: Prometheus + Grafana, DataDog, New Relic
- **Logging**: ELK Stack, CloudWatch, Papertrail
- **Error Tracking**: Sentry

### 3. Performance

**Database for Sessions**

Replace in-memory dict with Redis:

```python
import redis

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

# Store session
redis_client.setex(
    f"session:{session_id}",
    1800,  # 30 minutes TTL
    json.dumps(session_data)
)
```

**Connection Pooling**
```python
import httpx

# Create a client pool
http_client = httpx.AsyncClient(
    timeout=30.0,
    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
)
```

**Caching**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def detect_scam_cached(message_hash):
    # Cache detection results
    ...
```

### 4. Scalability

**Horizontal Scaling**
- Deploy multiple instances behind load balancer
- Use sticky sessions for conversation continuity
- Share session state via Redis/Database

**Load Balancer Configuration (Nginx)**
```nginx
upstream scam_honeypot {
    least_conn;
    server 10.0.1.10:8000;
    server 10.0.1.11:8000;
    server 10.0.1.12:8000;
}

server {
    location / {
        proxy_pass http://scam_honeypot;
    }
}
```

### 5. Backup & Recovery

**Database Backups**
```bash
# Automated Redis backups
redis-cli BGSAVE

# Cron job for daily backups
0 2 * * * redis-cli BGSAVE && cp /var/lib/redis/dump.rdb /backup/
```

**Application Logs**
```bash
# Rotate logs
sudo nano /etc/logrotate.d/scam-honeypot

/var/log/scam_honeypot/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
}
```

### 6. Testing in Production

**Smoke Tests**
```bash
#!/bin/bash
# smoke_test.sh

API_URL="https://your-api.com"
API_KEY="your-key"

# Health check
curl -f $API_URL/health || exit 1

# Test message
curl -X POST $API_URL/api/message \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"test","message":{"sender":"scammer","text":"test","timestamp":"2024-01-01T00:00:00Z"},"conversationHistory":[]}'

echo "Smoke tests passed!"
```

**Load Testing**
```bash
# Using locust
pip install locust

# Create locustfile.py and run
locust -f locustfile.py --host=https://your-api.com
```

---

## Troubleshooting

### Common Issues

**Port already in use**
```bash
# Find process using port 8000
sudo lsof -i :8000
# Kill process
sudo kill -9 <PID>
```

**Permission denied**
```bash
# Fix permissions
chmod +x main.py
# Or run with sudo (not recommended)
```

**Out of memory**
```bash
# Monitor memory
free -h
# Adjust worker count or upgrade instance
```

**High CPU usage**
```bash
# Check processes
top
# Optimize detection algorithms or scale horizontally
```

---

## Support

For issues or questions:
1. Check the [README.md](README.md)
2. Review logs for error messages
3. Test with `test_client.py`
4. Verify environment variables

---

**Happy Deploying! 🚀**