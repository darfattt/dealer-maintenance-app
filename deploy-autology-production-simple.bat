@echo off
REM Simple Production Deployment Script for autology.id
REM This script uses docker-compose.production.yml to deploy to autology.id:8000

setlocal enabledelayedexpansion

echo ========================================
echo   Autology.id Production Deployment
echo ========================================
echo.

REM Check if Docker is available
echo [INFO] Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed or not in PATH
    pause
    exit /b 1
)
echo [SUCCESS] Docker and Docker Compose are available

REM Setup environment
echo.
echo [INFO] Setting up production environment for autology.id...
if not exist .env (
    if exist .env.production (
        copy .env.production .env
        echo [SUCCESS] Copied production environment file
    ) else (
        echo [ERROR] .env.production file not found
        pause
        exit /b 1
    )
) else (
    echo [INFO] .env file already exists
)

REM Create necessary directories
echo.
echo [INFO] Creating necessary directories...
if not exist logs mkdir logs
if not exist backups mkdir backups
echo [SUCCESS] Directories created

REM Stop existing services
echo.
echo [INFO] Stopping existing services...
docker-compose -f docker-compose.production.yml down

REM Build and start services
echo.
echo [INFO] Building services for autology.id...
docker-compose -f docker-compose.production.yml build
if errorlevel 1 (
    echo [ERROR] Failed to build services
    pause
    exit /b 1
)

echo.
echo [INFO] Starting database and redis...
docker-compose -f docker-compose.production.yml up -d postgres redis
if errorlevel 1 (
    echo [ERROR] Failed to start database and redis
    pause
    exit /b 1
)

echo [INFO] Waiting for database to be ready...
timeout /t 15 /nobreak >nul

echo.
echo [INFO] Starting backend services...
docker-compose -f docker-compose.production.yml up -d backend celery_worker celery_beat
if errorlevel 1 (
    echo [ERROR] Failed to start backend services
    pause
    exit /b 1
)

echo [INFO] Waiting for backend to be ready...
timeout /t 10 /nobreak >nul

echo.
echo [INFO] Starting microservices...
docker-compose -f docker-compose.production.yml up -d account_service api_gateway dashboard_dealer_service
if errorlevel 1 (
    echo [ERROR] Failed to start microservices
    pause
    exit /b 1
)

echo [INFO] Waiting for API gateway to be ready...
timeout /t 15 /nobreak >nul

echo.
echo [INFO] Starting web application...
docker-compose -f docker-compose.production.yml up -d web_app
if errorlevel 1 (
    echo [ERROR] Failed to start web application
    pause
    exit /b 1
)

echo.
echo [INFO] Starting analytics and admin panels...
docker-compose -f docker-compose.production.yml up -d analytics_dashboard admin_panel
if errorlevel 1 (
    echo [ERROR] Failed to start analytics and admin panels
    pause
    exit /b 1
)

echo.
echo [SUCCESS] All services started successfully!

REM Show deployment status
echo.
echo [INFO] Checking deployment status...
docker-compose -f docker-compose.production.yml ps

echo.
echo ========================================
echo   Deployment Information
echo ========================================
echo.
echo 🌐 Web Application:
echo    - Production: https://autology.id:5000
echo    - Local: http://localhost:5000
echo.
echo 🔌 API Gateway:
echo    - Production: https://autology.id:8080
echo    - Local: http://localhost:8080
echo.
echo ⚙️  Backend API:
echo    - Production: https://autology.id:8000
echo    - Local: http://localhost:8000
echo.
echo 📊 Analytics Dashboard:
echo    - Production: https://autology.id:8501
echo    - Local: http://localhost:8501
echo.
echo 🛠️  Admin Panel:
echo    - Production: https://autology.id:8502
echo    - Local: http://localhost:8502
echo.
echo ========================================
echo   Management Commands
echo ========================================
echo.
echo 📋 View logs:
echo    docker-compose -f docker-compose.production.yml logs -f
echo.
echo 🔄 Restart services:
echo    docker-compose -f docker-compose.production.yml restart
echo.
echo 🛑 Stop services:
echo    docker-compose -f docker-compose.production.yml down
echo.
echo 🗑️  Clean up:
echo    docker-compose -f docker-compose.production.yml down -v --remove-orphans
echo.
echo ========================================

echo.
echo [SUCCESS] Production deployment for autology.id completed! 🎉
echo.
echo [IMPORTANT] Make sure:
echo 1. DNS records point autology.id to this server's IP
echo 2. Firewall allows ports 5000, 8000, 8080, 8501, 8502
echo 3. SSL certificates are properly configured
echo.

pause
