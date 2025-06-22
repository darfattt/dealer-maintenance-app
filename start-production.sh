#!/bin/bash

# =============================================================================
# DEALER DASHBOARD - PRODUCTION STARTUP SCRIPT
# =============================================================================
# This script starts the production deployment of Dealer Dashboard

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
COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE=".env"
BACKUP_DIR="./backups"
LOG_DIR="./logs"

echo ""
echo -e "${BLUE}========================================"
echo -e "  🚀 Starting Dealer Dashboard Production"
echo -e "========================================${NC}"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check Docker
    if ! docker version >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if ! docker-compose version >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker Compose is not installed${NC}"
        exit 1
    fi
    
    # Check compose file
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Production compose file not found: $COMPOSE_FILE${NC}"
        exit 1
    fi
    
    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}❌ Environment file not found: $ENV_FILE${NC}"
        echo -e "${YELLOW}💡 Copy .env.production to .env and update with your values${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Function to validate environment
validate_environment() {
    echo -e "${BLUE}🔍 Validating environment configuration...${NC}"
    
    # Source environment file
    export $(cat $ENV_FILE | grep -v '^#' | xargs)
    
    # Check critical variables
    critical_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "JWT_SECRET_KEY"
        "ADMIN_PASSWORD"
    )
    
    for var in "${critical_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo -e "${RED}❌ Critical environment variable $var is not set${NC}"
            exit 1
        fi
        
        # Check if using default/weak values
        case "$var" in
            "POSTGRES_PASSWORD"|"REDIS_PASSWORD"|"ADMIN_PASSWORD")
                if [[ "${!var}" == *"password"* ]] || [[ "${!var}" == *"123"* ]] || [ ${#!var} -lt 8 ]; then
                    echo -e "${YELLOW}⚠️ Warning: $var appears to be weak or default${NC}"
                fi
                ;;
            "JWT_SECRET_KEY")
                if [ ${#!var} -lt 32 ]; then
                    echo -e "${RED}❌ JWT_SECRET_KEY must be at least 32 characters${NC}"
                    exit 1
                fi
                ;;
        esac
    done
    
    echo -e "${GREEN}✅ Environment validation passed${NC}"
}

# Function to create directories
create_directories() {
    echo -e "${BLUE}📁 Creating required directories...${NC}"
    
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$LOG_DIR"
    
    # Set proper permissions
    chmod 755 "$BACKUP_DIR"
    chmod 755 "$LOG_DIR"
    
    echo -e "${GREEN}✅ Directories created${NC}"
}

# Function to backup existing data
backup_data() {
    if docker ps -q -f name=dealer_postgres_prod >/dev/null 2>&1; then
        echo -e "${YELLOW}💾 Creating database backup...${NC}"
        
        BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).sql"
        
        docker exec dealer_postgres_prod pg_dump -U dealer_user dealer_dashboard > "$BACKUP_FILE"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Database backup created: $BACKUP_FILE${NC}"
        else
            echo -e "${YELLOW}⚠️ Database backup failed (this is normal for first run)${NC}"
        fi
    fi
}

# Function to pull latest images
pull_images() {
    echo -e "${BLUE}📥 Pulling latest images...${NC}"
    
    docker-compose -f "$COMPOSE_FILE" pull
    
    echo -e "${GREEN}✅ Images pulled${NC}"
}

# Function to start services
start_services() {
    echo -e "${BLUE}🚀 Starting production services...${NC}"
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    echo -e "${GREEN}✅ Services started${NC}"
}

# Function to wait for services
wait_for_services() {
    echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
    
    # Wait for database
    echo -e "${YELLOW}📊 Waiting for database...${NC}"
    timeout 60 bash -c 'until docker exec dealer_postgres_prod pg_isready -U dealer_user; do sleep 2; done'
    
    # Wait for Redis
    echo -e "${YELLOW}🔄 Waiting for Redis...${NC}"
    timeout 60 bash -c 'until docker exec dealer_redis_prod redis-cli --no-auth-warning -a $REDIS_PASSWORD ping; do sleep 2; done'
    
    # Wait for backend services
    services=(
        "http://localhost:8000/health:Backend API"
        "http://localhost:8080/health:API Gateway"
        "http://localhost:8100/api/v1/health:Account Service"
        "http://localhost:5000:Web App"
    )
    
    for service in "${services[@]}"; do
        url="${service%:*}"
        name="${service#*:}"
        echo -e "${YELLOW}🔍 Waiting for $name...${NC}"
        
        timeout 120 bash -c "until curl -f $url >/dev/null 2>&1; do sleep 5; done" || {
            echo -e "${YELLOW}⚠️ $name may still be starting${NC}"
        }
    done
    
    echo -e "${GREEN}✅ Services are ready${NC}"
}

# Function to show service status
show_status() {
    echo -e "${BLUE}📊 Service Status:${NC}"
    echo ""
    
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    echo -e "${CYAN}🌐 Access URLs:${NC}"
    echo -e "  🎨 Web App: ${BLUE}http://localhost:5000${NC}"
    echo -e "  📊 Analytics: ${BLUE}http://localhost:8501${NC}"
    echo -e "  ⚙️ Admin Panel: ${BLUE}http://localhost:8502${NC}"
    echo -e "  🚪 API Gateway: ${BLUE}http://localhost:8080${NC}"
    echo -e "  🔧 Backend API: ${BLUE}http://localhost:8000/docs${NC}"
    echo ""
}

# Function to show logs
show_logs() {
    echo -e "${CYAN}📋 Recent logs:${NC}"
    echo ""
    
    docker-compose -f "$COMPOSE_FILE" logs --tail=10
}

# Function to setup monitoring
setup_monitoring() {
    echo -e "${BLUE}📈 Setting up monitoring...${NC}"
    
    # Create monitoring script
    cat > monitor-services.sh << 'EOF'
#!/bin/bash
# Simple monitoring script for production services

COMPOSE_FILE="docker-compose.production.yml"
LOG_FILE="./logs/monitor.log"

check_service() {
    local service=$1
    local url=$2
    
    if curl -f "$url" >/dev/null 2>&1; then
        echo "$(date): ✅ $service is healthy" >> "$LOG_FILE"
    else
        echo "$(date): ❌ $service is down" >> "$LOG_FILE"
        # Restart service
        docker-compose -f "$COMPOSE_FILE" restart "$service"
    fi
}

# Check services
check_service "web_app" "http://localhost:5000"
check_service "backend" "http://localhost:8000/health"
check_service "api_gateway" "http://localhost:8080/health"
check_service "account_service" "http://localhost:8100/api/v1/health"

# Clean old logs (keep last 1000 lines)
tail -n 1000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
EOF
    
    chmod +x monitor-services.sh
    
    echo -e "${GREEN}✅ Monitoring setup complete${NC}"
    echo -e "${YELLOW}💡 Add to crontab: */5 * * * * /path/to/monitor-services.sh${NC}"
}

# Function to show management commands
show_management() {
    echo ""
    echo -e "${CYAN}🔧 Management Commands:${NC}"
    echo -e "  📋 View logs: ${YELLOW}docker-compose -f $COMPOSE_FILE logs -f [service]${NC}"
    echo -e "  🔄 Restart service: ${YELLOW}docker-compose -f $COMPOSE_FILE restart [service]${NC}"
    echo -e "  🛑 Stop all: ${YELLOW}docker-compose -f $COMPOSE_FILE down${NC}"
    echo -e "  📊 Service status: ${YELLOW}docker-compose -f $COMPOSE_FILE ps${NC}"
    echo -e "  💾 Database backup: ${YELLOW}docker exec dealer_postgres_prod pg_dump -U dealer_user dealer_dashboard > backup.sql${NC}"
    echo -e "  🔍 Monitor: ${YELLOW}./monitor-services.sh${NC}"
    echo ""
    echo -e "${PURPLE}🚨 Emergency Commands:${NC}"
    echo -e "  🔄 Full restart: ${YELLOW}docker-compose -f $COMPOSE_FILE down && docker-compose -f $COMPOSE_FILE up -d${NC}"
    echo -e "  🧹 Clean restart: ${YELLOW}docker-compose -f $COMPOSE_FILE down -v && docker-compose -f $COMPOSE_FILE up -d${NC}"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    validate_environment
    create_directories
    backup_data
    pull_images
    start_services
    wait_for_services
    show_status
    setup_monitoring
    show_management
    
    echo -e "${GREEN}🎉 Production deployment started successfully!${NC}"
    echo -e "${CYAN}💡 Monitor logs with: docker-compose -f $COMPOSE_FILE logs -f${NC}"
}

# Handle script arguments
case "${1:-start}" in
    "start")
        main
        ;;
    "stop")
        echo -e "${YELLOW}🛑 Stopping production services...${NC}"
        docker-compose -f "$COMPOSE_FILE" down
        echo -e "${GREEN}✅ Services stopped${NC}"
        ;;
    "restart")
        echo -e "${YELLOW}🔄 Restarting production services...${NC}"
        docker-compose -f "$COMPOSE_FILE" down
        sleep 5
        main
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    *)
        echo -e "${CYAN}Usage: $0 {start|stop|restart|status|logs}${NC}"
        exit 1
        ;;
esac
