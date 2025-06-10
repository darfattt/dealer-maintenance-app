@echo off
echo.
echo ========================================
echo   🚀 Dealer Dashboard Split Architecture
echo ========================================
echo.

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Create logs directory
if not exist logs mkdir logs

echo 🔨 Building and starting services...
echo.

REM Start with main compose file (split architecture)
docker-compose up -d --build

echo.
echo ⏳ Waiting for services to start...
timeout /t 15 /nobreak >nul

echo.
echo 🔍 Checking service status...

REM Check PostgreSQL
docker-compose exec -T postgres pg_isready -U dealer_user >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL is ready
) else (
    echo ❌ PostgreSQL is not ready
)

REM Check Redis
docker-compose exec -T redis redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis is ready
) else (
    echo ❌ Redis is not ready
)

echo.
echo 🎉 Dealer Dashboard Split Architecture is starting up!
echo.
echo 📊 Analytics Dashboard: http://localhost:8501
echo ⚙️ Admin Panel: http://localhost:8502
echo 🔧 API Docs: http://localhost:8000/docs
echo 📈 API Health: http://localhost:8000/health
echo.
echo 📋 Usage Instructions:
echo   1. Analytics: Open http://localhost:8501 for charts and metrics
echo   2. Admin: Open http://localhost:8502 for dealer management
echo   3. Use Admin Panel to add dealers and run jobs
echo   4. View Analytics Dashboard for real-time data visualization
echo   5. Both services work independently
echo.
echo 📋 To view logs: docker-compose logs -f [service_name]
echo 🛑 To stop: docker-compose down
echo.

REM Wait a bit more and then test
echo ⏳ Testing application...
timeout /t 10 /nobreak >nul

REM Try to test the application
python tests\test_app.py 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Python test script failed. You can still access the dashboard manually.
    echo    Dashboard: http://localhost:8501
)

echo.
echo 🚀 Split Architecture is ready! Press any key to open dashboards...
pause >nul

REM Try to open both dashboards
start http://localhost:8501
timeout /t 2 /nobreak >nul
start http://localhost:8502

echo.
echo Application is running. Press any key to exit...
pause >nul
