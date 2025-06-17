# PowerShell script to start web application in development mode
param(
    [switch]$Build,
    [switch]$Clean
)

Write-Host "🚀 Starting Web Application in Development Mode" -ForegroundColor Green

# Set working directory to project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

# Clean up if requested
if ($Clean) {
    Write-Host "🧹 Cleaning up containers and volumes..." -ForegroundColor Yellow
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v --remove-orphans
    docker system prune -f
}

# Build if requested or if images don't exist
if ($Build) {
    Write-Host "🔨 Building development images..." -ForegroundColor Yellow
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml build web_app
}

# Create network if it doesn't exist
Write-Host "🌐 Creating network..." -ForegroundColor Yellow
docker network create dealer-network 2>$null

# Start the services
Write-Host "🚀 Starting development services..." -ForegroundColor Green
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres redis api_gateway account_service

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Start web application
Write-Host "🌐 Starting web application..." -ForegroundColor Green
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up web_app

Write-Host "✅ Development environment started!" -ForegroundColor Green
Write-Host "📱 Web Application: http://localhost:5173" -ForegroundColor Cyan
Write-Host "🔧 API Gateway: http://localhost:8080" -ForegroundColor Cyan
Write-Host "📊 Analytics: http://localhost:8501" -ForegroundColor Cyan
Write-Host "⚙️ Admin Panel: http://localhost:8502" -ForegroundColor Cyan
