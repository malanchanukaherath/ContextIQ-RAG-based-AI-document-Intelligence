@echo off
echo Starting RAG Application...
echo.

echo [1/2] Starting Backend Server on port 8000...
start "RAG Backend" cmd /k "cd /d %~dp0 && uv run uvicorn main:app --reload"
timeout /t 3 >nul

echo [2/2] Starting Frontend Server on port 3000...
start "RAG Frontend" cmd /k "cd /d %~dp0frontend && npm start"

echo.
echo ================================
echo RAG Application Started!
echo ================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo ================================
echo.
echo Press any key to close this window...
pause >nul
