@echo off
echo.
echo ========================================
echo   🚀 Dealer Dashboard - Development Mode
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

echo ✅ Python is available
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo 🐳 Starting external services...

REM Start PostgreSQL
echo Starting PostgreSQL...
docker run -d --name postgres -p 5432:5432 -e POSTGRES_DB=dealer_dashboard -e POSTGRES_USER=dealer_user -e POSTGRES_PASSWORD=dealer_pass postgres:15-alpine >nul 2>&1

REM Start Redis
echo Starting Redis...
docker run -d --name redis -p 6379:6379 redis:7-alpine >nul 2>&1

echo.
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

echo.
echo 📊 Setting up development data...
python dev_setup.py
if %errorlevel% neq 0 (
    echo ❌ Failed to setup development data
    pause
    exit /b 1
)

echo.
echo 🚀 Starting development services...
echo.
echo 📋 Services will start in separate windows:
echo   - Backend API (Port 8000)
echo   - Celery Worker
echo   - Streamlit Dashboard (Port 8501)
echo.

REM Start Backend API in new window
start "Backend API" cmd /k "echo Starting Backend API... && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start Celery Worker in new window
start "Celery Worker" cmd /k "echo Starting Celery Worker... && celery -A celery_app worker --loglevel=info"

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start Dashboard in new window
start "Dashboard" cmd /k "echo Starting Dashboard... && streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0"

echo.
echo 🎉 Development environment is starting!
echo.
echo 🌐 Access URLs:
echo   📊 Dashboard: http://localhost:8501
echo   🔧 API Docs: http://localhost:8000/docs
echo   📈 API Health: http://localhost:8000/health
echo.
echo 🏢 Default Dealer:
echo   ID: 00999
echo   Name: Default Dealer
echo.
echo 📋 Usage Instructions:
echo   1. Wait for all services to start (2-3 minutes)
echo   2. Open http://localhost:8501 in your browser
echo   3. Go to "Dashboard" to see dummy data
echo   4. Use "Run Jobs" to test data fetching
echo   5. Check "Job History" for execution logs
echo.
echo 🛑 To stop: Close all service windows and run:
echo    docker stop postgres redis
echo    docker rm postgres redis
echo.

REM Wait and then try to open browser
echo ⏳ Waiting for services to fully start...
timeout /t 15 /nobreak >nul

echo 🌐 Opening dashboard in browser...
start http://localhost:8501

echo.
echo ✅ Development environment is ready!
echo Press any key to exit this window...
pause >nul
