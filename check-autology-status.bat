@echo off
REM Quick status check for autology.id production deployment

echo ========================================
echo   Autology.id Production Status Check
echo ========================================
echo.

REM Check if services are running
echo [INFO] Checking service status...
docker-compose -f docker-compose.production.yml ps

echo.
echo [INFO] Testing service endpoints...

REM Test web application
echo Testing Web Application (localhost:5000)...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:5000/health 2>nul || echo "Web Application: Not responding"

REM Test API Gateway
echo Testing API Gateway (localhost:8080)...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8080/health 2>nul || echo "API Gateway: Not responding"

REM Test Backend API
echo Testing Backend API (localhost:8000)...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8000/health 2>nul || echo "Backend API: Not responding"

REM Test Analytics Dashboard
echo Testing Analytics Dashboard (localhost:8501)...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8501/_stcore/health 2>nul || echo "Analytics Dashboard: Not responding"

REM Test Admin Panel
echo Testing Admin Panel (localhost:8502)...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8502/_stcore/health 2>nul || echo "Admin Panel: Not responding"

echo.
echo ========================================
echo   Production URLs for autology.id
echo ========================================
echo.
echo 🌐 Web Application: https://autology.id:5000
echo 🔌 API Gateway: https://autology.id:8080
echo ⚙️  Backend API: https://autology.id:8000
echo 📊 Analytics Dashboard: https://autology.id:8501
echo 🛠️  Admin Panel: https://autology.id:8502
echo.

pause
