# Start both backend and frontend servers
# This script starts both servers in separate windows

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting Vibe Search - Full Stack" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if backend is already running
$backendRunning = netstat -ano | findstr ":8000" | Out-String
if ($backendRunning) {
    Write-Host "Backend already running on port 8000" -ForegroundColor Yellow
} else {
    Write-Host "Starting Backend API..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python run_server.py"
    Start-Sleep -Seconds 3
}

# Check if frontend is already running
$frontendRunning = netstat -ano | findstr ":3000" | Out-String
if ($frontendRunning) {
    Write-Host "Frontend already running on port 3000" -ForegroundColor Yellow
} else {
    Write-Host "Starting Frontend..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"
    Start-Sleep -Seconds 3
}

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Servers Starting..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Frontend:     http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Two new PowerShell windows will open:" -ForegroundColor Yellow
Write-Host "  - One for Backend (Python/FastAPI)" -ForegroundColor Yellow
Write-Host "  - One for Frontend (Next.js)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Wait for both to show 'Ready' messages" -ForegroundColor Yellow
Write-Host "Then open http://localhost:3000 in your browser" -ForegroundColor Cyan
Write-Host ""

