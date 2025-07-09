@echo off
REM Production Deployment Script for autology.id (Windows)
REM This script deploys the complete dealer management system to autology.id domain

setlocal enabledelayedexpansion

REM Configuration
set DOMAIN=autology.id
set COMPOSE_FILE=docker-compose.yml
set ENV_FILE=.env

echo [INFO] Starting production deployment for %DOMAIN%...

REM Check dependencies
echo [INFO] Checking dependencies...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed
    exit /b 1
)
echo [SUCCESS] Dependencies check passed

REM Setup environment
echo [INFO] Setting up production environment...
if not exist %ENV_FILE% (
    if exist .env.production (
        copy .env.production %ENV_FILE%
        echo [SUCCESS] Copied production environment file
    ) else (
        echo [ERROR] Production environment file not found
        exit /b 1
    )
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist logs mkdir logs
if not exist backups mkdir backups
if not exist ssl\certs mkdir ssl\certs
if not exist ssl\private mkdir ssl\private
echo [SUCCESS] Directories created

REM Deploy services
echo [INFO] Deploying services for %DOMAIN%...

REM Stop existing services
echo [INFO] Stopping existing services...
docker-compose -f %COMPOSE_FILE% down

REM Build services
echo [INFO] Building services...
docker-compose -f %COMPOSE_FILE% build
if errorlevel 1 (
    echo [ERROR] Failed to build services
    exit /b 1
)

REM Start database and redis first
echo [INFO] Starting database and redis...
docker-compose -f %COMPOSE_FILE% up -d postgres redis
if errorlevel 1 (
    echo [ERROR] Failed to start database and redis
    exit /b 1
)

REM Wait for database
echo [INFO] Waiting for database to be ready...
timeout /t 15 /nobreak >nul

REM Start backend services
echo [INFO] Starting backend services...
docker-compose -f %COMPOSE_FILE% up -d backend celery_worker celery_beat
if errorlevel 1 (
    echo [ERROR] Failed to start backend services
    exit /b 1
)

REM Wait for backend
echo [INFO] Waiting for backend to be ready...
timeout /t 10 /nobreak >nul

REM Start microservices
echo [INFO] Starting microservices...
docker-compose -f %COMPOSE_FILE% up -d account_service api_gateway dashboard_dealer_service
if errorlevel 1 (
    echo [ERROR] Failed to start microservices
    exit /b 1
)

REM Wait for API gateway
echo [INFO] Waiting for API gateway to be ready...
timeout /t 15 /nobreak >nul

REM Start web application
echo [INFO] Starting web application...
docker-compose -f %COMPOSE_FILE% up -d web_app
if errorlevel 1 (
    echo [ERROR] Failed to start web application
    exit /b 1
)

REM Start analytics and admin panels
echo [INFO] Starting analytics and admin panels...
docker-compose -f %COMPOSE_FILE% up -d analytics_dashboard admin_panel
if errorlevel 1 (
    echo [ERROR] Failed to start analytics and admin panels
    exit /b 1
)

echo [SUCCESS] Services deployed successfully

REM Start monitoring services
echo [INFO] Setting up monitoring...
docker-compose -f %COMPOSE_FILE% up -d prometheus grafana
echo [SUCCESS] Monitoring services started

REM Show deployment status
echo [INFO] Checking deployment status...
docker-compose -f %COMPOSE_FILE% ps

REM Show deployment information
echo [INFO] Deployment Information for %DOMAIN%:
echo ==================================================
echo 🌐 Web Application: https://%DOMAIN%:5000
echo 🔌 API Gateway: https://%DOMAIN%:8080
echo ⚙️  Backend API: https://%DOMAIN%:8000
echo 📊 Analytics Dashboard: https://%DOMAIN%:8501
echo 🛠️  Admin Panel: https://%DOMAIN%:8502
echo 📈 Grafana: https://%DOMAIN%:3000
echo 🔍 Prometheus: https://%DOMAIN%:9090
echo.
echo Local Development URLs:
echo 🌐 Web Application: http://localhost:5000
echo 🔌 API Gateway: http://localhost:8080
echo ⚙️  Backend API: http://localhost:8000
echo 📊 Analytics Dashboard: http://localhost:8501
echo 🛠️  Admin Panel: http://localhost:8502
echo.
echo Management Commands:
echo 📋 View logs: docker-compose logs -f
echo 🔄 Restart services: docker-compose restart
echo 🛑 Stop services: docker-compose down
echo 🗑️  Clean up: docker-compose down -v --remove-orphans
echo ==================================================

echo [SUCCESS] Production deployment for %DOMAIN% completed successfully! 🎉
echo [INFO] Please update your DNS records to point %DOMAIN% to this server's IP address.
echo [WARNING] Remember to replace self-signed certificates with proper SSL certificates for production use.

pause
