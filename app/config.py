"""Configuration module for the Pomodoro bot."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Configuration class for the Pomodoro bot."""

    # Telegram Bot Token
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable is not set")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///pomodoro.sqlite3")

    # Webhook settings (for production)
    WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL")
    RAILWAY_STATIC_URL: Optional[str] = os.getenv("RAILWAY_STATIC_URL")
    WEBHOOK_PORT: int = int(os.getenv("PORT", "8443"))

    # Construct webhook URL from Railway domain if needed
    if not WEBHOOK_URL and RAILWAY_STATIC_URL:
        WEBHOOK_URL = f"https://{RAILWAY_STATIC_URL}/webhook"

    # Default Pomodoro settings
    DEFAULT_WORK_MINUTES: int = 25
    DEFAULT_BREAK_MINUTES: int = 5

    # Development mode
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")


config = Config() 