### Как пользоваться планом
Каждый пункт помечен статусом (`TODO` / `DONE`). Начинайте работу с первого невыполненного пункта.

---

## Milestone 1 — Repository Bootstrap & Local Dev Setup
- TODO: Инициализировать Git-репозиторий и сделать **первый коммит** пустой структуры.  
- TODO: Создать файл **.gitignore** (до первого коммита!) и внести в него `*.env`, `__pycache__/`, `.pytest_cache/`, `*.sqlite3`, `*.log`.  
- TODO: Сгенерировать **pyproject.toml** c Poetry; добавить зависимости: `python-telegram-bot==23.*`, `SQLAlchemy==2.*`, `python-dotenv==1.*`, `asyncpg==0.*`.  
- TODO: Сформировать базовую структуру каталогов в соответствии с *file_structure_document.mdc*.  
- TODO: Добавить **README.md** с краткой установкой и ссылкой на PRD.  

## Milestone 2 — Core Bot Functionality
- TODO: Реализовать `app/config.py` для загрузки переменных окружения через **python-dotenv**.  
- TODO: Написать `app/bot.py` без `asyncio.run()`; использовать `Application.run_polling()` от python-telegram-bot.  
- TODO: Добавить хендлеры `/start`, `/help`, `/pomodoro`, `/today` в `app/handlers/`.  
- TODO: Создать `app/services/timer.py` с логикой Pomodoro и ежедневным сбросом счётчика (apscheduler).  
- TODO: Описать ORM-модели `User`, `PomodoroSession` в `app/db/models.py`; настроить миграции.  
- TODO: Добавить обработку ошибок для перекрывающихся таймеров и неверных аргументов.  

## Milestone 3 — Containerisation & Deployment
- TODO: Создать **Dockerfile** (python:3.12-slim) с корректным порядком команд:  
  1. `COPY pyproject.toml ./`  
  2. `COPY app/ ./app/`  
  3. `RUN pip install --no-cache-dir -e .`  
- TODO: Добавить **.dockerignore** (исключить tests, docs, .git, *.env).  
- TODO: Настроить Railway проект, добавить переменные окружения и webhook URL.  
- TODO: Подготовить GitHub Workflow для CI (lint, tests) и CD на Railway.  

## Milestone 4 — Quality Assurance & Docs
- TODO: Настроить **ruff** и **black** в `[tool]` секциях pyproject; добавить pre-commit.  
- TODO: Написать unit-тесты для сервисов и хендлеров в `tests/`; добиться покрытия ≥ 80 %.  
- TODO: Добавить badges (CI, codecov) в README.  
- TODO: Обновить документацию в `docs/` (описание API, переменных окружения).  

---

## Acceptance Checklist
- [ ] Бот деплоится на Railway последним пайплайном без ошибок.  
- [ ] Команды `/pomodoro` и `/today` работают в личном чате.  
- [ ] Счётчик помидоров сбрасывается в полночь по локальному времени пользователя.  
- [ ] Все тесты проходят; покрытие ≥ 80 %.  
- [ ] Ruff и Black не обнаруживают ошибок при `pre-commit run --all-files`.  
- [ ] docker image собирается < 200 MB и стартует без root.  

---

**@Cursor**: После завершения задачи поменяй её статус на DONE и добавь краткий маркер «// done by Cursor» с описанием, что именно сделано.
