@echo off
cd /d "%~dp0"
start /B pythonw watchers\gmail_watcher.py
timeout /t 2 /nobreak >nul
start /B pythonw watchers\linkedin_watcher.py
timeout /t 2 /nobreak >nul
start /B pythonw watchers\linkedin_scheduler.py
