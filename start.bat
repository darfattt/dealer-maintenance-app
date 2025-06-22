@echo off
echo.
echo ========================================
echo   🚀 Dealer Dashboard Full Stack Platform
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
echo   📦 Database & Cache (PostgreSQL, Redis)
echo   🔧 Backend Services (FastAPI, Celery)
echo   🌐 Microservices (Account, API Gateway, Dashboard)
echo   🎨 Frontend (Vue.js Web App)
echo   📊 Analytics (Streamlit Dashboards)
echo   📈 Monitoring (Prometheus, Grafana)
echo.

REM Start with main compose file (full architecture)
docker-compose up -d --build

echo.
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

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

REM Check API Gateway
curl -f http://localhost:8080/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API Gateway is ready
) else (
    echo ❌ API Gateway is not ready
)

REM Check Web App
curl -f http://localhost:5000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Web Application is ready
) else (
    echo ❌ Web Application is not ready
)

echo.
echo 🎉 Dealer Dashboard Full Stack Platform is ready!
echo.
echo 🌐 MAIN APPLICATIONS:
echo   🎨 Web Dashboard: http://localhost:5000
echo   📊 Analytics Dashboard: http://localhost:8501
echo   ⚙️ Admin Panel: http://localhost:8502
echo.
echo 🔧 API SERVICES:
echo   🚪 API Gateway: http://localhost:8080
echo   🔐 Account Service: http://localhost:8100
echo   📈 Dashboard Service: http://localhost:8200
echo   🔧 Backend API: http://localhost:8000/docs
echo.
echo 📈 MONITORING:
echo   📊 Grafana: http://localhost:3000 (admin/admin)
echo   📈 Prometheus: http://localhost:9090
echo.
echo 📋 QUICK START:
echo   1. 🎨 Main App: http://localhost:5000 (Vue.js Dashboard)
echo   2. 📊 Analytics: http://localhost:8501 (Streamlit Charts)
echo   3. ⚙️ Admin: http://localhost:8502 (Management Panel)
echo   4. 📈 Monitoring: http://localhost:3000 (Grafana)
echo.
echo 📋 MANAGEMENT:
echo   📋 View logs: docker-compose logs -f [service_name]
echo   🛑 Stop all: docker-compose down
echo   🔄 Restart: docker-compose restart [service_name]
echo.

REM Wait a bit more and then test
echo ⏳ Final health checks...
timeout /t 10 /nobreak >nul

REM Try to test the main application
curl -f http://localhost:5000 >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Web application may still be starting. You can access it manually.
    echo    Main App: http://localhost:5000
)

echo.
echo 🚀 Full Stack Platform is ready! Press any key to open applications...
pause >nul

REM Open main applications
echo 🌐 Opening Web Dashboard...
start http://localhost:5000
timeout /t 2 /nobreak >nul

echo 📊 Opening Analytics Dashboard...
start http://localhost:8501
timeout /t 2 /nobreak >nul

echo ⚙️ Opening Admin Panel...
start http://localhost:8502
timeout /t 2 /nobreak >nul

echo 📈 Opening Grafana Monitoring...
start http://localhost:3000

echo.
echo 🎉 All applications are now open in your browser!
echo.
echo 💡 TIP: Use Ctrl+C to view logs in real-time:
echo    docker-compose logs -f web_app
echo    docker-compose logs -f api_gateway
echo.
echo Press any key to exit this script (services will continue running)...
pause >nul
