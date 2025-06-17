# PowerShell script to start web application in production mode
param(
    [switch]$Build,
    [switch]$Clean
)

Write-Host "🚀 Starting Web Application in Production Mode" -ForegroundColor Green

# Set working directory to project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

# Clean up if requested
if ($Clean) {
    Write-Host "🧹 Cleaning up containers and volumes..." -ForegroundColor Yellow
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down -v --remove-orphans
    docker system prune -f
}

# Build if requested or if images don't exist
if ($Build) {
    Write-Host "🔨 Building production images..." -ForegroundColor Yellow
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build web_primevue
}

# Start the services
Write-Host "🚀 Starting production services..." -ForegroundColor Green
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service health
Write-Host "🔍 Checking service health..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

Write-Host "✅ Production environment started!" -ForegroundColor Green
Write-Host "📱 Web Application: http://localhost:5000" -ForegroundColor Cyan
Write-Host "🔧 API Gateway: http://localhost:8080" -ForegroundColor Cyan
Write-Host "📊 Analytics: http://localhost:8501" -ForegroundColor Cyan
Write-Host "⚙️ Admin Panel: http://localhost:8502" -ForegroundColor Cyan
Write-Host "📈 Grafana: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔍 Prometheus: http://localhost:9090" -ForegroundColor Cyan
