# Dealer Dashboard Makefile

.PHONY: help build start stop restart logs clean test

help:
	@echo "Dealer Dashboard Analytics - Available Commands:"
	@echo ""
	@echo "  make build     - Build Docker images"
	@echo "  make start     - Start all services"
	@echo "  make stop      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - Show logs for all services"
	@echo "  make clean     - Clean up containers and volumes"
	@echo "  make test      - Run tests"
	@echo "  make dev       - Start development environment"
	@echo ""

build:
	@echo "🔨 Building Docker images..."
	docker-compose build

start:
	@echo "🚀 Starting Dealer Dashboard..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "📊 Dashboard: http://localhost:8501"
	@echo "🔧 API Docs: http://localhost:8000/docs"
	@echo "📈 Prometheus: http://localhost:9090"
	@echo "📊 Grafana: http://localhost:3000"

stop:
	@echo "🛑 Stopping services..."
	docker-compose down

restart: stop start

logs:
	@echo "📋 Showing logs..."
	docker-compose logs -f

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker system prune -f

test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

dev:
	@echo "🔧 Starting development environment..."
	docker-compose up postgres redis -d
	@echo "✅ Database and Redis started for development"
	@echo "Run the following commands in separate terminals:"
	@echo "  uvicorn main:app --reload"
	@echo "  celery -A celery_app worker --loglevel=info"
	@echo "  celery -A celery_app beat --loglevel=info"
	@echo "  streamlit run dashboard.py"

status:
	@echo "📊 Service Status:"
	@docker-compose ps
