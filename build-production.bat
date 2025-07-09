@echo off
setlocal enabledelayedexpansion

REM =============================================================================
REM DEALER DASHBOARD - PRODUCTION BUILD SCRIPT (Windows)
REM =============================================================================

echo.
echo ========================================
echo   🏗️ Building Dealer Dashboard Production Images
echo ========================================
echo.

REM Configuration
set VERSION=%1
if "%VERSION%"=="" set VERSION=latest
set PROJECT_NAME=dealer-dashboard

echo 📦 Version: %VERSION%
echo 🏷️ Project: %PROJECT_NAME%
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

REM Create environment file if it doesn't exist
if not exist ".env" (
    echo ⚠️ No .env file found. Creating from template...
    if exist ".env.production" (
        copy .env.production .env >nul
        echo 📝 Please edit .env file with your production values
        echo 🔐 Update passwords, secrets, and domain names
    ) else (
        echo ❌ No .env.production template found
        pause
        exit /b 1
    )
)

echo 🔨 Building production images...
echo.

REM Build Backend
echo 🔧 Building backend...
docker build -t %PROJECT_NAME%-backend:%VERSION% -t %PROJECT_NAME%-backend:latest --target production ./backend
if %errorlevel% neq 0 (
    echo ❌ Failed to build backend
    pause
    exit /b 1
)
echo ✅ Backend built successfully
echo.

REM Build Account Service
echo 🔐 Building account service...
docker build -t %PROJECT_NAME%-account-service:%VERSION% -t %PROJECT_NAME%-account-service:latest --target production -f ./backend-microservices/docker/Dockerfile.account ./backend-microservices
if %errorlevel% neq 0 (
    echo ❌ Failed to build account service
    pause
    exit /b 1
)
echo ✅ Account service built successfully
echo.

REM Build API Gateway
echo 🚪 Building API gateway...
docker build -t %PROJECT_NAME%-api-gateway:%VERSION% -t %PROJECT_NAME%-api-gateway:latest --target production -f ./backend-microservices/docker/Dockerfile.gateway ./backend-microservices
if %errorlevel% neq 0 (
    echo ❌ Failed to build API gateway
    pause
    exit /b 1
)
echo ✅ API gateway built successfully
echo.

REM Build Dashboard Dealer Service
echo 📈 Building dashboard dealer service...
docker build -t %PROJECT_NAME%-dashboard-dealer-service:%VERSION% -t %PROJECT_NAME%-dashboard-dealer-service:latest --target production -f ./backend-microservices/docker/Dockerfile.dashboard-dealer ./backend-microservices
if %errorlevel% neq 0 (
    echo ❌ Failed to build dashboard dealer service
    pause
    exit /b 1
)
echo ✅ Dashboard dealer service built successfully
echo.

REM Build Web App
echo 🎨 Building web app...
docker build -t %PROJECT_NAME%-web-app:%VERSION% -t %PROJECT_NAME%-web-app:latest --target production ./web
if %errorlevel% neq 0 (
    echo ❌ Failed to build web app
    pause
    exit /b 1
)
echo ✅ Web app built successfully
echo.

REM Build Analytics Dashboard
echo 📊 Building analytics dashboard...
docker build -t %PROJECT_NAME%-analytics-dashboard:%VERSION% -t %PROJECT_NAME%-analytics-dashboard:latest --target production ./dashboard_analytics
if %errorlevel% neq 0 (
    echo ❌ Failed to build analytics dashboard
    pause
    exit /b 1
)
echo ✅ Analytics dashboard built successfully
echo.

REM Build Admin Panel
echo ⚙️ Building admin panel...
docker build -t %PROJECT_NAME%-admin-panel:%VERSION% -t %PROJECT_NAME%-admin-panel:latest --target production ./admin_panel
if %errorlevel% neq 0 (
    echo ❌ Failed to build admin panel
    pause
    exit /b 1
)
echo ✅ Admin panel built successfully
echo.

echo 🎉 Production build completed successfully!
echo.
echo 📋 Built Images:
echo   📦 %PROJECT_NAME%-backend:%VERSION%
echo   📦 %PROJECT_NAME%-account-service:%VERSION%
echo   📦 %PROJECT_NAME%-api-gateway:%VERSION%
echo   📦 %PROJECT_NAME%-dashboard-dealer-service:%VERSION%
echo   📦 %PROJECT_NAME%-web-app:%VERSION%
echo   📦 %PROJECT_NAME%-analytics-dashboard:%VERSION%
echo   📦 %PROJECT_NAME%-admin-panel:%VERSION%
echo.
echo 🚀 Next Steps:
echo   1. Update .env file with production values
echo   2. Deploy using: docker-compose -f docker-compose.production.yml up -d
echo   3. Or deploy to AWS using deployment scripts
echo.

pause
