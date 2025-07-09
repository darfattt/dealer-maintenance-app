@echo off
echo.
echo ========================================
echo   📊 Dealer Dashboard Platform Status
echo ========================================
echo.

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

echo 🔍 Service Status:
echo.

REM Check each service
echo 📦 Infrastructure:
docker-compose ps postgres redis 2>nul
echo.

echo 🔧 Backend Services:
docker-compose ps backend celery_worker celery_beat 2>nul
echo.

echo 🌐 Microservices:
docker-compose ps account_service api_gateway dashboard_dealer_service 2>nul
echo.

echo 🎨 Frontend Applications:
docker-compose ps web_app analytics_dashboard admin_panel 2>nul
echo.

echo 📈 Monitoring:
docker-compose ps prometheus grafana 2>nul
echo.

echo 🌐 Service Health Checks:
echo.

REM Health checks
curl -f http://localhost:5000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Web App: http://localhost:5000
) else (
    echo ❌ Web App: http://localhost:5000
)

curl -f http://localhost:8080/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API Gateway: http://localhost:8080
) else (
    echo ❌ API Gateway: http://localhost:8080
)

curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API: http://localhost:8000
) else (
    echo ❌ Backend API: http://localhost:8000
)

curl -f http://localhost:8501 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Analytics: http://localhost:8501
) else (
    echo ❌ Analytics: http://localhost:8501
)

curl -f http://localhost:8502 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Admin Panel: http://localhost:8502
) else (
    echo ❌ Admin Panel: http://localhost:8502
)

curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Grafana: http://localhost:3000
) else (
    echo ❌ Grafana: http://localhost:3000
)

echo.
echo 📋 Quick Actions:
echo   📋 View all logs: docker-compose logs -f
echo   🔄 Restart all: docker-compose restart
echo   🛑 Stop all: docker-compose down
echo.

pause
