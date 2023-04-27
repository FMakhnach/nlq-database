@echo off

start "Application" cmd /c archie_venv\Scripts\python app.py
start "Telegram bot" cmd /c archie_venv\Scripts\python tg_bot.py