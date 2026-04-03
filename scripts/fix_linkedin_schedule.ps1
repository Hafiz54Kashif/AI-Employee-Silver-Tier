$taskName = "AIEmployee_LinkedInGenerator"
$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($task) {
    $task.Settings.StartWhenAvailable = $true
    Set-ScheduledTask -InputObject $task
    Write-Host "SUCCESS: LinkedIn Generator will now run even if PC was sleeping at 9 AM" -ForegroundColor Green
} else {
    Write-Host "Task '$taskName' not found. Running setup_scheduler.bat first..." -ForegroundColor Yellow
}
