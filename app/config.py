"""Configuration management for the application."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    SUPER_MIND_API_KEY = os.getenv("SUPER_MIND_API_KEY")
    DATABENTO_API_KEY = os.getenv("DATABENTO_API_KEY")
    OPENAI_BASE_URL = "https://space.ai-builders.com/backend/v1"
    OPENAI_MODEL = "supermind-agent-v1"
    AI_BUILDER_API_BASE = "https://space.ai-builders.com/backend"
    
    # Monitoring configuration
    MONITORED_TICKERS = ["SPY", "QQQ", "GLD", "BTC"]
    PRICE_CHANGE_THRESHOLD = 0.005  # 0.5% threshold
    MONITORING_INTERVAL_HOURS = 1
    
    # Timezone
    TIMEZONE = "America/New_York"

