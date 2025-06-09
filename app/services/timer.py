"""Timer service for the Pomodoro bot."""

import asyncio
import logging
from datetime import datetime, time
from typing import Dict, Optional, Tuple

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.config import config
from app.db.models import PomodoroSession, User, get_db_session

logger = logging.getLogger(__name__)

# Store active timers in memory (telegram_id -> (work_job, break_job))
active_timers: Dict[int, Tuple[Optional[asyncio.Task], Optional[asyncio.Task]]] = {}


class TimerService:
    """Service for managing Pomodoro timers."""

    def __init__(self):
        """Initialize the TimerService."""
        self.scheduler = AsyncIOScheduler()
        # Откладываем запуск планировщика до старта event loop
        self.is_scheduler_started = False
        
    def start_scheduler(self):
        """Start the scheduler when event loop is running."""
        if not self.is_scheduler_started:
            self.scheduler.start()
            # Schedule daily reset at midnight for each user's timezone
            self._schedule_daily_reset()
            self.is_scheduler_started = True

    def _schedule_daily_reset(self):
        """Schedule daily reset for all users at their midnight."""
        trigger = CronTrigger(hour=0, minute=0)  # Midnight
        self.scheduler.add_job(
            self._reset_daily_counters, trigger, id="daily_reset"
        )

    async def _reset_daily_counters(self):
        """Reset daily pomodoro counters for all users."""
        logger.info("Resetting daily pomodoro counters")
        for session in get_db_session():
            # Close all active sessions from yesterday
            yesterday_sessions = (
                session.query(PomodoroSession)
                .filter(PomodoroSession.end_time.is_(None))
                .all()
            )
            for pomodoro in yesterday_sessions:
                pomodoro.end_time = datetime.utcnow()
            session.commit()

    async def start_timer(
        self,
        update: Update,
        context: CallbackContext,
        work_minutes: int,
        break_minutes: int,
    ):
        """Start a Pomodoro timer.

        Args:
            update: Telegram update
            context: Callback context
            work_minutes: Duration of work period in minutes
            break_minutes: Duration of break period in minutes
        """
        user_id = update.effective_user.id

        # Cancel existing timer if any
        if user_id in active_timers:
            work_job, break_job = active_timers[user_id]
            if work_job and not work_job.done():
                work_job.cancel()
            if break_job and not break_job.done():
                break_job.cancel()

        # Create a new session in DB
        for session in get_db_session():
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                # Create user if not exists
                user = User(
                    telegram_id=user_id,
                    username=update.effective_user.username,
                    first_name=update.effective_user.first_name,
                    last_name=update.effective_user.last_name,
                )
                session.add(user)
                session.commit()
                session.refresh(user)

            # Create new pomodoro session
            pomodoro = PomodoroSession(
                user_id=user.id,
                work_minutes=work_minutes,
                break_minutes=break_minutes,
            )
            session.add(pomodoro)
            session.commit()
            # Store session id in context
            context.user_data["session_id"] = pomodoro.id

        # Send start message
        await update.effective_message.reply_text("⏱ Время работать!")

        # Schedule work and break tasks
        work_job = asyncio.create_task(
            self._work_timer(update, context, work_minutes, break_minutes)
        )
        active_timers[user_id] = (work_job, None)

    async def _work_timer(
        self,
        update: Update,
        context: CallbackContext,
        work_minutes: int,
        break_minutes: int,
    ):
        """Work timer task.

        Args:
            update: Telegram update
            context: Callback context
            work_minutes: Duration of work period in minutes
            break_minutes: Duration of break period in minutes
        """
        user_id = update.effective_user.id
        # Wait for work period to finish
        await asyncio.sleep(work_minutes * 60)

        # Increment completed pomodoro count
        session_id = context.user_data.get("session_id")
        if session_id:
            for session in get_db_session():
                pomodoro = session.query(PomodoroSession).get(session_id)
                if pomodoro:
                    pomodoro.completed += 1
                    session.commit()

        # Send break message with keyboard
        keyboard = [
            [
                InlineKeyboardButton("Пропустить ⏭", callback_data="skip_break"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await update.effective_message.reply_text(
            "✅ Пора на перерыв!", reply_markup=reply_markup
        )

        # Schedule break timer
        break_job = asyncio.create_task(
            self._break_timer(update, context, message.message_id, break_minutes)
        )
        active_timers[user_id] = (None, break_job)

    async def _break_timer(
        self,
        update: Update,
        context: CallbackContext,
        message_id: int,
        break_minutes: int,
    ):
        """Break timer task.

        Args:
            update: Telegram update
            context: Callback context
            message_id: ID of the break message
            break_minutes: Duration of break period in minutes
        """
        user_id = update.effective_user.id
        # Wait for break period to finish
        await asyncio.sleep(break_minutes * 60)

        # Send next round prompt
        keyboard = [
            [
                InlineKeyboardButton("Да ✅", callback_data="next_round_yes"),
                InlineKeyboardButton("Нет ❌", callback_data="next_round_no"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🚀 Следующий раунд?",
            reply_markup=reply_markup,
        )

        # Remove from active timers
        if user_id in active_timers:
            active_timers.pop(user_id)

    async def get_today_count(self, user_id: int) -> int:
        """Get the number of completed pomodoros for today.

        Args:
            user_id: Telegram user ID

        Returns:
            int: Number of completed pomodoros today
        """
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)

        count = 0
        for session in get_db_session():
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                return 0

            # Get completed pomodoros for today
            pomodoros = (
                session.query(PomodoroSession)
                .filter(
                    PomodoroSession.user_id == user.id,
                    PomodoroSession.start_time >= today_start,
                    PomodoroSession.start_time <= today_end,
                )
                .all()
            )
            count = sum(p.completed for p in pomodoros)

        return count

    async def skip_break(self, update: Update, context: CallbackContext):
        """Skip the break period and prompt for next round.

        Args:
            update: Telegram update
            context: Callback context
        """
        user_id = update.effective_user.id
        
        # Cancel break timer if active
        if user_id in active_timers:
            _, break_job = active_timers[user_id]
            if break_job and not break_job.done():
                break_job.cancel()

        # Remove inline keyboard
        await update.callback_query.edit_message_reply_markup(None)
        
        # Send next round prompt
        keyboard = [
            [
                InlineKeyboardButton("Да ✅", callback_data="next_round_yes"),
                InlineKeyboardButton("Нет ❌", callback_data="next_round_no"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🚀 Следующий раунд?",
            reply_markup=reply_markup,
        )
        
        # Remove from active timers
        if user_id in active_timers:
            active_timers.pop(user_id)


# Create a singleton instance
timer_service = TimerService() 