#!/bin/bash

# =============================================================================
# DEALER DASHBOARD - AWS UPDATE/RESTART SCRIPT
# =============================================================================
# This script updates and restarts the deployed Dealer Dashboard on AWS EC2

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
SERVER_HOST=${SERVER_HOST:-"ec2-52-87-205-153.compute-1.amazonaws.com"}
KEY_PAIR_NAME=${KEY_PAIR_NAME:-"dealer-dashboard-key"}
PROJECT_DIR=${PROJECT_DIR:-"dealer-dashboard"}
COMPOSE_FILE=${COMPOSE_FILE:-"docker-compose.production.yml"}
UPDATE_TYPE=${1:-"restart"}  # restart, rebuild, full-rebuild, status

echo ""
echo -e "${BLUE}========================================="
echo -e "  🔄 AWS Update - Dealer Dashboard"
echo -e "  🖥️ Server: ${SERVER_HOST}"
echo -e "  📦 Action: ${UPDATE_TYPE}"
echo -e "=========================================${NC}"
echo ""

# Function to check if key file exists
check_key_file() {
    if [ ! -f "${KEY_PAIR_NAME}.pem" ]; then
        echo -e "${RED}❌ Key file not found: ${KEY_PAIR_NAME}.pem${NC}"
        echo -e "${YELLOW}💡 Make sure the key file is in the current directory${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Key file found${NC}"
}

# Function to test SSH connection
test_ssh_connection() {
    echo -e "${YELLOW}🔗 Testing SSH connection...${NC}"
    if ! ssh -i "${KEY_PAIR_NAME}.pem" -o ConnectTimeout=10 -o BatchMode=yes ec2-user@"${SERVER_HOST}" 'echo "Connection successful"' >/dev/null 2>&1; then
        echo -e "${RED}❌ Cannot connect to server${NC}"
        echo -e "${YELLOW}💡 Check server status and network connectivity${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ SSH connection successful${NC}"
}

# Function to show current status
show_status() {
    echo -e "${BLUE}📊 Checking current status...${NC}"
    
    echo -e "${CYAN}🐳 Docker containers:${NC}"
    ssh -i "${KEY_PAIR_NAME}.pem" ec2-user@"${SERVER_HOST}" 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"' || true
    
    echo ""
    echo -e "${CYAN}💾 Disk usage:${NC}"
    ssh -i "${KEY_PAIR_NAME}.pem" ec2-user@"${SERVER_HOST}" 'df -h /' || true
    
    echo ""
    echo -e "${CYAN}📈 Memory usage:${NC}"
    ssh -i "${KEY_PAIR_NAME}.pem" ec2-user@"${SERVER_HOST}" 'free -h' || true
}

# Function to restart services
restart_services() {
    echo -e "${YELLOW}🔄 Restarting services...${NC}"
    
    ssh -i "${KEY_PAIR_NAME}.pem" ec2-user@"${SERVER_HOST}" << 'EOF'
        cd dealer-dashboard
        echo "🛑 Stopping services..."
        docker-compose -f docker-compose.production.yml down
        echo "🚀 Starting services..."
        docker-compose -f docker-compose.production.yml up -d
        echo "✅ Services restarted"
EOF
    
    echo -e "${GREEN}✅ Services restarted successfully${NC}"
}

# Function to update and restart
update_and_restart() {
    echo -e "${YELLOW}📥 Updating code and restarting...${NC}"
    
    ssh -i "${KEY_PAIR_NAME}.pem" ec2-user@"${SERVER_HOST}" << 'EOF'
        cd dealer-dashboard
        echo "📥 Pulling latest code..."
        git pull origin main || git pull origin release/1.0.0 || echo "⚠️ Git pull failed, continuing with existing code"
        echo "🛑 Stopping services..."
        docker-compose -f docker-compose.production.yml down
        echo "🚀 Starting services..."
        docker-compose -f docker-compose.production.yml up -d
        echo "✅ Update and restart completed"
EOF
    
    echo -e "${GREEN}✅ Update and restart completed${NC}"
}

# Function to rebuild containers
rebuild_containers() {
    echo -e "${YELLOW}🔨 Rebuilding containers...${NC}"
    
    ssh -i "${KEY_PAIR_NAME}.pem" ec2-user@"${SERVER_HOST}" << 'EOF'
        cd dealer-dashboard
        echo "📥 Pulling latest code..."
        git pull origin main || git pull origin release/1.0.0 || echo "⚠️ Git pull failed, continuing with existing code"
        echo "🛑 Stopping services..."
        docker-compose -f docker-compose.production.yml down
        echo "🔨 Building containers..."
        docker-compose -f docker-compose.production.yml build --no-cache
        echo "🚀 Starting services..."
        docker-compose -f docker-compose.production.yml up -d
        echo "✅ Rebuild completed"
EOF
    
    echo -e "${GREEN}✅ Rebuild completed successfully${NC}"
}

# Function to full rebuild (clean everything)
full_rebuild() {
    echo -e "${YELLOW}🧹 Full rebuild (cleaning everything)...${NC}"
    
    ssh -i "${KEY_PAIR_NAME}.pem" ec2-user@"${SERVER_HOST}" << 'EOF'
        cd dealer-dashboard
        echo "📥 Pulling latest code..."
        git pull origin main || git pull origin release/1.0.0 || echo "⚠️ Git pull failed, continuing with existing code"
        echo "🛑 Stopping and removing everything..."
        docker-compose -f docker-compose.production.yml down -v --remove-orphans
        echo "🧹 Cleaning Docker system..."
        docker system prune -f
        docker volume prune -f
        echo "🔨 Building containers from scratch..."
        docker-compose -f docker-compose.production.yml build --no-cache --pull
        echo "🚀 Starting services..."
        docker-compose -f docker-compose.production.yml up -d
        echo "✅ Full rebuild completed"
EOF
    
    echo -e "${GREEN}✅ Full rebuild completed successfully${NC}"
}

# Function to show logs
show_logs() {
    echo -e "${BLUE}📋 Showing recent logs...${NC}"
    
    ssh -i "${KEY_PAIR_NAME}.pem" ec2-user@"${SERVER_HOST}" << 'EOF'
        cd dealer-dashboard
        echo "📋 Recent logs (last 50 lines):"
        docker-compose -f docker-compose.production.yml logs --tail=50
EOF
}

# Function to show usage
show_usage() {
    echo -e "${CYAN}Usage: $0 [action]${NC}"
    echo ""
    echo -e "${YELLOW}Actions:${NC}"
    echo -e "  status       - Show current status (default)"
    echo -e "  restart      - Restart services only"
    echo -e "  update       - Pull code and restart"
    echo -e "  rebuild      - Rebuild containers and restart"
    echo -e "  full-rebuild - Clean everything and rebuild"
    echo -e "  logs         - Show recent logs"
    echo ""
    echo -e "${YELLOW}Environment Variables:${NC}"
    echo -e "  SERVER_HOST      - Server address (default: ec2-52-87-205-153.compute-1.amazonaws.com)"
    echo -e "  KEY_PAIR_NAME    - Key pair name (default: dealer-dashboard-key)"
    echo -e "  PROJECT_DIR      - Project directory (default: dealer-dashboard)"
    echo -e "  COMPOSE_FILE     - Docker compose file (default: docker-compose.production.yml)"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  $0 status"
    echo -e "  $0 restart"
    echo -e "  $0 update"
    echo -e "  $0 rebuild"
    echo -e "  SERVER_HOST=my-server.com $0 update"
    echo ""
}

# Function to wait for services
wait_for_services() {
    echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
    sleep 10
    
    echo -e "${CYAN}🔍 Final status check:${NC}"
    ssh -i "${KEY_PAIR_NAME}.pem" ec2-user@"${SERVER_HOST}" 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
}

# Function to show access info
show_access_info() {
    echo ""
    echo -e "${GREEN}🎉 Operation completed successfully!${NC}"
    echo ""
    echo -e "${CYAN}📋 Access Information:${NC}"
    echo -e "  🌐 Web App: http://${SERVER_HOST}:5000"
    echo -e "  📊 Analytics: http://${SERVER_HOST}:8501"
    echo -e "  ⚙️ Admin Panel: http://${SERVER_HOST}:8502"
    echo -e "  🔧 API Gateway: http://${SERVER_HOST}:8080"
    echo ""
    echo -e "${CYAN}🔧 Management Commands:${NC}"
    echo -e "  📊 Status: $0 status"
    echo -e "  📋 Logs: $0 logs"
    echo -e "  🔄 Restart: $0 restart"
    echo -e "  🔨 Rebuild: $0 rebuild"
    echo ""
}

# Main execution
main() {
    case "$UPDATE_TYPE" in
        "status")
            check_key_file
            test_ssh_connection
            show_status
            ;;
        "restart")
            check_key_file
            test_ssh_connection
            restart_services
            wait_for_services
            show_access_info
            ;;
        "update")
            check_key_file
            test_ssh_connection
            update_and_restart
            wait_for_services
            show_access_info
            ;;
        "rebuild")
            check_key_file
            test_ssh_connection
            rebuild_containers
            wait_for_services
            show_access_info
            ;;
        "full-rebuild")
            check_key_file
            test_ssh_connection
            full_rebuild
            wait_for_services
            show_access_info
            ;;
        "logs")
            check_key_file
            test_ssh_connection
            show_logs
            ;;
        "help"|"-h"|"--help")
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown action: ${UPDATE_TYPE}${NC}"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"