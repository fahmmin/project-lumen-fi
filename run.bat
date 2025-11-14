@echo off
REM PROJECT LUMEN - Windows Quick Start Script

echo 🔆 PROJECT LUMEN - Starting System...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv\.installed" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo installed > venv\.installed
)

REM Check for .env file
if not exist ".env" (
    echo ⚠️  No .env file found. Creating from .env.example...
    copy .env.example .env
    echo 📝 Please edit .env with your configuration (especially OPENAI_API_KEY)
    echo.
)

REM Start backend
echo 🚀 Starting FastAPI backend...
start "LUMEN Backend" cmd /k "cd backend && python main.py"

timeout /t 3 /nobreak > nul

REM Start frontend
echo 🎨 Starting frontend server...
start "LUMEN Frontend" cmd /k "cd frontend && python -m http.server 3000"

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ✅ PROJECT LUMEN is running!
echo.
echo 📡 API: http://localhost:8000
echo 📚 Docs: http://localhost:8000/docs
echo 🌐 UI: http://localhost:3000
echo.
echo Close the command windows to stop services
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

pause
