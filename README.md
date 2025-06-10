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
git clone https://github.com/anikitin2507/pomodoro_bot.git
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

4. Создать файл `.env` в корне проекта на основе env.example:
```
TELEGRAM_TOKEN=your_telegram_token
DATABASE_URL=sqlite:///pomodoro.sqlite3
DEBUG=True
```

5. Запустить бота:
```bash
python -m app.main
```

### Деплой на Railway

1. Зарегистрируйтесь на [Railway](https://railway.app/)

2. Установите CLI Railway:
```bash
npm i -g @railway/cli
```

3. Войдите в свой аккаунт:
```bash
railway login
```

4. Создайте новый проект:
```bash
railway init
```

5. Добавьте переменную окружения:
```bash
railway variables set TELEGRAM_TOKEN=your_telegram_token
```
После генерации домена Railway автоматически задаст `RAILWAY_STATIC_URL`, из которой бот сформирует `WEBHOOK_URL`.

6. Разверните приложение:
```bash
railway up
```

Также можно настроить автоматический деплой при пуше в репозиторий GitHub, связав проект Railway с репозиторием в настройках.

## Лицензия

MIT 