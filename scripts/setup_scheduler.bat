@echo off
echo ================================================
echo   AI Employee - Task Scheduler Setup
echo ================================================

set PYTHON=C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\python.exe
set PROJECT=D:\Agentic AI\Assignments\AI_Employee_Project\AI_Employee_Project

echo Creating Gmail Watcher task...
schtasks /create /tn "AIEmployee_GmailWatcher" /tr "\"%PYTHON%\" \"%PROJECT%\watchers\gmail_watcher.py\"" /sc ONLOGON /rl HIGHEST /f
if %errorlevel%==0 (echo [OK] GmailWatcher created) else (echo [FAIL] GmailWatcher failed)

echo.
echo Creating Approval Watcher task...
schtasks /create /tn "AIEmployee_ApprovalWatcher" /tr "\"%PYTHON%\" \"%PROJECT%\watchers\approval_watcher.py\"" /sc ONLOGON /rl HIGHEST /f
if %errorlevel%==0 (echo [OK] ApprovalWatcher created) else (echo [FAIL] ApprovalWatcher failed)

echo.
echo Creating LinkedIn Watcher task (on login)...
schtasks /create /tn "AIEmployee_LinkedInWatcher" /tr "\"%PYTHON%\" \"%PROJECT%\watchers\linkedin_watcher.py\"" /sc ONLOGON /rl HIGHEST /f
if %errorlevel%==0 (echo [OK] LinkedInWatcher created) else (echo [FAIL] LinkedInWatcher failed)

echo.
echo Creating LinkedIn Content Generator task (daily 9:00 AM)...
schtasks /create /tn "AIEmployee_LinkedInGenerator" /tr "\"%PYTHON%\" \"%PROJECT%\watchers\linkedin_content_generator.py\"" /sc DAILY /st 09:00 /rl HIGHEST /f
if %errorlevel%==0 (echo [OK] LinkedInGenerator created - runs daily at 9:00 AM) else (echo [FAIL] LinkedInGenerator failed)

echo.
echo Creating Watchdog task (on login - monitors all watchers)...
schtasks /create /tn "AIEmployee_Watchdog" /tr "\"%PYTHON%\" \"%PROJECT%\watchers\watchdog.py\"" /sc ONLOGON /rl HIGHEST /f
if %errorlevel%==0 (echo [OK] Watchdog created - auto-restarts crashed watchers) else (echo [FAIL] Watchdog failed)

echo.
echo Creating CEO Briefing task (every Sunday 11:00 PM)...
schtasks /create /tn "AIEmployee_CEOBriefing" /tr "\"%PYTHON%\" \"%PROJECT%\watchers\ceo_briefing_generator.py\"" /sc WEEKLY /d SUN /st 23:00 /rl HIGHEST /f
if %errorlevel%==0 (echo [OK] CEOBriefing created - runs every Sunday at 11:00 PM) else (echo [FAIL] CEOBriefing failed)

echo.
echo ================================================
echo Verifying tasks...
schtasks /query /tn "AIEmployee_GmailWatcher" >nul 2>&1 && echo [EXISTS] AIEmployee_GmailWatcher || echo [MISSING] AIEmployee_GmailWatcher
schtasks /query /tn "AIEmployee_ApprovalWatcher" >nul 2>&1 && echo [EXISTS] AIEmployee_ApprovalWatcher || echo [MISSING] AIEmployee_ApprovalWatcher
schtasks /query /tn "AIEmployee_LinkedInWatcher" >nul 2>&1 && echo [EXISTS] AIEmployee_LinkedInWatcher || echo [MISSING] AIEmployee_LinkedInWatcher
schtasks /query /tn "AIEmployee_LinkedInGenerator" >nul 2>&1 && echo [EXISTS] AIEmployee_LinkedInGenerator (Daily 9AM) || echo [MISSING] AIEmployee_LinkedInGenerator
schtasks /query /tn "AIEmployee_Watchdog" >nul 2>&1 && echo [EXISTS] AIEmployee_Watchdog (On Login) || echo [MISSING] AIEmployee_Watchdog
schtasks /query /tn "AIEmployee_CEOBriefing" >nul 2>&1 && echo [EXISTS] AIEmployee_CEOBriefing (Sunday 11PM) || echo [MISSING] AIEmployee_CEOBriefing

echo.
echo Done! All AI Employee tasks scheduled.
echo Open Task Scheduler to verify.
echo ================================================
pause
