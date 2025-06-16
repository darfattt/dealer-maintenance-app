#!/bin/bash

# Setup script for backend microservices

set -e

echo "🚀 Setting up Backend Microservices"
echo "=================================="

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

# Create environment files if they don't exist
echo "📝 Creating environment files..."

# Account service .env
if [ ! -f "services/account/.env" ]; then
    echo "Creating services/account/.env"
    cp services/account/.env.example services/account/.env
fi

# API Gateway .env
if [ ! -f "api-gateway/.env" ]; then
    echo "Creating api-gateway/.env"
    cp api-gateway/.env.example api-gateway/.env
fi

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U dealer_user -d dealer_dashboard; then
    echo "✅ PostgreSQL is healthy"
else
    echo "❌ PostgreSQL is not healthy"
    exit 1
fi

# Check Account Service
if curl -f http://localhost:8100/api/v1/health > /dev/null 2>&1; then
    echo "✅ Account Service is healthy"
else
    echo "❌ Account Service is not healthy"
    exit 1
fi

# Check API Gateway
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ API Gateway is healthy"
else
    echo "❌ API Gateway is not healthy"
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Services are running on:"
echo "  📊 API Gateway:     http://localhost:8080"
echo "  👤 Account Service: http://localhost:8100"
echo "  🗄️  PostgreSQL:     localhost:5432"
echo "  🔴 Redis:           localhost:6379"
echo ""
echo "API Documentation:"
echo "  📚 API Gateway:     http://localhost:8080/docs"
echo "  📚 Account Service: http://localhost:8100/docs"
echo ""
echo "Default Admin User:"
echo "  📧 Email:    admin@dealer-dashboard.com"
echo "  🔑 Password: admin123"
echo ""
echo "To stop services: docker-compose down"
echo "To view logs:     docker-compose logs -f"
