"""
Configuration file for Scam Honeypot API
Customize these settings for your deployment
"""

import os

class Config:
    """Configuration settings"""
    
    # API Settings
    API_KEY = os.getenv("HONEYPOT_API_KEY", "Decay-of-Coders")
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # GUVI Callback
    GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    # Claude AI Settings (optional but recommended)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", None)
    CLAUDE_MODEL = "claude-sonnet-4-20250514"
    CLAUDE_MAX_TOKENS = 150
    CLAUDE_TEMPERATURE = 0.8
    
    # Agent Behavior Settings
    MIN_TURNS_BEFORE_END = 5  # Minimum conversation turns
    MAX_TURNS_BEFORE_END = 12  # Maximum conversation turns
    SCAM_DETECTION_THRESHOLD = 0.3  # Confidence threshold (0.0-1.0)
    MIN_INTELLIGENCE_ITEMS = 3  # Min items before ending conversation
    
    # Session Settings
    SESSION_TIMEOUT_MINUTES = 30
    MAX_ACTIVE_SESSIONS = 1000
    
    # Scam Detection Keywords (can be extended)
    CRITICAL_KEYWORDS = [
        "otp", "pin", "cvv", "password", "card number",
        "bank account", "upi id", "paytm", "phonepe"
    ]
    
    URGENCY_KEYWORDS = [
        "urgent", "immediately", "now", "today", "expire",
        "blocked", "suspended", "terminated"
    ]
    
    REWARD_KEYWORDS = [
        "prize", "won", "lottery", "congratulations",
        "refund", "cashback", "offer"
    ]
    
    # Agent Response Templates
    PERSONA_TRAITS = [
        "slightly tech-unsavvy",
        "cautious but curious",
        "concerned about security",
        "wants to verify information",
        "asks clarifying questions"
    ]
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "scam_honeypot.log"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    MAX_REQUESTS_PER_SESSION_PER_MINUTE = 10


# Development vs Production
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"


# Select configuration based on environment
ENV = os.getenv("ENVIRONMENT", "development")
if ENV == "production":
    config = ProductionConfig()
else:

    config = DevelopmentConfig()
