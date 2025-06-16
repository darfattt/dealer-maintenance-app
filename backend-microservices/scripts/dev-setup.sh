#!/bin/bash

# Development setup script for individual service development

set -e

echo "🛠️  Development Setup for Backend Microservices"
echo "=============================================="

# Function to setup a service
setup_service() {
    local service_name=$1
    local service_path=$2
    
    echo "📦 Setting up $service_name..."
    
    cd "$service_path"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment for $service_name"
        python -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing dependencies for $service_name"
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        echo "Creating .env file for $service_name"
        cp .env.example .env
    fi
    
    echo "✅ $service_name setup completed"
    
    cd - > /dev/null
}

# Setup Account Service
setup_service "Account Service" "services/account"

# Setup API Gateway
echo "📦 Setting up API Gateway..."
cd "api-gateway"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment for API Gateway"
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies for API Gateway"
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file for API Gateway"
    cp .env.example .env
fi

echo "✅ API Gateway setup completed"

cd - > /dev/null

# Start only PostgreSQL and Redis for development
echo "🗄️  Starting database services..."
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check PostgreSQL health
if docker-compose exec -T postgres pg_isready -U dealer_user -d dealer_dashboard; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
    exit 1
fi

echo ""
echo "🎉 Development setup completed!"
echo ""
echo "To run services individually:"
echo ""
echo "Account Service:"
echo "  cd services/account"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "API Gateway:"
echo "  cd api-gateway"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Database services are running:"
echo "  🗄️  PostgreSQL: localhost:5432"
echo "  🔴 Redis:       localhost:6379"
echo ""
echo "To stop database services: docker-compose down"
