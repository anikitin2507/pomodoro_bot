"""Bot initialization and configuration."""

import logging
import asyncio
from typing import Optional

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    Defaults,
)

from app.config import config
from app.db.models import init_db
from app.handlers import (
    callback_handler,
    help_handler,
    pomodoro_handler,
    start_handler,
    today_handler,
)
from app.services.timer import timer_service

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
)
logger = logging.getLogger(__name__)


async def create_application():
    """Create and configure the bot application.

    Returns:
        Application: Configured application instance
    """
    # Initialize database
    init_db()
    
    # Configure default behavior
    defaults = Defaults(
        parse_mode=None,
        disable_notification=False,
        disable_web_page_preview=True,
    )

    # Create application
    application = (
        ApplicationBuilder().token(config.TELEGRAM_TOKEN).defaults(defaults).build()
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("pomodoro", pomodoro_handler))
    application.add_handler(CommandHandler("today", today_handler))
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Start the scheduler
    timer_service.start_scheduler()
    
    # Initialize the application
    await application.initialize()
    
    # Log successful setup
    logger.info("Bot initialized successfully")

    return application


async def run_polling():
    """Run the bot with polling (for development)."""
    application = await create_application()
    
    # Start receiving updates
    await application.start()
    
    try:
        # Keep the program running until it's interrupted
        await application.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
        )
        await asyncio.Event().wait()  # Wait forever
    finally:
        # Properly close the application
        await application.stop()
        await application.shutdown()


async def run_webhook():
    """Run the bot with webhook (for production)."""
    if not config.WEBHOOK_URL:
        logger.error("WEBHOOK_URL is not set, cannot start webhook mode")
        return
        
    application = await create_application()
    
    # Start receiving updates
    await application.start()
    
    try:
        # Start webhook server
        url_path = config.WEBHOOK_URL.split("/")[-1] if config.WEBHOOK_URL.endswith("/webhook") else "webhook"
        
        base_url = "/".join(config.WEBHOOK_URL.split("/")[:-1]) if url_path != "webhook" else config.WEBHOOK_URL
        
        logger.info(f"Starting webhook with URL path: {url_path} on port {config.WEBHOOK_PORT}")
        
        # Run the webhook server
        await application.updater.start_webhook(
            listen="0.0.0.0",
            port=config.WEBHOOK_PORT,
            url_path=url_path,
            webhook_url=config.WEBHOOK_URL,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
        )
        
        # Setup webhook
        await application.bot.set_webhook(url=config.WEBHOOK_URL)
        
        # Check webhook info
        webhook_info = await application.bot.get_webhook_info()
        logger.info(f"Webhook is set to: {webhook_info.url}")
        
        await asyncio.Event().wait()  # Wait forever
    finally:
        # Properly close the application
        await application.stop()
        await application.shutdown() 