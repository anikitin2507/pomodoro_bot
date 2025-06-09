# FocusTimerBot — Product Requirements Document (MVP v1.0)

## 1. Overview / Problem
Knowledge-work distractions make it hard to maintain deep focus. Users want a friction-free way—directly in Telegram—to start a Pomodoro timer, receive timely reminders, and track how many “pomodoros” they complete per day.

## 2. Key User Flows
1. **Start & Configure**  
   - User sends `/start` or adds the bot in DM.  
   - Bot replies with inline-keyboard presets (25 / 5, 50 / 10, Custom) and explains the `/pomodoro <work> <break>` command for custom lengths.  
2. **Run Session**  
   - Upon selection (e.g. tapping “25 / 5” or sending `/pomodoro 25 5`), bot stores durations, sends **“⏱ Время работать!”** and starts the timer.  
3. **Break Notification**  
   - After *work* duration, bot sends **“✅ Пора на перерыв!”**.  
4. **Next-Round Prompt**  
   - After *break* duration, bot asks **“🚀 Следующий раунд?”** with **Yes / No** buttons.  
   - **Yes** repeats the flow; **No** ends the cycle.  
5. **Daily Counter**  
   - Each completed work period increments today’s pomodoro count.  
   - `/today` shows count; resets automatically at midnight user-timezone.

## 3. Functional Requirements
| ID | Requirement |
|----|-------------|
|F-1|Slash command `/pomodoro <work> <break>` accepts integers (minutes). Defaults: 25 / 5.|
|F-2|Inline-keyboard presets for quick selection.|
|F-3|Store active timer per user; support concurrent users (DM only).|
|F-4|Send three notification messages per cycle (start, break, next-round prompt).|
|F-5|Persist daily pomodoro count in lightweight storage (SQLite or Railway PostgreSQL).|
|F-6|Reset counts at 00:00 local user time (lib: `pytz`, `apscheduler`).|
|F-7|Commands: `/start`, `/pomodoro`, `/today`, `/help`.|
|F-8|Error handling for invalid inputs and overlapping timers.|

### v1.1 (post-MVP)
| ID | Additional Feature |
|----|--------------------|
|F-9|Auto-start next round when user toggles `/autonext on/off`.|
|F-10|`/stats` — bar chart of pomodoros for the last 7 days.|

## 4. Non-Goals
- Group-chat usage or multi-user sessions.  
- Long-running stats beyond 7 days.  
- Detailed analytics, sound alerts, or desktop apps.  
- Localization beyond Russian + basic English.

## 5. Milestones & Release Plan
| Date*| Milestone |
|------|-----------|
|Day 0|Repo & CI/CD: GitHub repo, Poetry setup, Railway deployment pipeline.|
|Day 0|Telegram Webhook & basic `/start` reply live.|
|Day 0 → Evening|Implement F-1 – F-8, manual test with personal chat.|
|Tonight (EOD)|**Release v1.0** to production.|
|+5 days|Add F-9, F-10; verify with test users.|
|+7 days|**Release v1.1**.|

\*Dates relative to project kick-off (June 10 2025).
