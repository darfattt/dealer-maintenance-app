#!/bin/bash

# Unified startup script for all Dealer Dashboard services
# This script starts both the existing monolithic services and new microservices

set -e

echo "🚀 Starting Dealer Dashboard - Complete System"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please review and update .env file with your configuration"
fi

# Build and start all services
echo "🏗️  Building and starting all services..."
echo "This includes:"
echo "  📊 Main Backend (Port 8000)"
echo "  👤 Account Service (Port 8100)" 
echo "  🌐 API Gateway (Port 8080)"
echo "  📈 Analytics Dashboard (Port 8501)"
echo "  ⚙️  Admin Panel (Port 8502)"
echo "  🗄️  PostgreSQL (Port 5432)"
echo "  🔴 Redis (Port 6379)"
echo "  📊 Prometheus (Port 9090)"
echo "  📊 Grafana (Port 3000)"
echo ""

docker-compose up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 45

echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U dealer_user -d dealer_dashboard; then
    echo "✅ PostgreSQL is healthy"
else
    echo "❌ PostgreSQL is not healthy"
    echo "📋 PostgreSQL logs:"
    docker-compose logs postgres | tail -20
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis is not healthy"
fi

# Check Main Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Main Backend is healthy"
else
    echo "❌ Main Backend is not healthy"
    echo "📋 Backend logs:"
    docker-compose logs backend | tail -10
fi

# Check Account Service
if curl -f http://localhost:8100/api/v1/health > /dev/null 2>&1; then
    echo "✅ Account Service is healthy"
else
    echo "❌ Account Service is not healthy"
    echo "📋 Account Service logs:"
    docker-compose logs account_service | tail -10
fi

# Check API Gateway
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ API Gateway is healthy"
else
    echo "❌ API Gateway is not healthy"
    echo "📋 API Gateway logs:"
    docker-compose logs api_gateway | tail -10
fi

# Check Analytics Dashboard
if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "✅ Analytics Dashboard is healthy"
else
    echo "❌ Analytics Dashboard is not healthy"
fi

# Check Admin Panel
if curl -f http://localhost:8502/_stcore/health > /dev/null 2>&1; then
    echo "✅ Admin Panel is healthy"
else
    echo "❌ Admin Panel is not healthy"
fi

echo ""
echo "🎉 Dealer Dashboard System Started!"
echo ""
echo "🌐 Access Points:"
echo "=================================="
echo "  🌐 API Gateway (Unified API):     http://localhost:8080"
echo "  📚 API Gateway Docs:              http://localhost:8080/docs"
echo ""
echo "  📊 Main Backend (Legacy):         http://localhost:8000"
echo "  👤 Account Service:               http://localhost:8100"
echo "  📚 Account Service Docs:          http://localhost:8100/docs"
echo ""
echo "  📈 Analytics Dashboard:           http://localhost:8501"
echo "  ⚙️  Admin Panel:                  http://localhost:8502"
echo ""
echo "  📊 Prometheus (Metrics):          http://localhost:9090"
echo "  📊 Grafana (Monitoring):          http://localhost:3000"
echo ""
echo "🗄️  Database Access:"
echo "=================================="
echo "  🗄️  PostgreSQL:                   localhost:5432"
echo "  🔴 Redis:                         localhost:6379"
echo ""
echo "🔐 Default Credentials:"
echo "=================================="
echo "  👤 Admin User:"
echo "     📧 Email:    admin@dealer-dashboard.com"
echo "     🔑 Password: admin123"
echo ""
echo "  📊 Grafana:"
echo "     👤 Username: admin"
echo "     🔑 Password: admin"
echo ""
echo "📋 Management Commands:"
echo "=================================="
echo "  🛑 Stop all services:    docker-compose down"
echo "  📋 View logs:            docker-compose logs -f"
echo "  📋 View specific logs:   docker-compose logs -f [service_name]"
echo "  🔄 Restart service:      docker-compose restart [service_name]"
echo "  🏗️  Rebuild service:      docker-compose up -d --build [service_name]"
echo ""
echo "📖 Available Services:"
echo "=================================="
echo "  backend, account_service, api_gateway"
echo "  analytics_dashboard, admin_panel"
echo "  postgres, redis, prometheus, grafana"
echo "  celery_worker, celery_beat"
