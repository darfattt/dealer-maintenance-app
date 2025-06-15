# Backend Microservices

This directory contains the microservices architecture for the dealer dashboard system.

## Architecture Overview

```
backend-microservices/
├── services/
│   ├── account/           # User authentication and authorization service
│   └── dealer-dashboard/  # Main dealer dashboard service (future migration)
├── utils/                 # Shared utilities between services
├── api-gateway/          # API Gateway for routing and load balancing
└── docker/               # Docker configurations for development and production
```

## Services

### Account Service
- **Port**: 8100
- **Database Schema**: `account`
- **Responsibilities**:
  - User authentication (JWT)
  - User management
  - Role-based access control (SUPER_ADMIN, DEALER_ADMIN)
  - Password management

### API Gateway
- **Port**: 8080
- **Responsibilities**:
  - Route requests to appropriate services
  - Load balancing
  - Authentication middleware
  - Rate limiting
  - CORS handling

## Development Setup

1. **Start all services with Docker Compose**:
   ```bash
   cd backend-microservices
   docker-compose up -d
   ```

2. **Individual service development**:
   ```bash
   cd services/account
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```

## Database Schemas

- `account`: User management and authentication
- `dealer_integration`: Existing dealer dashboard data (from main backend)

## API Endpoints

### Account Service (via API Gateway)
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `GET /api/v1/users` - List users (admin only)
- `POST /api/v1/users` - Create user (admin only)
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)

## Environment Variables

Create `.env` file in each service directory:

```env
# Database
DATABASE_URL=postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Service
SERVICE_NAME=account-service
SERVICE_VERSION=1.0.0
LOG_LEVEL=INFO

# API Gateway
API_GATEWAY_URL=http://localhost:8080
```

## Logging

All services use centralized logging with structured JSON format:
- Development: Console output with colored formatting
- Production: JSON logs for log aggregation systems

## Security

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM

## Testing

Each service includes:
- Unit tests with pytest
- Integration tests
- API endpoint tests
- Database tests with test fixtures
