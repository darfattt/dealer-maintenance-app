# Unified startup script for all Dealer Dashboard services (PowerShell)
# This script starts both the existing monolithic services and new microservices

Write-Host "🚀 Starting Dealer Dashboard - Complete System" -ForegroundColor Green
Write-Host "=============================================="

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Please review and update .env file with your configuration" -ForegroundColor Yellow
}

# Build and start all services
Write-Host "🏗️  Building and starting all services..." -ForegroundColor Cyan
Write-Host "This includes:" -ForegroundColor Cyan
Write-Host "  📊 Main Backend (Port 8000)" -ForegroundColor White
Write-Host "  👤 Account Service (Port 8100)" -ForegroundColor White
Write-Host "  🌐 API Gateway (Port 8080)" -ForegroundColor White
Write-Host "  📈 Analytics Dashboard (Port 8501)" -ForegroundColor White
Write-Host "  ⚙️  Admin Panel (Port 8502)" -ForegroundColor White
Write-Host "  🗄️  PostgreSQL (Port 5432)" -ForegroundColor White
Write-Host "  🔴 Redis (Port 6379)" -ForegroundColor White
Write-Host "  📊 Prometheus (Port 9090)" -ForegroundColor White
Write-Host "  📊 Grafana (Port 3000)" -ForegroundColor White
Write-Host ""

docker-compose up -d --build

# Wait for services to start
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

Write-Host "🔍 Checking service health..." -ForegroundColor Cyan

# Function to check HTTP endpoint
function Test-HttpEndpoint {
    param($Url, $ServiceName)
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $ServiceName is healthy" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "❌ $ServiceName is not healthy" -ForegroundColor Red
        return $false
    }
}

# Check PostgreSQL
try {
    $pgResult = docker-compose exec -T postgres pg_isready -U dealer_user -d dealer_dashboard
    if ($pgResult -match "accepting connections") {
        Write-Host "✅ PostgreSQL is healthy" -ForegroundColor Green
    } else {
        Write-Host "❌ PostgreSQL is not healthy" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ PostgreSQL check failed" -ForegroundColor Red
}

# Check Redis
try {
    $redisResult = docker-compose exec -T redis redis-cli ping
    if ($redisResult -match "PONG") {
        Write-Host "✅ Redis is healthy" -ForegroundColor Green
    } else {
        Write-Host "❌ Redis is not healthy" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Redis check failed" -ForegroundColor Red
}

# Check services
Test-HttpEndpoint "http://localhost:8000/health" "Main Backend"
Test-HttpEndpoint "http://localhost:8100/api/v1/health" "Account Service"
Test-HttpEndpoint "http://localhost:8080/health" "API Gateway"
Test-HttpEndpoint "http://localhost:8501/_stcore/health" "Analytics Dashboard"
Test-HttpEndpoint "http://localhost:8502/_stcore/health" "Admin Panel"

Write-Host ""
Write-Host "🎉 Dealer Dashboard System Started!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access Points:" -ForegroundColor Cyan
Write-Host "=================================="
Write-Host "  🌐 API Gateway (Unified API):     http://localhost:8080" -ForegroundColor White
Write-Host "  📚 API Gateway Docs:              http://localhost:8080/docs" -ForegroundColor White
Write-Host ""
Write-Host "  📊 Main Backend (Legacy):         http://localhost:8000" -ForegroundColor White
Write-Host "  👤 Account Service:               http://localhost:8100" -ForegroundColor White
Write-Host "  📚 Account Service Docs:          http://localhost:8100/docs" -ForegroundColor White
Write-Host ""
Write-Host "  📈 Analytics Dashboard:           http://localhost:8501" -ForegroundColor White
Write-Host "  ⚙️  Admin Panel:                  http://localhost:8502" -ForegroundColor White
Write-Host ""
Write-Host "  📊 Prometheus (Metrics):          http://localhost:9090" -ForegroundColor White
Write-Host "  📊 Grafana (Monitoring):          http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "🗄️  Database Access:" -ForegroundColor Cyan
Write-Host "=================================="
Write-Host "  🗄️  PostgreSQL:                   localhost:5432" -ForegroundColor White
Write-Host "  🔴 Redis:                         localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Default Credentials:" -ForegroundColor Cyan
Write-Host "=================================="
Write-Host "  👤 Admin User:" -ForegroundColor White
Write-Host "     📧 Email:    admin@dealer-dashboard.com" -ForegroundColor White
Write-Host "     🔑 Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "  📊 Grafana:" -ForegroundColor White
Write-Host "     👤 Username: admin" -ForegroundColor White
Write-Host "     🔑 Password: admin" -ForegroundColor White
Write-Host ""
Write-Host "📋 Management Commands:" -ForegroundColor Cyan
Write-Host "=================================="
Write-Host "  🛑 Stop all services:    docker-compose down" -ForegroundColor White
Write-Host "  📋 View logs:            docker-compose logs -f" -ForegroundColor White
Write-Host "  📋 View specific logs:   docker-compose logs -f [service_name]" -ForegroundColor White
Write-Host "  🔄 Restart service:      docker-compose restart [service_name]" -ForegroundColor White
Write-Host "  🏗️  Rebuild service:      docker-compose up -d --build [service_name]" -ForegroundColor White
