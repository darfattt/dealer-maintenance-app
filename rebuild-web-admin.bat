@echo off
REM Quick rebuild script for web admin application (System Admin Portal)
REM This rebuilds the Docker container to reflect code changes

echo 🚀 Rebuilding Web Admin Application...
echo.

REM Stop and remove current container
echo Stopping current container...
docker stop dealer_web_admin 2>nul
docker rm dealer_web_admin 2>nul

REM Rebuild with no cache
echo Building new image...
docker-compose build --no-cache web_admin

REM Start container
echo Starting container...
docker-compose up -d web_admin

REM Show status
echo.
echo Container status:
docker ps --filter "name=dealer_web_admin"

echo.
echo ✅ Done! Access the System Admin Portal at:
echo    - Production: http://localhost:5001
echo    - Development: http://localhost:5174 (use npm run dev)
echo.
pause
