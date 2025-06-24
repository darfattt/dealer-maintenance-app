# AWS Update & Rebuild Guide

## Overview
This guide explains how to update and rebuild the Dealer Dashboard application deployed on AWS EC2 using the `update-aws.sh` script.

## Prerequisites
- AWS EC2 instance is running and accessible
- SSH key file (`dealer-dashboard-key.pem`) in current directory
- Application is deployed using the `deploy-aws.sh` script

## Server Configuration
- **Server Host**: `ec2-52-87-205-153.compute-1.amazonaws.com`
- **SSH Key**: `dealer-dashboard-key.pem`
- **Project Directory**: `dealer-dashboard`
- **Compose File**: `docker-compose.production.yml`

## Available Commands

### 1. Check Status
```bash
./update-aws.sh status
```
**What it does:**
- Shows running Docker containers
- Displays disk usage
- Shows memory usage
- Tests SSH connectivity

### 2. Restart Services
```bash
./update-aws.sh restart
```
**What it does:**
- Stops all running containers
- Starts all containers again
- No code updates or rebuilds

**Use when:**
- Services are stuck or unresponsive
- Need to restart without code changes
- Quick service refresh

### 3. Update Code & Restart
```bash
./update-aws.sh update
```
**What it does:**
- Pulls latest code from git repository
- Stops running containers
- Starts containers with new code
- Uses existing Docker images

**Use when:**
- Code changes in repository
- Configuration file updates
- Regular updates with minor changes

### 4. Rebuild Containers
```bash
./update-aws.sh rebuild
```
**What it does:**
- Pulls latest code from git repository
- Stops running containers
- Rebuilds Docker images from scratch
- Starts containers with new images

**Use when:**
- Dependency changes (package.json, requirements.txt)
- Dockerfile modifications
- Major code changes requiring new builds

### 5. Full Rebuild (Clean Everything)
```bash
./update-aws.sh full-rebuild
```
**What it does:**
- Pulls latest code from git repository
- Stops and removes all containers and volumes
- Cleans Docker system (removes unused images, networks)
- Rebuilds everything from scratch
- Starts fresh containers

**Use when:**
- Database schema changes
- Persistent storage issues
- Complete environment reset needed
- Troubleshooting complex issues

### 6. View Logs
```bash
./update-aws.sh logs
```
**What it does:**
- Shows recent logs from all services
- Displays last 50 lines of combined logs

**Use when:**
- Debugging issues
- Monitoring service health
- Checking error messages

## Command Comparison

| Command | Code Update | Container Rebuild | Volume Reset | Use Case |
|---------|-------------|-------------------|--------------|----------|
| `status` | ❌ | ❌ | ❌ | Check health |
| `restart` | ❌ | ❌ | ❌ | Quick restart |
| `update` | ✅ | ❌ | ❌ | Code changes |
| `rebuild` | ✅ | ✅ | ❌ | Dependencies |
| `full-rebuild` | ✅ | ✅ | ✅ | Complete reset |
| `logs` | ❌ | ❌ | ❌ | Debugging |

## Customization

### Environment Variables
```bash
# Custom server
SERVER_HOST=my-server.com ./update-aws.sh update

# Custom key file
KEY_PAIR_NAME=my-key ./update-aws.sh rebuild

# Custom project directory
PROJECT_DIR=my-project ./update-aws.sh update
```

### Configuration Options
- `SERVER_HOST`: Server address (default: ec2-52-87-205-153.compute-1.amazonaws.com)
- `KEY_PAIR_NAME`: SSH key name (default: dealer-dashboard-key)
- `PROJECT_DIR`: Project directory (default: dealer-dashboard)
- `COMPOSE_FILE`: Docker compose file (default: docker-compose.production.yml)

## Service Access URLs

After successful deployment/update:
- **Web Application**: http://ec2-52-87-205-153.compute-1.amazonaws.com:5000
- **Analytics Dashboard**: http://ec2-52-87-205-153.compute-1.amazonaws.com:8501
- **Admin Panel**: http://ec2-52-87-205-153.compute-1.amazonaws.com:8502
- **API Gateway**: http://ec2-52-87-205-153.compute-1.amazonaws.com:8080

## Troubleshooting

### Common Issues

**1. SSH Connection Failed**
```bash
# Check if key file exists and has correct permissions
ls -la dealer-dashboard-key.pem
chmod 400 dealer-dashboard-key.pem
```

**2. Git Pull Failed**
- Script continues with existing code
- Manually check repository access
- Verify git configuration on server

**3. Services Won't Start**
```bash
# Check logs for errors
./update-aws.sh logs

# Try full rebuild
./update-aws.sh full-rebuild
```

**4. Port Conflicts**
- Check if ports are already in use
- Verify security group settings
- Review docker-compose port mappings

### Manual SSH Commands
```bash
# SSH into server
ssh -i dealer-dashboard-key.pem ec2-user@ec2-52-87-205-153.compute-1.amazonaws.com

# Check Docker status
docker ps

# View specific service logs
docker-compose -f docker-compose.production.yml logs [service-name]

# Manual restart
cd dealer-dashboard
docker-compose -f docker-compose.production.yml restart
```

## Best Practices

### Regular Maintenance
1. **Daily**: Check status
2. **Weekly**: Update code if changes exist
3. **Monthly**: Full rebuild for health

### Before Updates
1. Check current status
2. Backup important data if needed
3. Verify git repository has latest changes
4. Test in development environment first

### After Updates
1. Check service status
2. Verify all services are running
3. Test application functionality
4. Monitor logs for errors

## Update Workflow Example

```bash
# 1. Check current status
./update-aws.sh status

# 2. Update code (most common)
./update-aws.sh update

# 3. If issues, check logs
./update-aws.sh logs

# 4. If still issues, try rebuild
./update-aws.sh rebuild

# 5. Last resort: full rebuild
./update-aws.sh full-rebuild
```

## Emergency Procedures

### Service Down
1. `./update-aws.sh status` - Check what's running
2. `./update-aws.sh restart` - Quick restart
3. `./update-aws.sh logs` - Check for errors
4. `./update-aws.sh rebuild` - If restart fails

### Complete Failure
1. `./update-aws.sh full-rebuild` - Nuclear option
2. If still failing, check AWS console
3. Verify security groups and network settings
4. Consider redeploying with `deploy-aws.sh`

## Script Location
The `update-aws.sh` script is located in the project root directory alongside `deploy-aws.sh`.