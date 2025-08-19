#!/bin/bash

# Production Web Deployment Script
# This script deploys the web application in production mode with proper backend connectivity

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.production.yml"
WEB_SERVICE="web_app"
API_SERVICE="api_gateway"

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

# Check if Docker and Docker Compose are available
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    log_success "Dependencies check passed"
}

# Check if required environment variables are set
check_environment() {
    log_info "Checking environment variables..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        log_warning ".env file not found, creating default one..."
        cat > .env << EOF
# Database Configuration
POSTGRES_DB=dealer_dashboard
POSTGRES_USER=dealer_user
POSTGRES_PASSWORD=dealer_pass_prod_$(date +%s)
POSTGRES_PORT=5432

# Redis Configuration
REDIS_PASSWORD=redis_pass_prod_$(date +%s)
REDIS_PORT=6379

# JWT Configuration
JWT_SECRET_KEY=jwt_secret_prod_$(openssl rand -hex 32)

# Service Ports
BACKEND_PORT=8000
API_GATEWAY_PORT=8080
WEB_APP_PORT=5000
ACCOUNT_SERVICE_PORT=8100
DASHBOARD_SERVICE_PORT=8200
ANALYTICS_PORT=8501
ADMIN_PANEL_PORT=8502

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5000,http://localhost:3000

# Admin Configuration
ADMIN_EMAIL=admin@dealer-dashboard.com
ADMIN_PASSWORD=admin_pass_$(date +%s)
ADMIN_FULL_NAME=System Administrator
EOF
        log_success "Created default .env file"
    fi
    
    # Source the .env file
    source .env
    
    log_success "Environment variables loaded"
}

# Build and deploy the web application
deploy_web() {
    log_info "Building and deploying web application..."
    
    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose -f $COMPOSE_FILE down || true
    
    # Build the web application
    log_info "Building web application..."
    docker-compose -f $COMPOSE_FILE build $WEB_SERVICE
    
    # Start the backend services first
    log_info "Starting backend services..."
    docker-compose -f $COMPOSE_FILE up -d postgres redis
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 10
    
    # Start backend and API gateway
    docker-compose -f $COMPOSE_FILE up -d backend account_service api_gateway
    
    # Wait for API gateway to be ready
    log_info "Waiting for API gateway to be ready..."
    sleep 15
    
    # Start the web application
    log_info "Starting web application..."
    docker-compose -f $COMPOSE_FILE up -d $WEB_SERVICE
    
    log_success "Web application deployed successfully"
}

# Check deployment status
check_deployment() {
    log_info "Checking deployment status..."
    
    # Check if containers are running
    if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        log_success "Containers are running"
    else
        log_error "Some containers are not running"
        docker-compose -f $COMPOSE_FILE ps
        return 1
    fi
    
    # Check web application health
    log_info "Checking web application health..."
    local web_port=$(grep WEB_APP_PORT .env | cut -d'=' -f2)
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:${web_port}/health &> /dev/null; then
            log_success "Web application is healthy"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Web application health check failed after $max_attempts attempts"
            return 1
        fi
        
        log_info "Attempt $attempt/$max_attempts: Web application not ready, waiting 5 seconds..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    # Check API gateway health
    log_info "Checking API gateway health..."
    local api_port=$(grep API_GATEWAY_PORT .env | cut -d'=' -f2)
    
    if curl -f http://localhost:${api_port}/health &> /dev/null; then
        log_success "API gateway is healthy"
    else
        log_warning "API gateway health check failed"
    fi
    
    log_success "Deployment status check completed"
}

# Show deployment information
show_info() {
    log_info "Deployment Information:"
    echo "=========================="
    
    source .env
    
    echo "Web Application: http://localhost:${WEB_APP_PORT:-5000}"
    echo "API Gateway: http://localhost:${API_GATEWAY_PORT:-8080}"
    echo "Backend API: http://localhost:${BACKEND_PORT:-8000}"
    echo "Analytics Dashboard: http://localhost:${ANALYTICS_PORT:-8501}"
    echo "Admin Panel: http://localhost:${ADMIN_PANEL_PORT:-8502}"
    echo ""
    echo "To view logs: docker-compose -f $COMPOSE_FILE logs -f"
    echo "To stop services: docker-compose -f $COMPOSE_FILE down"
    echo "=========================="
}

# Main execution
main() {
    log_info "Starting production web deployment..."
    
    check_dependencies
    check_environment
    deploy_web
    check_deployment
    show_info
    
    log_success "Production web deployment completed successfully!"
}

# Run main function
main "$@"
