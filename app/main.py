"""Main entry point for the Pomodoro bot application."""

import asyncio
import logging

from app.bot import run_polling, run_webhook
from app.config import config

logger = logging.getLogger(__name__)


async def main():
    """Start the bot application."""
    logger.info("Starting Pomodoro bot...")

    # Use polling in debug mode, webhook in production
    if config.DEBUG or not config.WEBHOOK_URL:
        logger.info("Starting in polling mode")
        await run_polling()
    else:
        logger.info("Starting in webhook mode")
        await run_webhook()


if __name__ == "__main__":
    asyncio.run(main()) 