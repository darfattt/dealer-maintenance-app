@echo off
echo.
echo ========================================
echo   🚀 Dealer Dashboard - Split Architecture
echo ========================================
echo.
echo 📊 Analytics Dashboard: Port 8501 (Direct DB)
echo ⚙️ Admin Panel: Port 8502 (API-based)
echo 🔧 Backend API: Port 8000
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
pip install -r requirements.txt >nul 2>&1
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
timeout /t 15 /nobreak >nul

echo.
echo 📊 Setting up development data...
python insert_sample_data.py more >nul 2>&1

echo.
echo 🚀 Starting split services...
echo.
echo 📋 Services will start in separate windows:
echo   - Backend API (Port 8000)
echo   - Celery Worker
echo   - Analytics Dashboard (Port 8501) - Direct DB
echo   - Admin Panel (Port 8502) - API-based
echo.

REM Start Backend API in new window
start "Backend API" cmd /k "echo Starting Backend API (Port 8000)... && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start Celery Worker in new window
start "Celery Worker" cmd /k "echo Starting Celery Worker... && celery -A celery_app worker --loglevel=info"

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start Analytics Dashboard in new window
start "Analytics Dashboard" cmd /k "echo Starting Analytics Dashboard (Port 8501)... && streamlit run dashboard_analytics.py --server.port 8501 --server.address 0.0.0.0"

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start Admin Panel in new window
start "Admin Panel" cmd /k "echo Starting Admin Panel (Port 8502)... && streamlit run admin_app.py --server.port 8502 --server.address 0.0.0.0"

echo.
echo 🎉 Split architecture is starting!
echo.
echo 🌐 Access URLs:
echo   📊 Analytics Dashboard: http://localhost:8501
echo   ⚙️ Admin Panel: http://localhost:8502
echo   🔧 Backend API: http://localhost:8000/docs
echo   📈 API Health: http://localhost:8000/health
echo.
echo 🏗️ Architecture:
echo   📊 Analytics Dashboard (8501) → Direct DB Connection
echo   ⚙️ Admin Panel (8502) → Backend API (8000) → Database
echo   🔄 Celery Worker → Background Jobs → Database
echo.
echo 📋 Default Dealer:
echo   ID: 00999
echo   Name: Default Dealer
echo   Sample Data: 20+ prospect records
echo.
echo 💡 Usage:
echo   1. Analytics Dashboard: View charts and metrics
echo   2. Admin Panel: Manage dealers, run jobs, view history
echo   3. Both services work independently
echo.
echo 🛑 To stop: Close all service windows and run:
echo    docker stop postgres redis
echo    docker rm postgres redis
echo.

REM Wait and then try to open browsers
echo ⏳ Waiting for services to fully start...
timeout /t 20 /nobreak >nul

echo 🌐 Opening dashboards in browser...
start http://localhost:8501
timeout /t 2 /nobreak >nul
start http://localhost:8502

echo.
echo ✅ Split architecture is ready!
echo Press any key to exit this window...
pause >nul
