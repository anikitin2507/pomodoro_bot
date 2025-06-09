"""Command handlers for the Pomodoro bot."""

import logging
import re
from typing import Tuple, Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.config import config
from app.services.timer import timer_service

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: CallbackContext) -> None:
    """Handle the /start command."""
    keyboard = [
        [
            InlineKeyboardButton("25 / 5", callback_data="preset_25_5"),
            InlineKeyboardButton("50 / 10", callback_data="preset_50_10"),
        ],
        [InlineKeyboardButton("Свой вариант", callback_data="custom")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"Привет, {update.effective_user.first_name}! 👋\n\n"
        "Я помогу тебе сосредоточиться на работе с помощью техники Pomodoro.\n\n"
        "Выбери длительность рабочего периода и перерыва в минутах или используй "
        "команду /pomodoro <работа> <перерыв> (например, /pomodoro 25 5)."
    )

    await update.effective_message.reply_text(welcome_text, reply_markup=reply_markup)


async def help_handler(update: Update, context: CallbackContext) -> None:
    """Handle the /help command."""
    help_text = (
        "🍅 *FocusTimerBot* — бот для техники Pomodoro\n\n"
        "*Доступные команды:*\n"
        "/start - Начать работу с ботом\n"
        "/pomodoro <работа> <перерыв> - Запустить таймер с указанной длительностью в минутах\n"
        "/today - Показать количество выполненных помидоров за сегодня\n"
        "/help - Показать эту справку\n\n"
        "*Примеры:*\n"
        "/pomodoro 25 5 - Запустить таймер с 25 минутами работы и 5 минутами перерыва\n"
        "/pomodoro 50 10 - Запустить таймер с 50 минутами работы и 10 минутами перерыва"
    )

    await update.effective_message.reply_text(
        help_text, parse_mode="Markdown"
    )


def parse_pomodoro_args(args: list) -> Tuple[int, int]:
    """Parse arguments for the pomodoro command.

    Returns:
        tuple: (work_minutes, break_minutes)
    """
    work_minutes = config.DEFAULT_WORK_MINUTES
    break_minutes = config.DEFAULT_BREAK_MINUTES

    if len(args) >= 1:
        try:
            work_minutes = int(args[0])
            if work_minutes <= 0:
                raise ValueError("Work minutes must be positive")
        except ValueError:
            # Use default if conversion fails
            pass

    if len(args) >= 2:
        try:
            break_minutes = int(args[1])
            if break_minutes <= 0:
                raise ValueError("Break minutes must be positive")
        except ValueError:
            # Use default if conversion fails
            pass

    return work_minutes, break_minutes


async def pomodoro_handler(update: Update, context: CallbackContext) -> None:
    """Handle the /pomodoro command."""
    # Parse arguments
    work_minutes, break_minutes = parse_pomodoro_args(context.args)

    # Start timer
    await timer_service.start_timer(update, context, work_minutes, break_minutes)


async def today_handler(update: Update, context: CallbackContext) -> None:
    """Handle the /today command."""
    user_id = update.effective_user.id
    count = await timer_service.get_today_count(user_id)

    # Use appropriate emoji and message based on count
    if count == 0:
        emoji = "😔"
        message = "У тебя пока нет выполненных помидоров сегодня."
    elif count < 4:
        emoji = "🙂"
        message = f"У тебя {count} {'помидор' if count == 1 else 'помидора'} сегодня. Хорошее начало!"
    elif count < 8:
        emoji = "😊"
        message = f"У тебя {count} помидоров сегодня. Отличный прогресс!"
    else:
        emoji = "🔥"
        message = f"У тебя {count} помидоров сегодня. Вау, супер продуктивный день!"

    await update.effective_message.reply_text(f"{emoji} {message}")


async def callback_handler(update: Update, context: CallbackContext) -> None:
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()  # Answer to remove the loading state

    data = query.data

    # Handle preset timers
    if data.startswith("preset_"):
        # Extract minutes from preset_X_Y format
        match = re.match(r"preset_(\d+)_(\d+)", data)
        if match:
            work_minutes = int(match.group(1))
            break_minutes = int(match.group(2))
            await timer_service.start_timer(update, context, work_minutes, break_minutes)
            # Remove the inline keyboard
            await query.edit_message_reply_markup(None)
            return

    # Handle custom timer request
    if data == "custom":
        custom_text = (
            "Введите команду в формате:\n"
            "/pomodoro <работа> <перерыв>\n\n"
            "Например: /pomodoro 30 7"
        )
        await query.edit_message_text(text=custom_text)
        return

    # Handle skip break
    if data == "skip_break":
        await timer_service.skip_break(update, context)
        return

    # Handle next round
    if data == "next_round_yes":
        # Get the previous session parameters
        session_id = context.user_data.get("session_id")
        work_minutes = config.DEFAULT_WORK_MINUTES
        break_minutes = config.DEFAULT_BREAK_MINUTES

        # If we have a previous session, use its parameters
        if session_id:
            from app.db.models import PomodoroSession, get_db_session
            for session in get_db_session():
                pomodoro = session.query(PomodoroSession).get(session_id)
                if pomodoro:
                    work_minutes = pomodoro.work_minutes
                    break_minutes = pomodoro.break_minutes

        # Start a new timer with the same parameters
        await timer_service.start_timer(update, context, work_minutes, break_minutes)
        # Remove the inline keyboard
        await query.edit_message_reply_markup(None)
        return

    # Handle end session
    if data == "next_round_no":
        await query.edit_message_text(
            text="Сессия завершена. Отдохни и возвращайся, когда будешь готов!"
        )
        return 