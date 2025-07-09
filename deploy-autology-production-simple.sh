#!/bin/bash

# Simple Production Deployment Script for autology.id
# This script uses docker-compose.production.yml to deploy to autology.id:8000

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "   Autology.id Production Deployment"
echo "========================================"
echo

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is available
log_info "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed or not in PATH"
    exit 1
fi
log_success "Docker and Docker Compose are available"

# Setup environment
echo
log_info "Setting up production environment for autology.id..."
if [ ! -f .env ]; then
    if [ -f .env.production ]; then
        cp .env.production .env
        log_success "Copied production environment file"
    else
        log_error ".env.production file not found"
        exit 1
    fi
else
    log_info ".env file already exists"
fi

# Create necessary directories
echo
log_info "Creating necessary directories..."
mkdir -p logs backups
log_success "Directories created"

# Stop existing services
echo
log_info "Stopping existing services..."
docker-compose -f docker-compose.production.yml down || true

# Build and start services
echo
log_info "Building services for autology.id..."
docker-compose -f docker-compose.production.yml build
if [ $? -ne 0 ]; then
    log_error "Failed to build services"
    exit 1
fi

echo
log_info "Starting database and redis..."
docker-compose -f docker-compose.production.yml up -d postgres redis
if [ $? -ne 0 ]; then
    log_error "Failed to start database and redis"
    exit 1
fi

log_info "Waiting for database to be ready..."
sleep 15

echo
log_info "Starting backend services..."
docker-compose -f docker-compose.production.yml up -d backend celery_worker celery_beat
if [ $? -ne 0 ]; then
    log_error "Failed to start backend services"
    exit 1
fi

log_info "Waiting for backend to be ready..."
sleep 10

echo
log_info "Starting microservices..."
docker-compose -f docker-compose.production.yml up -d account_service api_gateway dashboard_dealer_service
if [ $? -ne 0 ]; then
    log_error "Failed to start microservices"
    exit 1
fi

log_info "Waiting for API gateway to be ready..."
sleep 15

echo
log_info "Starting web application..."
docker-compose -f docker-compose.production.yml up -d web_app
if [ $? -ne 0 ]; then
    log_error "Failed to start web application"
    exit 1
fi

echo
log_info "Starting analytics and admin panels..."
docker-compose -f docker-compose.production.yml up -d analytics_dashboard admin_panel
if [ $? -ne 0 ]; then
    log_error "Failed to start analytics and admin panels"
    exit 1
fi

echo
log_success "All services started successfully!"

# Show deployment status
echo
log_info "Checking deployment status..."
docker-compose -f docker-compose.production.yml ps

echo
echo "========================================"
echo "   Deployment Information"
echo "========================================"
echo
echo "🌐 Web Application:"
echo "   - Production: https://autology.id:5000"
echo "   - Local: http://localhost:5000"
echo
echo "🔌 API Gateway:"
echo "   - Production: https://autology.id:8080"
echo "   - Local: http://localhost:8080"
echo
echo "⚙️  Backend API:"
echo "   - Production: https://autology.id:8000"
echo "   - Local: http://localhost:8000"
echo
echo "📊 Analytics Dashboard:"
echo "   - Production: https://autology.id:8501"
echo "   - Local: http://localhost:8501"
echo
echo "🛠️  Admin Panel:"
echo "   - Production: https://autology.id:8502"
echo "   - Local: http://localhost:8502"
echo
echo "========================================"
echo "   Management Commands"
echo "========================================"
echo
echo "📋 View logs:"
echo "   docker-compose -f docker-compose.production.yml logs -f"
echo
echo "🔄 Restart services:"
echo "   docker-compose -f docker-compose.production.yml restart"
echo
echo "🛑 Stop services:"
echo "   docker-compose -f docker-compose.production.yml down"
echo
echo "🗑️  Clean up:"
echo "   docker-compose -f docker-compose.production.yml down -v --remove-orphans"
echo
echo "========================================"

echo
log_success "Production deployment for autology.id completed! 🎉"
echo
log_warning "IMPORTANT: Make sure:"
echo "1. DNS records point autology.id to this server's IP"
echo "2. Firewall allows ports 5000, 8000, 8080, 8501, 8502"
echo "3. SSL certificates are properly configured"
echo
