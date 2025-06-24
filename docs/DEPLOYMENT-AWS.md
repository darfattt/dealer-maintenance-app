# 🚀 AWS Deployment Guide - Dealer Dashboard

This guide provides comprehensive instructions for deploying the Dealer Dashboard platform to AWS.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Deployment](#quick-deployment)
3. [Manual Deployment](#manual-deployment)
4. [Production Configuration](#production-configuration)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### Local Requirements
- Docker and Docker Compose
- AWS CLI configured with appropriate permissions
- Git (for cloning repository)
- SSH client

### AWS Requirements
- AWS Account with appropriate permissions
- EC2, VPC, and Security Group permissions
- (Optional) Route 53 for domain management
- (Optional) Certificate Manager for SSL

### Recommended AWS Resources
- **Instance Type**: t3.large or larger (4GB+ RAM)
- **Storage**: 20GB+ EBS volume
- **Network**: VPC with public subnet
- **Security**: Security group with required ports

## 🚀 Quick Deployment

### Option 1: Automated AWS Deployment
```bash
# 1. Clone repository
git clone https://github.com/yourusername/dealer-dashboard.git
cd dealer-dashboard

# 2. Configure AWS credentials
aws configure

# 3. Run automated deployment
chmod +x deploy-aws.sh
./deploy-aws.sh ec2

# 4. Access your application
# URLs will be displayed after deployment
```

### Option 2: One-Command Build & Deploy
```bash
# Build production images and deploy
chmod +x build-production.sh
./build-production.sh latest

# Deploy to AWS
./deploy-aws.sh ec2
```

## 🔧 Manual Deployment

### Step 1: Prepare Environment
```bash
# 1. Create environment file
cp .env.production .env

# 2. Update with your values
nano .env
```

**Critical Environment Variables:**
```bash
# Database
POSTGRES_PASSWORD=your_super_secure_password
REDIS_PASSWORD=your_redis_password

# Security
JWT_SECRET_KEY=your_32_character_minimum_secret_key
ADMIN_PASSWORD=your_admin_password

# Domain (update with your domain)
VITE_API_BASE_URL=https://api.yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com
```

### Step 2: Build Production Images
```bash
# Build all production images
chmod +x build-production.sh
./build-production.sh v1.0.0
```

### Step 3: Create AWS Infrastructure
```bash
# Create security group and key pair
aws ec2 create-security-group \
    --group-name dealer-dashboard-sg \
    --description "Dealer Dashboard Security Group"

# Add security group rules
aws ec2 authorize-security-group-ingress \
    --group-name dealer-dashboard-sg \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# Add application ports (80, 443, 5000, 8000, 8080, 8501, 8502)
for port in 80 443 5000 8000 8080 8501 8502; do
    aws ec2 authorize-security-group-ingress \
        --group-name dealer-dashboard-sg \
        --protocol tcp \
        --port $port \
        --cidr 0.0.0.0/0
done

# Create key pair
aws ec2 create-key-pair \
    --key-name dealer-dashboard-key \
    --query 'KeyMaterial' \
    --output text > dealer-dashboard-key.pem

chmod 400 dealer-dashboard-key.pem
```

### Step 4: Launch EC2 Instance
```bash
# Get latest Amazon Linux 2 AMI
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text)

# Launch instance
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type t3.large \
    --key-name dealer-dashboard-key \
    --security-groups dealer-dashboard-sg \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "Instance ID: $INSTANCE_ID"
```

### Step 5: Setup Server
```bash
# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

# SSH to server
ssh -i dealer-dashboard-key.pem ec2-user@$PUBLIC_IP

# On the server:
sudo yum update -y
sudo yum install -y docker git

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Logout and login again for group changes
exit
ssh -i dealer-dashboard-key.pem ec2-user@$PUBLIC_IP
```

### Step 6: Deploy Application
```bash
# Clone repository
git clone https://github.com/yourusername/dealer-dashboard.git
cd dealer-dashboard

# Copy environment file
cp .env.production .env
nano .env  # Update with your values

# Start production services
chmod +x start-production.sh
./start-production.sh
```

## 🔧 Production Configuration

### Domain Setup
```bash
# Update environment file
VITE_API_BASE_URL=https://api.yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DOMAIN_NAME=yourdomain.com
```

### SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo yum install -y certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Update nginx configuration (if using reverse proxy)
```

### Reverse Proxy Setup (Nginx)
```bash
# Install nginx
sudo yum install -y nginx

# Create configuration
sudo tee /etc/nginx/conf.d/dealer-dashboard.conf << 'EOF'
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Check all services
docker-compose -f docker-compose.production.yml ps

# Check specific service health
curl http://localhost:5000        # Web App
curl http://localhost:8000/health # Backend API
curl http://localhost:8080/health # API Gateway
```

### Log Management
```bash
# View all logs
docker-compose -f docker-compose.production.yml logs -f

# View specific service logs
docker-compose -f docker-compose.production.yml logs -f web_app
docker-compose -f docker-compose.production.yml logs -f backend

# Rotate logs (add to crontab)
0 2 * * * docker system prune -f
```

### Database Backup
```bash
# Manual backup
docker exec dealer_postgres_prod pg_dump -U dealer_user dealer_dashboard > backup-$(date +%Y%m%d).sql

# Automated backup script
cat > backup-database.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/ec2-user/backups"
mkdir -p $BACKUP_DIR
docker exec dealer_postgres_prod pg_dump -U dealer_user dealer_dashboard > $BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).sql
# Keep only last 7 days
find $BACKUP_DIR -name "backup-*.sql" -mtime +7 -delete
EOF

chmod +x backup-database.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /home/ec2-user/backup-database.sh" | crontab -
```

### System Updates
```bash
# Update system packages
sudo yum update -y

# Update Docker images
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d

# Clean unused images
docker system prune -f
```

## 🔧 Service Management

### Start/Stop Services
```bash
# Start all services
./start-production.sh start

# Stop all services
./start-production.sh stop

# Restart all services
./start-production.sh restart

# Check status
./start-production.sh status
```

### Individual Service Management
```bash
# Restart specific service
docker-compose -f docker-compose.production.yml restart web_app

# Scale service (if needed)
docker-compose -f docker-compose.production.yml up -d --scale celery_worker=3

# Update single service
docker-compose -f docker-compose.production.yml pull web_app
docker-compose -f docker-compose.production.yml up -d web_app
```

## 🚨 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs

# Check disk space
df -h

# Check memory
free -h

# Restart Docker
sudo systemctl restart docker
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
docker exec dealer_postgres_prod pg_isready -U dealer_user

# Reset database password
docker exec -it dealer_postgres_prod psql -U dealer_user -d dealer_dashboard
```

#### SSL Certificate Issues
```bash
# Renew Let's Encrypt certificate
sudo certbot renew

# Test certificate
sudo certbot certificates
```

### Performance Optimization
```bash
# Increase instance size if needed
# Monitor with htop
sudo yum install -y htop
htop

# Check Docker stats
docker stats

# Optimize PostgreSQL
# Edit postgresql.conf in container
```

## 📞 Support

### Log Collection for Support
```bash
# Collect all logs
mkdir support-logs
docker-compose -f docker-compose.production.yml logs > support-logs/docker-logs.txt
dmesg > support-logs/system-logs.txt
df -h > support-logs/disk-usage.txt
free -h > support-logs/memory-usage.txt

# Create archive
tar -czf support-logs-$(date +%Y%m%d).tar.gz support-logs/
```

### Emergency Contacts
- System Administrator: admin@yourdomain.com
- Technical Support: support@yourdomain.com

---

## 🎯 Quick Reference

### Service URLs
- **Web App**: http://your-ip:5000
- **Analytics**: http://your-ip:8501
- **Admin Panel**: http://your-ip:8502
- **API Gateway**: http://your-ip:8080

### Important Files
- **Environment**: `.env`
- **Compose**: `docker-compose.production.yml`
- **Logs**: `./logs/`
- **Backups**: `./backups/`

### Key Commands
```bash
# Deploy: ./deploy-aws.sh ec2
# Start: ./start-production.sh
# Status: docker-compose -f docker-compose.production.yml ps
# Logs: docker-compose -f docker-compose.production.yml logs -f
```
