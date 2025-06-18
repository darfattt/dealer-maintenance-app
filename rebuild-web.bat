@echo off
REM Quick rebuild script for web application
REM This rebuilds the Docker container to reflect code changes

echo 🚀 Rebuilding Web Application...
echo.

REM Stop and remove current container
echo Stopping current container...
docker stop dealer_web_app 2>nul
docker rm dealer_web_app 2>nul

REM Rebuild with no cache
echo Building new image...
docker-compose build --no-cache web_app

REM Start container
echo Starting container...
docker-compose up -d web_app

REM Show status
echo.
echo Container status:
docker ps --filter "name=dealer_web_app"

echo.
echo ✅ Done! Access your app at http://localhost:5000
echo.
pause
