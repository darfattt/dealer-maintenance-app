# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a **hybrid dealer dashboard system** combining monolithic and microservices patterns. The system processes automotive dealer data through multiple interfaces:

- **Hybrid Architecture**: Legacy monolithic backend + modern microservices
- **Multiple Frontends**: Vue.js web app, Streamlit analytics dashboard, admin panel
- **Database Strategy**: Shared PostgreSQL with schema isolation (`account`, `dealer_integration`)
- **Message Queue**: Redis for Celery background processing
- **API Gateway**: Routes requests between services with authentication middleware

## Key Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| Vue.js Web App | 5000 | Main authenticated dashboard |
| API Gateway | 8080 | Unified API entry point |
| Account Service | 8100 | JWT authentication & user management |
| Dashboard Service | 8200 | Analytics data aggregation |
| Backend API | 8000 | Legacy FastAPI endpoints |
| Analytics Dashboard | 8501 | Streamlit charts (direct DB access) |
| Admin Panel | 8502 | Management interface (API-based) |
| PostgreSQL | 5432 | Shared database |
| Redis | 6379 | Celery message broker |

## Common Development Commands

### Start Full System
```bash
# Quick start (all services)
./start.sh              # Linux/macOS
start.bat               # Windows
make start              # Using Makefile

# Development mode (database only)
make dev
```

### Build and Deploy
```bash
# Build all containers
make build
docker-compose build

# Production deployment
./build-production.sh v1.0.0
./deploy-aws.sh ec2
```

### Service Management
```bash
# Check status
./status.sh             # Linux/macOS  
status.bat              # Windows
make status

# View logs
docker-compose logs -f [service_name]
make logs

# Stop services
docker-compose down
make stop
```

### Testing
```bash
# Backend tests
pytest tests/ -v

# Microservices tests
cd backend-microservices
./scripts/test.sh

# Web app tests
cd web
npm run lint
```

### Frontend Development
```bash
cd web
npm run dev             # Development server
npm run build           # Production build
npm run lint            # ESLint
```

## Authentication Architecture

**JWT-based authentication** with role hierarchy:
- `SUPER_ADMIN`: Full system access
- `DEALER_ADMIN`: Single dealer access  
- `DEALER_USER`: Limited dealer access via `users_dealer` table

Authentication flows through:
1. Account Service (port 8100) - JWT generation
2. API Gateway (port 8080) - Token validation middleware
3. Frontend stores tokens in localStorage with auto-refresh

## Database Schema Structure

### Account Schema (`account`)
- `users` - User authentication and roles
- `users_dealer` - Many-to-many user-dealer relationships

### Dealer Integration Schema (`dealer_integration`)
- `dealers` - Dealer configuration and API credentials
- `billing_process_data` - Invoice and payment data
- `unit_inbound_data` - Vehicle inventory data
- Various process tables (prospect, leasing, etc.)

## Key Data Flow Patterns

1. **Web App → API Gateway → Account Service** (authentication)
2. **Web App → API Gateway → Backend API** (business logic)
3. **Analytics Dashboard → Direct PostgreSQL** (performance optimization)
4. **Admin Panel → Backend API** (management operations)
5. **Celery Workers → DGI API → PostgreSQL** (background data fetching)

## Code Architecture Patterns

### Backend Services
- **FastAPI** with dependency injection
- **SQLAlchemy ORM** with Base classes
- **Pydantic** for request/response schemas
- **Alembic** for database migrations
- **Celery** for background tasks

### Frontend Architecture
- **Vue 3 Composition API** with Pinia stores
- **PrimeVue** UI components with Aura theme
- **Axios** for HTTP with interceptors
- **Vue Router** for navigation
- **Tailwind CSS** + SCSS for styling

### API Design
- RESTful endpoints with `/api/v1/` prefix
- JWT Bearer token authentication
- Consistent error response format
- Rate limiting via API Gateway
- CORS configured for frontend origins

## Development Workflow

1. **Start Database**: `docker-compose up -d postgres redis`
2. **Run Backend Services**: Individual terminals for each service
3. **Frontend Development**: `cd web && npm run dev` 
4. **Test Changes**: Run relevant test suites
5. **Check Types**: Use linting commands before commits

## Important File Locations

### Configuration
- `docker-compose.yml` - Full service orchestration
- `backend-microservices/docker-compose.yml` - Microservices only
- `.env` files in each service directory
- `web/vite.config.mjs` - Frontend build configuration

### Models & Schema
- `backend-microservices/services/account/app/models/user.py` - User models
- `backend/models/schemas.py` - Legacy database models
- `backend-microservices/utils/database.py` - Shared database utilities

### API Routes
- `backend-microservices/api-gateway/main.py` - Request routing
- `backend-microservices/services/account/app/routes/` - Auth endpoints
- `backend/controllers/` - Legacy business logic

### Frontend Components
- `web/src/stores/auth.js` - Authentication state management
- `web/src/service/ApiService.js` - HTTP client configuration
- `web/src/components/dashboard/` - Chart and widget components

## Deployment Notes

- **Development**: Uses local Docker Compose
- **Production**: Multi-stage Docker builds with nginx
- **AWS**: Automated deployment scripts for EC2
- **Database**: PostgreSQL with connection pooling
- **Monitoring**: Prometheus + Grafana stack included
- **Health Checks**: All services have `/health` endpoints