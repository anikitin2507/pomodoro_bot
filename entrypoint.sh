#!/bin/bash
set -e

echo "Starting Pomodoro Bot..."

# Trap signals and pass them to the Python process
trap 'kill -TERM $PID' TERM INT

# Start the bot
python -m app.main &
PID=$!

# Wait for the process to finish
wait $PID
trap - TERM INT
wait $PID
EXIT_STATUS=$?

echo "Bot exited with status $EXIT_STATUS"
exit $EXIT_STATUS 