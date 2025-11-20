# Simple startup script for Vibe Search
# Uses password: postgres

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting Vibe Search" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:POSTGRES_PASSWORD = "postgres"
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DB_NAME = "vibe_search"
$env:DB_USER = "postgres"

Write-Host "Database Password: postgres" -ForegroundColor Yellow
Write-Host ""

# Check/Start Backend
Write-Host "Checking Backend..." -ForegroundColor Yellow
$backendRunning = netstat -ano | findstr ":8000"
if ($backendRunning) {
    Write-Host "OK Backend already running on port 8000" -ForegroundColor Green
} else {
    Write-Host "Starting Backend API..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:POSTGRES_PASSWORD='postgres'; `$env:DB_HOST='localhost'; `$env:DB_PORT='5432'; `$env:DB_NAME='vibe_search'; `$env:DB_USER='postgres'; cd '$PWD'; python run_server.py"
    Start-Sleep -Seconds 3
}

Write-Host ""

# Check/Start Frontend
Write-Host "Checking Frontend..." -ForegroundColor Yellow
$frontendRunning = netstat -ano | findstr ":3000"
if ($frontendRunning) {
    Write-Host "OK Frontend already running on port 3000" -ForegroundColor Green
} else {
    Write-Host "Starting Frontend..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"
    Start-Sleep -Seconds 3
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Project Starting..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services:" -ForegroundColor Green
Write-Host "  Backend:     http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Wait 10-15 seconds for services to start..." -ForegroundColor Yellow
Write-Host "Then open: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

