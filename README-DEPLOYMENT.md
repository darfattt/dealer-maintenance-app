# 🚀 Production Deployment Guide

Complete guide for building Docker images and deploying the Dealer Dashboard platform to production servers, including AWS.

## 📋 Quick Start

### 1. Build Production Images
```bash
# Linux/macOS
chmod +x build-production.sh
./build-production.sh v1.0.0

# Windows
build-production.bat v1.0.0
```

### 2. Deploy to AWS
```bash
# Automated AWS deployment
chmod +x deploy-aws.sh
./deploy-aws.sh ec2
```

### 3. Start Production Services
```bash
# On your server
chmod +x start-production.sh
./start-production.sh
```

## 📦 Available Scripts

### Build Scripts
- **`build-production.sh`** - Linux/macOS production build
- **`build-production.bat`** - Windows production build
- **Features**: Multi-stage builds, image tagging, validation

### Deployment Scripts
- **`deploy-aws.sh`** - Automated AWS EC2 deployment
- **`start-production.sh`** - Production startup and management
- **Features**: Infrastructure setup, health checks, monitoring

### Configuration Files
- **`docker-compose.production.yml`** - Production Docker Compose
- **`.env.production`** - Environment template
- **Features**: Production optimizations, security, scaling

## 🏗️ Build Process

### What Gets Built
1. **Backend Services**
   - FastAPI backend with production optimizations
   - Celery worker and beat scheduler
   - Multi-stage builds for smaller images

2. **Microservices**
   - Account service (authentication)
   - API Gateway (routing and rate limiting)
   - Dashboard dealer service (analytics)

3. **Frontend Applications**
   - Vue.js web application (optimized build)
   - Streamlit analytics dashboard
   - Streamlit admin panel

### Build Features
- ✅ **Multi-stage builds** for optimized image sizes
- ✅ **Production targets** with security hardening
- ✅ **Health checks** for all services
- ✅ **Environment validation** before build
- ✅ **Automatic tagging** with version and latest

## 🌐 AWS Deployment

### Supported Deployment Types
1. **EC2 Instance** (Ready)
   - Automated instance creation
   - Security group configuration
   - Docker installation and setup

2. **ECS/Fargate** (Coming Soon)
   - Container orchestration
   - Auto-scaling capabilities
   - Load balancer integration

### AWS Infrastructure Created
- **EC2 Instance** (t3.large recommended)
- **Security Group** with required ports
- **Key Pair** for SSH access
- **EBS Volume** for persistent storage

### Required AWS Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:*",
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🔧 Production Configuration

### Environment Variables
```bash
# Critical Security Settings
POSTGRES_PASSWORD=your_super_secure_password
REDIS_PASSWORD=your_redis_password
JWT_SECRET_KEY=your_32_character_minimum_secret
ADMIN_PASSWORD=your_admin_password

# Domain Configuration
VITE_API_BASE_URL=https://api.yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com
DOMAIN_NAME=yourdomain.com

# Performance Settings
WORKER_PROCESSES=4
CELERY_CONCURRENCY=4
LOG_LEVEL=INFO
```

### Service Ports
| Service | Port | Description |
|---------|------|-------------|
| Web App | 5000 | Vue.js Frontend |
| Backend API | 8000 | FastAPI Backend |
| API Gateway | 8080 | Microservices Router |
| Account Service | 8100 | Authentication |
| Dashboard Service | 8200 | Analytics Data |
| Analytics | 8501 | Streamlit Dashboard |
| Admin Panel | 8502 | Management Interface |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache & Message Broker |

## 📊 Production Features

### Security
- ✅ **Environment-based secrets** management
- ✅ **JWT authentication** with secure keys
- ✅ **Rate limiting** on API endpoints
- ✅ **CORS protection** with allowed origins
- ✅ **SQL injection protection** with SQLAlchemy
- ✅ **Input validation** on all endpoints

### Performance
- ✅ **Multi-worker** FastAPI deployment
- ✅ **Connection pooling** for database
- ✅ **Redis caching** for frequent queries
- ✅ **Celery background tasks** for heavy operations
- ✅ **Optimized Docker images** with multi-stage builds
- ✅ **Health checks** for all services

### Monitoring
- ✅ **Health endpoints** for all services
- ✅ **Structured logging** with configurable levels
- ✅ **Service status monitoring** script
- ✅ **Database backup** automation
- ✅ **Log rotation** and cleanup

### Scalability
- ✅ **Horizontal scaling** ready architecture
- ✅ **Load balancer** compatible
- ✅ **Database connection pooling**
- ✅ **Stateless application design**
- ✅ **Container orchestration** ready

## 🔄 Deployment Workflow

### 1. Development to Production
```bash
# 1. Test locally
docker-compose up -d

# 2. Build production images
./build-production.sh v1.0.0

# 3. Test production build locally
docker-compose -f docker-compose.production.yml up -d

# 4. Deploy to AWS
./deploy-aws.sh ec2

# 5. Configure domain and SSL
# Update DNS records and setup certificates
```

### 2. Updates and Maintenance
```bash
# Update application
git pull origin main
./build-production.sh v1.1.0

# Deploy update
ssh -i key.pem ec2-user@your-server
cd dealer-dashboard
git pull origin main
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d
```

## 🚨 Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check Docker daemon
docker version

# Clean build cache
docker system prune -a

# Check disk space
df -h
```

#### Deployment Issues
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify security group rules
aws ec2 describe-security-groups --group-names dealer-dashboard-sg

# Check instance status
aws ec2 describe-instances --instance-ids i-1234567890abcdef0
```

#### Service Issues
```bash
# Check service logs
docker-compose -f docker-compose.production.yml logs service_name

# Restart specific service
docker-compose -f docker-compose.production.yml restart service_name

# Check service health
curl http://localhost:8000/health
```

## 📞 Support

### Log Collection
```bash
# Collect deployment logs
mkdir support-logs
docker-compose -f docker-compose.production.yml logs > support-logs/services.log
docker system df > support-logs/docker-usage.log
df -h > support-logs/disk-usage.log
```

### Emergency Procedures
```bash
# Complete service restart
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d

# Database recovery
docker exec dealer_postgres_prod pg_dump -U dealer_user dealer_dashboard > emergency-backup.sql
```

## 📚 Additional Resources

- **[AWS Deployment Guide](DEPLOYMENT-AWS.md)** - Detailed AWS setup
- **[Production Configuration](docker-compose.production.yml)** - Service definitions
- **[Environment Template](.env.production)** - Configuration reference
- **[Monitoring Setup](start-production.sh)** - Health checks and monitoring

---

## 🎯 Quick Reference

### Essential Commands
```bash
# Build: ./build-production.sh v1.0.0
# Deploy: ./deploy-aws.sh ec2
# Start: ./start-production.sh
# Status: docker-compose -f docker-compose.production.yml ps
# Logs: docker-compose -f docker-compose.production.yml logs -f
```

### Access URLs (after deployment)
- **Main App**: http://your-domain:5000
- **Analytics**: http://your-domain:8501
- **Admin**: http://your-domain:8502
- **API Docs**: http://your-domain:8000/docs

### Support Contacts
- **Technical**: support@yourdomain.com
- **Emergency**: admin@yourdomain.com
