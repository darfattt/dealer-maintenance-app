# Backend Microservices Deployment Guide

This guide covers deployment options for the backend microservices architecture.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │ Account Service │    │ Future Services │
│   Port: 8080    │    │   Port: 8100    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   Port: 5432    │
                    └─────────────────┘
```

## Quick Start

### 1. Production Deployment (Docker Compose)

```bash
# Clone and setup
git clone <repository>
cd backend-microservices

# Make scripts executable
chmod +x scripts/*.sh

# Run setup script
./scripts/setup.sh
```

### 2. Development Setup

```bash
# Setup development environment
./scripts/dev-setup.sh

# Run services individually
cd services/account
source venv/bin/activate
python main.py

# In another terminal
cd api-gateway
source venv/bin/activate
python main.py
```

## Environment Configuration

### Account Service (.env)

```env
# Database
DATABASE_URL=postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Service
SERVICE_NAME=account-service
SERVICE_VERSION=1.0.0
LOG_LEVEL=INFO
ENVIRONMENT=production

# Admin User
ADMIN_EMAIL=admin@dealer-dashboard.com
ADMIN_PASSWORD=admin123
ADMIN_FULL_NAME=System Administrator
```

### API Gateway (.env)

```env
# Gateway
GATEWAY_PORT=8080
GATEWAY_HOST=0.0.0.0

# Services
ACCOUNT_SERVICE_URL=http://account-service:8100
DEALER_DASHBOARD_SERVICE_URL=http://localhost:8000

# JWT (must match account service)
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-this-in-production
JWT_ALGORITHM=HS256

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## Database Setup

### Schema Structure

- `account`: User management and authentication
- `dealer_integration`: Existing dealer dashboard data

### Migrations

```bash
# Account service migrations
cd services/account
source venv/bin/activate

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## Security Configuration

### JWT Security

1. **Change JWT Secret**: Update `JWT_SECRET_KEY` in production
2. **Token Expiration**: Configure appropriate token lifetimes
3. **HTTPS Only**: Use HTTPS in production

### Database Security

1. **Strong Passwords**: Use strong database passwords
2. **Network Security**: Restrict database access
3. **SSL/TLS**: Enable SSL for database connections

### API Gateway Security

1. **Rate Limiting**: Configure appropriate rate limits
2. **CORS**: Configure CORS for your frontend domains
3. **Request Validation**: Enable request validation

## Monitoring and Logging

### Centralized Logging

All services use structured JSON logging:

```json
{
  "timestamp": "2025-06-15T10:30:00Z",
  "level": "INFO",
  "service": "account-service",
  "message": "User login successful",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Health Checks

- Account Service: `GET http://localhost:8100/api/v1/health`
- API Gateway: `GET /health`
- Database: Built-in PostgreSQL health checks

### Metrics Collection

Services expose metrics for monitoring:

- Request count and duration
- Error rates
- Database connection pool status
- JWT token validation metrics

## Scaling Considerations

### Horizontal Scaling

1. **Stateless Services**: All services are stateless
2. **Load Balancing**: Use load balancer in front of API Gateway
3. **Database Scaling**: Consider read replicas for high load

### Performance Optimization

1. **Connection Pooling**: Configured for database connections
2. **Caching**: Redis available for session/data caching
3. **Async Processing**: FastAPI with async/await support

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U dealer_user dealer_dashboard > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U dealer_user dealer_dashboard < backup.sql
```

### Configuration Backup

- Environment files
- Docker Compose configuration
- SSL certificates

## Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check logs
   docker-compose logs account-service
   
   # Check health
   curl http://localhost:8100/api/v1/health
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL
   docker-compose exec postgres pg_isready -U dealer_user
   
   # Check connection from service
   docker-compose exec account-service python -c "from utils.database import check_database_health; print(check_database_health())"
   ```

3. **Authentication Issues**
   ```bash
   # Check JWT configuration
   # Ensure JWT_SECRET_KEY matches between services
   
   # Test login
   curl -X POST http://localhost:8080/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@dealer-dashboard.com","password":"admin123"}'
   ```

### Log Analysis

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f account-service

# Search logs
docker-compose logs account-service | grep ERROR
```

## Service URLs

### Development
- **API Gateway**: http://localhost:8080
- **Account Service**: http://localhost:8100
- **API Docs (Gateway)**: http://localhost:8080/docs
- **API Docs (Account)**: http://localhost:8100/docs

### Database
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Production Checklist

- [ ] Change default passwords
- [ ] Update JWT secret key
- [ ] Configure HTTPS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test disaster recovery
- [ ] Security audit
- [ ] Performance testing
- [ ] Documentation review
