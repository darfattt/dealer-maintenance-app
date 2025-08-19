@echo off
REM Production Web Deployment Script for Windows
REM This script deploys the web application in production mode with proper backend connectivity

setlocal enabledelayedexpansion

REM Configuration
set COMPOSE_FILE=docker-compose.production.yml
set WEB_SERVICE=web_app
set API_SERVICE=api_gateway

echo [INFO] Starting production web deployment...

REM Check if Docker and Docker Compose are available
echo [INFO] Checking dependencies...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed or not in PATH
    exit /b 1
)
echo [SUCCESS] Dependencies check passed

REM Check if .env file exists, create if not
if not exist .env (
    echo [WARNING] .env file not found, creating default one...
    (
        echo # Database Configuration
        echo POSTGRES_DB=dealer_dashboard
        echo POSTGRES_USER=dealer_user
        echo POSTGRES_PASSWORD=dealer_pass_prod_%RANDOM%
        echo POSTGRES_PORT=5432
        echo.
        echo # Redis Configuration
        echo REDIS_PASSWORD=redis_pass_prod_%RANDOM%
        echo REDIS_PORT=6379
        echo.
        echo # JWT Configuration
        echo JWT_SECRET_KEY=jwt_secret_prod_%RANDOM%_%RANDOM%
        echo.
        echo # Service Ports
        echo BACKEND_PORT=8000
        echo API_GATEWAY_PORT=8080
        echo WEB_APP_PORT=5000
        echo ACCOUNT_SERVICE_PORT=8100
        echo DASHBOARD_SERVICE_PORT=8200
        echo ANALYTICS_PORT=8501
        echo ADMIN_PANEL_PORT=8502
        echo.
        echo # Environment
        echo ENVIRONMENT=production
        echo LOG_LEVEL=INFO
        echo.
        echo # CORS Configuration
        echo ALLOWED_ORIGINS=http://localhost:5000,http://localhost:3000
        echo.
        echo # Admin Configuration
        echo ADMIN_EMAIL=admin@dealer-dashboard.com
        echo ADMIN_PASSWORD=admin_pass_%RANDOM%
        echo ADMIN_FULL_NAME=System Administrator
    ) > .env
    echo [SUCCESS] Created default .env file
)

REM Build and deploy the web application
echo [INFO] Building and deploying web application...

REM Stop existing containers
echo [INFO] Stopping existing containers...
docker-compose -f %COMPOSE_FILE% down

REM Build the web application
echo [INFO] Building web application...
docker-compose -f %COMPOSE_FILE% build %WEB_SERVICE%
if errorlevel 1 (
    echo [ERROR] Failed to build web application
    exit /b 1
)

REM Start the backend services first
echo [INFO] Starting backend services...
docker-compose -f %COMPOSE_FILE% up -d postgres redis
if errorlevel 1 (
    echo [ERROR] Failed to start backend services
    exit /b 1
)

REM Wait for database to be ready
echo [INFO] Waiting for database to be ready...
timeout /t 10 /nobreak >nul

REM Start backend and API gateway
echo [INFO] Starting backend and API gateway...
docker-compose -f %COMPOSE_FILE% up -d backend account_service api_gateway
if errorlevel 1 (
    echo [ERROR] Failed to start backend and API gateway
    exit /b 1
)

REM Wait for API gateway to be ready
echo [INFO] Waiting for API gateway to be ready...
timeout /t 15 /nobreak >nul

REM Start the web application
echo [INFO] Starting web application...
docker-compose -f %COMPOSE_FILE% up -d %WEB_SERVICE%
if errorlevel 1 (
    echo [ERROR] Failed to start web application
    exit /b 1
)

echo [SUCCESS] Web application deployed successfully

REM Check deployment status
echo [INFO] Checking deployment status...
docker-compose -f %COMPOSE_FILE% ps

REM Show deployment information
echo [INFO] Deployment Information:
echo ==========================
echo Web Application: http://localhost:5000
echo API Gateway: http://localhost:8080
echo Backend API: http://localhost:8000
echo Analytics Dashboard: http://localhost:8501
echo Admin Panel: http://localhost:8502
echo.
echo To view logs: docker-compose -f %COMPOSE_FILE% logs -f
echo To stop services: docker-compose -f %COMPOSE_FILE% down
echo ==========================

echo [SUCCESS] Production web deployment completed successfully!
pause
