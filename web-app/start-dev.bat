@echo off
echo Starting Dealer Dashboard Web Application...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if package.json exists
if not exist package.json (
    echo Error: package.json not found
    echo Please run this script from the web-app directory
    pause
    exit /b 1
)

REM Install dependencies if node_modules doesn't exist
if not exist node_modules (
    echo Installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Copy environment file if it doesn't exist
if not exist .env (
    if exist .env.example (
        echo Creating .env file from .env.example...
        copy .env.example .env
    )
)

echo.
echo Starting development server...
echo Web App will be available at: http://localhost:3000
echo.
echo Make sure the following services are running:
echo - API Gateway: http://localhost:8080
echo - Account Service: http://localhost:8100
echo.

REM Start the development server
npm run dev
