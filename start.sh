#!/bin/bash

echo ""
echo "========================================"
echo "  🚀 Dealer Dashboard Full Stack Platform"
echo "========================================"
echo ""

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker version >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Create logs directory
mkdir -p logs

echo -e "${BLUE}🔨 Building and starting services...${NC}"
echo -e "   📦 Database & Cache (PostgreSQL, Redis)"
echo -e "   🔧 Backend Services (FastAPI, Celery)"
echo -e "   🌐 Microservices (Account, API Gateway, Dashboard)"
echo -e "   🎨 Frontend (Vue.js Web App)"
echo -e "   📊 Analytics (Streamlit Dashboards)"
echo -e "   📈 Monitoring (Prometheus, Grafana)"
echo ""

# Start with main compose file (full architecture)
docker-compose up -d --build

echo ""
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 30

echo ""
echo -e "${BLUE}🔍 Checking service status...${NC}"

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U dealer_user >/dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
else
    echo -e "${RED}❌ PostgreSQL is not ready${NC}"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is ready${NC}"
else
    echo -e "${RED}❌ Redis is not ready${NC}"
fi

# Check API Gateway
if curl -f http://localhost:8080/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ API Gateway is ready${NC}"
else
    echo -e "${RED}❌ API Gateway is not ready${NC}"
fi

# Check Web App
if curl -f http://localhost:5000 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Web Application is ready${NC}"
else
    echo -e "${RED}❌ Web Application is not ready${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Dealer Dashboard Full Stack Platform is ready!${NC}"
echo ""
echo -e "${CYAN}🌐 MAIN APPLICATIONS:${NC}"
echo -e "   🎨 Web Dashboard: ${BLUE}http://localhost:5000${NC}"
echo -e "   📊 Analytics Dashboard: ${BLUE}http://localhost:8501${NC}"
echo -e "   ⚙️ Admin Panel: ${BLUE}http://localhost:8502${NC}"
echo ""
echo -e "${CYAN}🔧 API SERVICES:${NC}"
echo -e "   🚪 API Gateway: ${BLUE}http://localhost:8080${NC}"
echo -e "   🔐 Account Service: ${BLUE}http://localhost:8100${NC}"
echo -e "   📈 Dashboard Service: ${BLUE}http://localhost:8200${NC}"
echo -e "   🔧 Backend API: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${CYAN}📈 MONITORING:${NC}"
echo -e "   📊 Grafana: ${BLUE}http://localhost:3000${NC} (admin/admin)"
echo -e "   📈 Prometheus: ${BLUE}http://localhost:9090${NC}"
echo ""
echo -e "${CYAN}📋 QUICK START:${NC}"
echo -e "   1. 🎨 Main App: ${BLUE}http://localhost:5000${NC} (Vue.js Dashboard)"
echo -e "   2. 📊 Analytics: ${BLUE}http://localhost:8501${NC} (Streamlit Charts)"
echo -e "   3. ⚙️ Admin: ${BLUE}http://localhost:8502${NC} (Management Panel)"
echo -e "   4. 📈 Monitoring: ${BLUE}http://localhost:3000${NC} (Grafana)"
echo ""
echo -e "${CYAN}📋 MANAGEMENT:${NC}"
echo -e "   📋 View logs: ${YELLOW}docker-compose logs -f [service_name]${NC}"
echo -e "   🛑 Stop all: ${YELLOW}docker-compose down${NC}"
echo -e "   🔄 Restart: ${YELLOW}docker-compose restart [service_name]${NC}"
echo ""

# Wait a bit more and then test
echo -e "${YELLOW}⏳ Final health checks...${NC}"
sleep 10

# Try to test the main application
if ! curl -f http://localhost:5000 >/dev/null 2>&1; then
    echo ""
    echo -e "${YELLOW}⚠️  Web application may still be starting. You can access it manually.${NC}"
    echo -e "    Main App: ${BLUE}http://localhost:5000${NC}"
fi

echo ""
echo -e "${GREEN}🚀 Full Stack Platform is ready!${NC}"
echo ""

# Function to open URL (works on most Linux distributions)
open_url() {
    if command -v xdg-open > /dev/null; then
        xdg-open "$1" >/dev/null 2>&1
    elif command -v gnome-open > /dev/null; then
        gnome-open "$1" >/dev/null 2>&1
    elif command -v kde-open > /dev/null; then
        kde-open "$1" >/dev/null 2>&1
    else
        echo -e "${YELLOW}Please open manually: ${BLUE}$1${NC}"
    fi
}

# Ask user if they want to open applications
echo -e "${CYAN}Would you like to open the applications in your browser? (y/n):${NC}"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo ""
    echo -e "${BLUE}🌐 Opening Web Dashboard...${NC}"
    open_url "http://localhost:5000"
    sleep 2

    echo -e "${BLUE}📊 Opening Analytics Dashboard...${NC}"
    open_url "http://localhost:8501"
    sleep 2

    echo -e "${BLUE}⚙️ Opening Admin Panel...${NC}"
    open_url "http://localhost:8502"
    sleep 2

    echo -e "${BLUE}📈 Opening Grafana Monitoring...${NC}"
    open_url "http://localhost:3000"

    echo ""
    echo -e "${GREEN}🎉 All applications are now open in your browser!${NC}"
fi

echo ""
echo -e "${PURPLE}💡 TIP: Use Ctrl+C to view logs in real-time:${NC}"
echo -e "    ${YELLOW}docker-compose logs -f web_app${NC}"
echo -e "    ${YELLOW}docker-compose logs -f api_gateway${NC}"
echo ""
echo -e "${GREEN}✨ Platform is running! Services will continue in the background.${NC}"
echo -e "${CYAN}Press Enter to exit this script...${NC}"
read -r
