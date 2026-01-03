"""Configuration management for the application."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    SUPER_MIND_API_KEY = os.getenv("SUPER_MIND_API_KEY")
    DATABENTO_API_KEY = os.getenv("DATABENTO_API_KEY")  # Deprecated, kept for backward compatibility
    POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = "https://space.ai-builders.com/backend/v1"
    OPENAI_MODEL = "supermind-agent-v1"
    AI_BUILDER_API_BASE = "https://space.ai-builders.com/backend"
    
    # LLM Scoring Configuration
    # Set to True to use OpenAI GPT-5 for scoring (faster), False to use AI Builder API
    USE_OPENAI_FOR_SCORING = True  # Using OpenAI GPT-5-mini for scoring
    OPENAI_MODEL_FOR_SCORING = "gpt-5-mini"  # OpenAI model for scoring
    
    # Monitoring configuration
    MONITORED_TICKERS = ["TSLA"]
    PRICE_CHANGE_THRESHOLD = 0.005  # 0.5% threshold
    MONITORING_INTERVAL_HOURS = 1
    
    # Timezone
    TIMEZONE = "America/New_York"

