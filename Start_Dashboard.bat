@echo off
echo ========================================
echo    AI Employee — Starting...
echo ========================================
cd /d "%~dp0"
pip install flask -q 2>nul
start http://localhost:5000
python dashboard/app.py
