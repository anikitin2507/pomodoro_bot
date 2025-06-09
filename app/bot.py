"""Bot initialization and configuration."""

import logging
import asyncio
import os
from typing import Optional
import time

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    Defaults,
)
from telegram.error import RetryAfter

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
        # First, delete any existing webhook
        await application.bot.delete_webhook()
        
        # Keep the program running until it's interrupted
        await application.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
        )
        await asyncio.Event().wait()  # Wait forever
    except KeyboardInterrupt:
        logger.info("Stopping bot due to keyboard interrupt")
    except Exception as e:
        logger.error(f"Error in polling: {e}", exc_info=True)
    finally:
        # Properly close the application
        try:
            await application.stop()
            await application.shutdown()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


async def run_webhook():
    """Run the bot with webhook (for production)."""
    # Всегда запускаем в режиме polling, если на Railway не настроен домен
    if not os.environ.get("RAILWAY_STATIC_URL"):
        logger.info("No RAILWAY_STATIC_URL environment variable, switching to polling mode")
        await run_polling()
        return
        
    # Если есть RAILWAY_STATIC_URL, используем его для webhook
    webhook_url = f"https://{os.environ.get('RAILWAY_STATIC_URL')}/webhook"
    logger.info(f"Using webhook URL: {webhook_url}")
        
    application = await create_application()
    
    try:
        # Start receiving updates
        await application.start()
        
        # Удаляем существующий webhook
        await application.bot.delete_webhook()
        await asyncio.sleep(1)  # Небольшая задержка
        
        # Устанавливаем новый webhook
        await application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
        
        # Запускаем webhook сервер
        await application.updater.start_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", "8080")),
            url_path="webhook",
            drop_pending_updates=True,
        )
        
        # Проверяем, что webhook установлен
        webhook_info = await application.bot.get_webhook_info()
        logger.info(f"Webhook info: {webhook_info.url}")
        
        # Ждем бесконечно
        await asyncio.Event().wait()
    except Exception as e:
        logger.error(f"Error in webhook mode: {e}", exc_info=True)
    finally:
        try:
            # Удаляем webhook перед выключением
            await application.bot.delete_webhook()
            # Останавливаем updater
            await application.updater.stop()
            # Останавливаем приложение
            await application.stop()
            # Завершаем приложение
            await application.shutdown()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}") 