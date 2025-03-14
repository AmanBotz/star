#!/bin/bash
# Start the Flask health server on port 8000 in the background.
python health.py &
# Start the Telegram bot.
python bot.py
