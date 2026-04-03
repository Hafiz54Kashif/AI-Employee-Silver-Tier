@echo off
:: Self-elevate to Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ================================================
echo  Fixing LinkedIn Generator Schedule...
echo ================================================

powershell -ExecutionPolicy Bypass -Command "$task = Get-ScheduledTask -TaskName 'AIEmployee_LinkedInGenerator'; $task.Settings.StartWhenAvailable = $true; Set-ScheduledTask -InputObject $task; Write-Host 'DONE - Task updated successfully' -ForegroundColor Green"

echo.
echo Verifying...
schtasks /query /tn "AIEmployee_LinkedInGenerator" /fo LIST | findstr /i "start\|status\|next"

echo.
echo ================================================
echo  Fix complete! LinkedIn post will now run
echo  automatically even if PC was sleeping at 9 AM.
echo ================================================
pause
