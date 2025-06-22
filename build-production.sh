#!/bin/bash

# =============================================================================
# DEALER DASHBOARD - PRODUCTION BUILD SCRIPT
# =============================================================================
# This script builds all Docker images for production deployment
# Usage: ./build-production.sh [version]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
VERSION=${1:-latest}
REGISTRY=${DOCKER_REGISTRY:-""}
PROJECT_NAME="dealer-dashboard"

echo ""
echo -e "${BLUE}========================================"
echo -e "  🏗️ Building Dealer Dashboard Production Images"
echo -e "  📦 Version: ${VERSION}"
echo -e "  🏷️ Registry: ${REGISTRY:-"local"}"
echo -e "========================================${NC}"
echo ""

# Function to build and tag image
build_image() {
    local service=$1
    local context=$2
    local dockerfile=$3
    local image_name="${PROJECT_NAME}-${service}"
    
    if [ ! -z "$REGISTRY" ]; then
        image_name="${REGISTRY}/${image_name}"
    fi
    
    echo -e "${YELLOW}🔨 Building ${service}...${NC}"
    
    if [ -z "$dockerfile" ]; then
        docker build -t "${image_name}:${VERSION}" -t "${image_name}:latest" \
            --target production \
            "${context}"
    else
        docker build -t "${image_name}:${VERSION}" -t "${image_name}:latest" \
            --target production \
            -f "${dockerfile}" \
            "${context}"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ ${service} built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build ${service}${NC}"
        exit 1
    fi
    
    echo ""
}

# Function to check if Docker is running
check_docker() {
    if ! docker version >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker is running${NC}"
}

# Function to create production environment file if it doesn't exist
setup_env() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️ No .env file found. Creating from template...${NC}"
        if [ -f ".env.production" ]; then
            cp .env.production .env
            echo -e "${YELLOW}📝 Please edit .env file with your production values${NC}"
            echo -e "${YELLOW}🔐 Update passwords, secrets, and domain names${NC}"
        else
            echo -e "${RED}❌ No .env.production template found${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Environment file exists${NC}"
    fi
}

# Function to validate environment
validate_env() {
    echo -e "${BLUE}🔍 Validating environment...${NC}"
    
    # Source environment file
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    # Check required variables
    required_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "JWT_SECRET_KEY"
        "ADMIN_PASSWORD"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo -e "${RED}❌ Required environment variable ${var} is not set${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✅ Environment validation passed${NC}"
}

# Function to build all images
build_all_images() {
    echo -e "${BLUE}🏗️ Building all production images...${NC}"
    echo ""
    
    # Backend services
    build_image "backend" "./backend" ""
    build_image "account-service" "./backend-microservices" "./docker/Dockerfile.account"
    build_image "api-gateway" "./backend-microservices" "./docker/Dockerfile.gateway"
    build_image "dashboard-dealer-service" "./backend-microservices" "./docker/Dockerfile.dashboard-dealer"
    
    # Frontend services
    build_image "web-app" "./web" ""
    build_image "analytics-dashboard" "./dashboard_analytics" ""
    build_image "admin-panel" "./admin_panel" ""
}

# Function to push images to registry
push_images() {
    if [ -z "$REGISTRY" ]; then
        echo -e "${YELLOW}⚠️ No registry specified, skipping push${NC}"
        return
    fi
    
    echo -e "${BLUE}📤 Pushing images to registry...${NC}"
    
    services=(
        "backend"
        "account-service"
        "api-gateway"
        "dashboard-dealer-service"
        "web-app"
        "analytics-dashboard"
        "admin-panel"
    )
    
    for service in "${services[@]}"; do
        image_name="${REGISTRY}/${PROJECT_NAME}-${service}"
        echo -e "${YELLOW}📤 Pushing ${service}...${NC}"
        
        docker push "${image_name}:${VERSION}"
        docker push "${image_name}:latest"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ ${service} pushed successfully${NC}"
        else
            echo -e "${RED}❌ Failed to push ${service}${NC}"
            exit 1
        fi
    done
}

# Function to create deployment package
create_deployment_package() {
    echo -e "${BLUE}📦 Creating deployment package...${NC}"
    
    PACKAGE_NAME="dealer-dashboard-${VERSION}.tar.gz"
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    DEPLOY_DIR="${TEMP_DIR}/dealer-dashboard-deploy"
    
    mkdir -p "${DEPLOY_DIR}"
    
    # Copy deployment files
    cp docker-compose.production.yml "${DEPLOY_DIR}/docker-compose.yml"
    cp .env.production "${DEPLOY_DIR}/.env.template"
    cp -r docker/init.sql "${DEPLOY_DIR}/"
    cp -r backend-microservices/docker/init-db.sql "${DEPLOY_DIR}/"
    
    # Copy scripts
    mkdir -p "${DEPLOY_DIR}/scripts"
    cp deploy-aws.sh "${DEPLOY_DIR}/scripts/" 2>/dev/null || true
    cp start-production.sh "${DEPLOY_DIR}/scripts/" 2>/dev/null || true
    
    # Create README for deployment
    cat > "${DEPLOY_DIR}/README.md" << EOF
# Dealer Dashboard Production Deployment

## Quick Start
1. Copy .env.template to .env and update with your values
2. Run: docker-compose up -d
3. Access: http://your-domain.com:5000

## Services
- Web App: Port 5000
- API Gateway: Port 8080
- Analytics: Port 8501
- Admin Panel: Port 8502

## Documentation
See main repository for full documentation.
EOF
    
    # Create package
    cd "${TEMP_DIR}"
    tar -czf "${PACKAGE_NAME}" dealer-dashboard-deploy/
    mv "${PACKAGE_NAME}" "${OLDPWD}/"
    
    # Cleanup
    rm -rf "${TEMP_DIR}"
    
    echo -e "${GREEN}✅ Deployment package created: ${PACKAGE_NAME}${NC}"
}

# Function to show summary
show_summary() {
    echo ""
    echo -e "${GREEN}🎉 Production build completed successfully!${NC}"
    echo ""
    echo -e "${CYAN}📋 Built Images:${NC}"
    
    services=(
        "backend"
        "account-service"
        "api-gateway"
        "dashboard-dealer-service"
        "web-app"
        "analytics-dashboard"
        "admin-panel"
    )
    
    for service in "${services[@]}"; do
        image_name="${PROJECT_NAME}-${service}"
        if [ ! -z "$REGISTRY" ]; then
            image_name="${REGISTRY}/${image_name}"
        fi
        echo -e "  📦 ${image_name}:${VERSION}"
    done
    
    echo ""
    echo -e "${CYAN}🚀 Next Steps:${NC}"
    echo -e "  1. Update .env file with production values"
    echo -e "  2. Deploy using: docker-compose -f docker-compose.production.yml up -d"
    echo -e "  3. Or use AWS deployment script: ./deploy-aws.sh"
    echo ""
}

# Main execution
main() {
    check_docker
    setup_env
    validate_env
    build_all_images
    
    # Push to registry if specified
    if [ ! -z "$REGISTRY" ]; then
        push_images
    fi
    
    create_deployment_package
    show_summary
}

# Run main function
main "$@"
