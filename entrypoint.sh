#!/bin/bash
set -e

echo "Starting Pomodoro Bot..."
# Используем Python для запуска приложения через asyncio
python -c "import asyncio; from app.main import main; asyncio.run(main())" 