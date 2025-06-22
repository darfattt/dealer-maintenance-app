#!/bin/bash

echo ""
echo "========================================"
echo "  📊 Dealer Dashboard Platform Status"
echo "========================================"
echo ""

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker version >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

echo -e "${BLUE}🔍 Service Status:${NC}"
echo ""

# Check each service group
echo -e "${CYAN}📦 Infrastructure:${NC}"
docker-compose ps postgres redis 2>/dev/null
echo ""

echo -e "${CYAN}🔧 Backend Services:${NC}"
docker-compose ps backend celery_worker celery_beat 2>/dev/null
echo ""

echo -e "${CYAN}🌐 Microservices:${NC}"
docker-compose ps account_service api_gateway dashboard_dealer_service 2>/dev/null
echo ""

echo -e "${CYAN}🎨 Frontend Applications:${NC}"
docker-compose ps web_app analytics_dashboard admin_panel 2>/dev/null
echo ""

echo -e "${CYAN}📈 Monitoring:${NC}"
docker-compose ps prometheus grafana 2>/dev/null
echo ""

echo -e "${BLUE}🌐 Service Health Checks:${NC}"
echo ""

# Health checks with colored output
check_service() {
    local url=$1
    local name=$2
    
    if curl -f "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $name: ${BLUE}$url${NC}"
    else
        echo -e "${RED}❌ $name: ${BLUE}$url${NC}"
    fi
}

check_service "http://localhost:5000" "Web App"
check_service "http://localhost:8080/health" "API Gateway"
check_service "http://localhost:8000/health" "Backend API"
check_service "http://localhost:8501" "Analytics"
check_service "http://localhost:8502" "Admin Panel"
check_service "http://localhost:3000" "Grafana"

echo ""
echo -e "${CYAN}📋 Quick Actions:${NC}"
echo -e "   📋 View all logs: ${YELLOW}docker-compose logs -f${NC}"
echo -e "   🔄 Restart all: ${YELLOW}docker-compose restart${NC}"
echo -e "   🛑 Stop all: ${YELLOW}docker-compose down${NC}"
echo ""

echo -e "${GREEN}Status check complete!${NC}"
