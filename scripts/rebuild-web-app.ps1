#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Rebuild and restart the web application container to reflect code changes

.DESCRIPTION
    This script stops the current web application container, rebuilds it with no cache
    to ensure all changes are included, and starts it again on port 5000.

.EXAMPLE
    .\scripts\rebuild-web-app.ps1
    
.NOTES
    Use this script whenever you make changes to the web application code
    and want to see them reflected in the production container on port 5000.
#>

param(
    [switch]$NoCache = $true,
    [switch]$Verbose = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = $Reset
    )
    Write-Host "${Color}${Message}${Reset}"
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "🔧 $Message" $Blue
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" $Green
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" $Red
}

try {
    Write-ColorOutput "🚀 Web Application Rebuild Script" $Blue
    Write-ColorOutput "=================================" $Blue
    Write-Host ""

    # Check if we're in the correct directory
    if (-not (Test-Path "docker-compose.yml")) {
        Write-Error "docker-compose.yml not found. Please run this script from the project root directory."
        exit 1
    }

    # Step 1: Stop the current container
    Write-Step "Stopping current web application container..."
    try {
        docker stop dealer_web_app 2>$null
        Write-Success "Container stopped successfully"
    }
    catch {
        Write-Warning "Container was not running or already stopped"
    }

    # Step 2: Remove the container
    Write-Step "Removing container..."
    try {
        docker rm dealer_web_app 2>$null
        Write-Success "Container removed successfully"
    }
    catch {
        Write-Warning "Container was already removed"
    }

    # Step 3: Build the new image
    Write-Step "Building new web application image..."
    if ($NoCache) {
        Write-Host "   Using --no-cache to ensure fresh build..."
        $buildResult = docker-compose build --no-cache web_app
    }
    else {
        $buildResult = docker-compose build web_app
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Image built successfully"
    }
    else {
        Write-Error "Failed to build image"
        exit 1
    }

    # Step 4: Start the container
    Write-Step "Starting web application container..."
    $startResult = docker-compose up -d web_app
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Container started successfully"
    }
    else {
        Write-Error "Failed to start container"
        exit 1
    }

    # Step 5: Wait for container to be healthy
    Write-Step "Waiting for container to be ready..."
    $maxWait = 30
    $waited = 0
    
    do {
        Start-Sleep 2
        $waited += 2
        $status = docker inspect dealer_web_app --format='{{.State.Health.Status}}' 2>$null
        
        if ($status -eq "healthy") {
            Write-Success "Container is healthy and ready!"
            break
        }
        elseif ($waited -ge $maxWait) {
            Write-Warning "Container health check timeout, but it may still be working"
            break
        }
        else {
            Write-Host "   Waiting... ($waited/$maxWait seconds)"
        }
    } while ($true)

    # Step 6: Show container status
    Write-Step "Container status:"
    docker ps --filter "name=dealer_web_app" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    # Step 7: Test the application
    Write-Step "Testing web application..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000" -Method HEAD -TimeoutSec 10 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Success "Web application is responding correctly!"
        }
        else {
            Write-Warning "Web application returned status code: $($response.StatusCode)"
        }
    }
    catch {
        Write-Warning "Could not test web application: $($_.Exception.Message)"
    }

    Write-Host ""
    Write-ColorOutput "🎉 Web Application Rebuild Complete!" $Green
    Write-ColorOutput "====================================" $Green
    Write-Host ""
    Write-ColorOutput "📱 Access your application at: http://localhost:5000" $Blue
    Write-Host ""
    Write-ColorOutput "💡 Tips:" $Yellow
    Write-ColorOutput "   • Development mode (hot reload): npm run dev in web/ directory" $Yellow
    Write-ColorOutput "   • Production mode (this script): Requires rebuild for changes" $Yellow
    Write-ColorOutput "   • Use this script whenever you make changes to web/ code" $Yellow

}
catch {
    Write-Error "Script failed: $($_.Exception.Message)"
    exit 1
}
