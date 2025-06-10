#!/bin/bash

# Dealer Dashboard Startup Script

echo "🚀 Starting Dealer Dashboard Analytics..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

# Create logs directory
mkdir -p logs

# Copy .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env .env.backup 2>/dev/null || true
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U dealer_user > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis is not ready"
fi

# Check Backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is ready"
else
    echo "❌ Backend API is not ready"
fi

# Check Dashboard
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ Dashboard is ready"
else
    echo "❌ Dashboard is not ready"
fi

echo ""
echo "🎉 Dealer Dashboard is starting up!"
echo ""
echo "📊 Dashboard: http://localhost:8501"
echo "🔧 API Docs: http://localhost:8000/docs"
echo "📈 Prometheus: http://localhost:9090"
echo "📊 Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "📋 To view logs: docker-compose logs -f [service_name]"
echo "🛑 To stop: docker-compose down"
echo ""

# Show logs for a few seconds
echo "📋 Recent logs:"
docker-compose logs --tail=20
