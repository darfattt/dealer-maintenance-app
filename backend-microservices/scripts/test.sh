#!/bin/bash

# Test script for backend microservices

set -e

echo "🧪 Running Tests for Backend Microservices"
echo "========================================"

# Function to run tests for a service
run_service_tests() {
    local service_name=$1
    local service_path=$2
    
    echo "🔍 Testing $service_name..."
    
    cd "$service_path"
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "❌ Virtual environment not found for $service_name. Run dev-setup.sh first."
        exit 1
    fi
    
    # Run tests
    if [ -d "tests" ]; then
        echo "Running pytest for $service_name"
        pytest tests/ -v --tb=short
        echo "✅ $service_name tests completed"
    else
        echo "⚠️  No tests directory found for $service_name"
    fi
    
    cd - > /dev/null
}

# Ensure database is running for tests
echo "🗄️  Starting test database..."
docker-compose up -d postgres

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
sleep 10

# Test Account Service
run_service_tests "Account Service" "services/account"

echo ""
echo "🎉 All tests completed!"

# Optional: Stop test database
read -p "Stop test database? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down
    echo "🛑 Test database stopped"
fi
