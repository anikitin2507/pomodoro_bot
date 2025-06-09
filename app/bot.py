"""Bot initialization and configuration."""

import logging
from typing import Optional

from telegram.ext import (
    Application,
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

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
)
logger = logging.getLogger(__name__)


def create_application() -> Application:
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
        Application.builder().token(config.TELEGRAM_TOKEN).defaults(defaults).build()
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("pomodoro", pomodoro_handler))
    application.add_handler(CommandHandler("today", today_handler))
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Log successful setup
    logger.info("Bot initialized successfully")

    return application


def run_polling(application: Optional[Application] = None) -> None:
    """Run the bot with polling (for development).

    Args:
        application: Preconfigured application instance or None to create a new one
    """
    if application is None:
        application = create_application()

    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )


def run_webhook(application: Optional[Application] = None) -> None:
    """Run the bot with webhook (for production).

    Args:
        application: Preconfigured application instance or None to create a new one
    """
    if application is None:
        application = create_application()

    if not config.WEBHOOK_URL:
        logger.error("WEBHOOK_URL is not set, cannot start webhook mode")
        return

    application.run_webhook(
        listen="0.0.0.0",
        port=config.WEBHOOK_PORT,
        webhook_url=config.WEBHOOK_URL,
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    ) 