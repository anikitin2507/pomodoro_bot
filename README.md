# FocusTimerBot

Telegram-бот для техники Pomodoro, который помогает поддерживать фокус во время работы.

## Описание

FocusTimerBot позволяет:
- Запускать таймеры по технике Pomodoro
- Получать уведомления о начале и окончании рабочих интервалов и перерывов
- Отслеживать количество выполненных "помидоров" за день

Подробное описание требований можно найти в [PRD](docs/prd.md).

## Установка и запуск

### Локальная разработка

1. Клонировать репозиторий:
```bash
git clone https://github.com/yourusername/pomodoro_bot.git
cd pomodoro_bot
```

2. Создать и активировать виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate  # Windows
```

3. Установить зависимости:
```bash
pip install -e .
```

4. Создать файл `.env` в корне проекта:
```
TELEGRAM_TOKEN=your_telegram_token
DATABASE_URL=sqlite:///pomodoro.sqlite3
```

5. Запустить бота:
```bash
python -m app.main
```

## Лицензия

MIT 