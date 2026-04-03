# AI Employee - Windows Task Scheduler Setup
# Run this as Administrator

$genBat = "D:\Agentic AI\Assignments\AI_Employee_Project\AI_Employee_Project\scripts\run_linkedin_generator.bat"
$watchBat = "D:\Agentic AI\Assignments\AI_Employee_Project\AI_Employee_Project\scripts\run_linkedin_watcher.bat"
$gmailBat = "D:\Agentic AI\Assignments\AI_Employee_Project\AI_Employee_Project\scripts\run_gmail_watcher.bat"
$approvalBat = "D:\Agentic AI\Assignments\AI_Employee_Project\AI_Employee_Project\scripts\run_approval_watcher.bat"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  AI Employee - Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# 1. LinkedIn Content Generator - Daily 9 AM
Write-Host "`nCreating LinkedIn Generator (Daily 9:00 AM)..."
schtasks /create /tn "AIEmployee_LinkedInGenerator" /tr "`"$genBat`"" /sc DAILY /st 09:00 /f
if ($LASTEXITCODE -eq 0) { Write-Host "[OK] LinkedInGenerator - runs every day at 9:00 AM" -ForegroundColor Green }
else { Write-Host "[FAIL] LinkedInGenerator" -ForegroundColor Red }

# 2. LinkedIn Watcher - On Login
Write-Host "`nCreating LinkedIn Watcher (On Login)..."
schtasks /create /tn "AIEmployee_LinkedInWatcher" /tr "`"$watchBat`"" /sc ONLOGON /f
if ($LASTEXITCODE -eq 0) { Write-Host "[OK] LinkedInWatcher - starts on Windows login" -ForegroundColor Green }
else { Write-Host "[FAIL] LinkedInWatcher" -ForegroundColor Red }

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "Verifying..." -ForegroundColor Cyan
schtasks /query /tn "AIEmployee_LinkedInGenerator" | Select-String "Next Run"
schtasks /query /tn "AIEmployee_LinkedInWatcher" | Select-String "Status"

Write-Host "`nDone! LinkedIn will auto-post every day at 9:00 AM." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Read-Host "Press Enter to close"
