#!/bin/bash

# Production Deployment Script for autology.id
# This script deploys the complete dealer management system to autology.id domain

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="autology.id"
COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE=".env"

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

# Check if running as root (required for SSL certificates)
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. Make sure this is intended for production deployment."
    fi
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    if ! command -v openssl &> /dev/null; then
        log_error "OpenSSL is not installed"
        exit 1
    fi
    
    log_success "Dependencies check passed"
}

# Setup environment
setup_environment() {
    log_info "Setting up production environment..."
    
    # Copy production environment file
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f ".env.production" ]; then
            cp .env.production $ENV_FILE
            log_success "Copied production environment file"
        else
            log_error "Production environment file not found"
            exit 1
        fi
    fi
    
    # Source environment variables
    source $ENV_FILE
    
    # Validate required variables
    if [ -z "$DOMAIN_NAME" ]; then
        log_error "DOMAIN_NAME not set in environment"
        exit 1
    fi
    
    log_success "Environment setup completed"
}

# Setup SSL certificates
setup_ssl() {
    log_info "Setting up SSL certificates for $DOMAIN..."
    
    # Create SSL directory
    mkdir -p ssl/certs ssl/private
    
    # Check if certificates exist
    if [ ! -f "ssl/certs/${DOMAIN}.crt" ] || [ ! -f "ssl/private/${DOMAIN}.key" ]; then
        log_warning "SSL certificates not found. Generating self-signed certificates for development..."
        
        # Generate self-signed certificate
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "ssl/private/${DOMAIN}.key" \
            -out "ssl/certs/${DOMAIN}.crt" \
            -subj "/C=ID/ST=Jakarta/L=Jakarta/O=Autology/OU=IT/CN=${DOMAIN}/emailAddress=admin@${DOMAIN}"
        
        log_warning "Self-signed certificate generated. Replace with proper SSL certificate for production!"
    else
        log_success "SSL certificates found"
    fi
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p backups
    mkdir -p ssl/certs
    mkdir -p ssl/private
    
    # Set proper permissions
    chmod 755 logs backups
    chmod 700 ssl/private
    chmod 755 ssl/certs
    
    log_success "Directories created"
}

# Deploy services
deploy_services() {
    log_info "Deploying services for $DOMAIN..."
    
    # Stop existing services
    log_info "Stopping existing services..."
    docker compose -f $COMPOSE_FILE down || true
    
    # Pull latest images
    log_info "Pulling latest images..."
    docker compose -f $COMPOSE_FILE pull || true
    
    # Build services
    log_info "Building services..."
    docker compose -f $COMPOSE_FILE build
    
    # Start database and redis first
    log_info "Starting database and redis..."
    docker compose -f $COMPOSE_FILE up -d postgres redis
    
    # Wait for database
    log_info "Waiting for database to be ready..."
    sleep 15
    
    # Start backend services
    log_info "Starting backend services..."
    docker compose -f $COMPOSE_FILE up -d backend celery_worker celery_beat
    
    # Wait for backend
    log_info "Waiting for backend to be ready..."
    sleep 10
    
    # Start microservices
    log_info "Starting microservices..."
    docker compose -f $COMPOSE_FILE up -d account_service api_gateway dashboard_dealer_service
    
    # Wait for API gateway
    log_info "Waiting for API gateway to be ready..."
    sleep 15
    
    # Start web application
    log_info "Starting web application..."
    docker compose -f $COMPOSE_FILE up -d web_app
    
    # Start analytics and admin panels
    log_info "Starting analytics and admin panels..."
    docker compose -f $COMPOSE_FILE up -d analytics_dashboard admin_panel
    
    log_success "Services deployed successfully"
}

# Health checks
run_health_checks() {
    log_info "Running health checks..."
    
    local max_attempts=30
    local attempt=1
    
    # Check web application
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:5000/health &> /dev/null; then
            log_success "Web application is healthy"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Web application health check failed"
            return 1
        fi
        
        log_info "Attempt $attempt/$max_attempts: Web application not ready..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    # Check API gateway
    if curl -f http://localhost:8080/health &> /dev/null; then
        log_success "API gateway is healthy"
    else
        log_warning "API gateway health check failed"
    fi
    
    # Check backend
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "Backend is healthy"
    else
        log_warning "Backend health check failed"
    fi
    
    log_success "Health checks completed"
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Start monitoring services
    docker compose -f $COMPOSE_FILE up -d prometheus grafana
    
    log_success "Monitoring services started"
}

# Show deployment information
show_deployment_info() {
    log_info "Deployment Information for $DOMAIN:"
    echo "=================================================="
    echo "🌐 Web Application: https://$DOMAIN:5000"
    echo "🔌 API Gateway: https://$DOMAIN:8080"
    echo "⚙️  Backend API: https://$DOMAIN:8000"
    echo "📊 Analytics Dashboard: https://$DOMAIN:8501"
    echo "🛠️  Admin Panel: https://$DOMAIN:8502"
    echo "📈 Grafana: https://$DOMAIN:3000"
    echo "🔍 Prometheus: https://$DOMAIN:9090"
    echo ""
    echo "Local Development URLs:"
    echo "🌐 Web Application: http://localhost:5000"
    echo "🔌 API Gateway: http://localhost:8080"
    echo "⚙️  Backend API: http://localhost:8000"
    echo "📊 Analytics Dashboard: http://localhost:8501"
    echo "🛠️  Admin Panel: http://localhost:8502"
    echo ""
    echo "Management Commands:"
    echo "📋 View logs: docker compose logs -f"
    echo "🔄 Restart services: docker compose restart"
    echo "🛑 Stop services: docker compose down"
    echo "🗑️  Clean up: docker compose down -v --remove-orphans"
    echo "=================================================="
}

# Main execution
main() {
    log_info "Starting production deployment for $DOMAIN..."
    
    check_permissions
    check_dependencies
    setup_environment
    create_directories
    setup_ssl
    deploy_services
    run_health_checks
    setup_monitoring
    show_deployment_info
    
    log_success "Production deployment for $DOMAIN completed successfully! 🎉"
    log_info "Please update your DNS records to point $DOMAIN to this server's IP address."
    log_warning "Remember to replace self-signed certificates with proper SSL certificates for production use."
}

# Run main function
main "$@"
