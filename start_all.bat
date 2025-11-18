@echo off
echo ==========================================
echo Starting Vibe Search - Full Stack
echo ==========================================
echo.

echo Starting Backend API...
start "Vibe Search Backend" cmd /k "python run_server.py"

timeout /t 3 /nobreak >nul

echo Starting Frontend...
start "Vibe Search Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ==========================================
echo Servers Starting...
echo ==========================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Frontend:     http://localhost:3000
echo.
echo Two command windows will open:
echo   - One for Backend (Python/FastAPI)
echo   - One for Frontend (Next.js)
echo.
echo Wait for both to show 'Ready' messages
echo Then open http://localhost:3000 in your browser
echo.
pause

