# 🚀 Dealer Dashboard Startup Scripts

This directory contains startup scripts for the Dealer Dashboard Full Stack Platform.

## 📋 Available Scripts

### Windows
- **`start.bat`** - Windows batch script for starting the platform

### Linux/macOS
- **`start.sh`** - Bash script for starting the platform

## 🌐 Platform Architecture

The platform includes the following services:

### Main Applications
- **🎨 Web Dashboard** (Port 5000) - Vue.js with PrimeVue UI
- **📊 Analytics Dashboard** (Port 8501) - Streamlit data visualization
- **⚙️ Admin Panel** (Port 8502) - Streamlit management interface

### API Services
- **🚪 API Gateway** (Port 8080) - Microservices router
- **🔐 Account Service** (Port 8100) - Authentication & authorization
- **📈 Dashboard Service** (Port 8200) - Analytics data aggregation
- **🔧 Backend API** (Port 8000) - Main FastAPI backend

### Infrastructure
- **🗄️ PostgreSQL** (Port 5432) - Primary database
- **🔄 Redis** (Port 6379) - Cache and message broker
- **⚡ Celery Worker** - Background task processing
- **📅 Celery Beat** - Task scheduling

### Monitoring
- **📊 Grafana** (Port 3000) - Metrics visualization (admin/admin)
- **📈 Prometheus** (Port 9090) - Metrics collection

## 🚀 Quick Start

### Windows
```cmd
# Double-click or run from command prompt
start.bat
```

### Linux/macOS
```bash
# Make executable (first time only)
chmod +x start.sh

# Run the script
./start.sh
```

## 📋 What the Scripts Do

1. **Check Docker** - Verify Docker is running
2. **Build Services** - Build all Docker containers
3. **Start Platform** - Launch all services with docker-compose
4. **Health Checks** - Verify services are responding
5. **Open Applications** - Launch web browsers (optional)

## 🔧 Manual Commands

### Start Platform
```bash
docker-compose up -d --build
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web_app
docker-compose logs -f api_gateway
docker-compose logs -f account_service
```

### Stop Platform
```bash
docker-compose down
```

### Restart Service
```bash
docker-compose restart web_app
```

## 🌐 Access URLs

After startup, access these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **Main Web App** | http://localhost:5000 | Vue.js Dashboard |
| **Analytics** | http://localhost:8501 | Streamlit Charts |
| **Admin Panel** | http://localhost:8502 | Management Interface |
| **API Gateway** | http://localhost:8080 | API Router |
| **Backend API** | http://localhost:8000/docs | FastAPI Documentation |
| **Grafana** | http://localhost:3000 | Monitoring (admin/admin) |
| **Prometheus** | http://localhost:9090 | Metrics Collection |

## 🛠️ Troubleshooting

### Docker Not Running
- **Windows**: Start Docker Desktop
- **Linux**: `sudo systemctl start docker`

### Port Conflicts
Check if ports are already in use:
```bash
# Windows
netstat -an | findstr :5000

# Linux/macOS
lsof -i :5000
```

### Service Not Starting
Check logs for specific service:
```bash
docker-compose logs service_name
```

### Reset Everything
```bash
# Stop and remove all containers
docker-compose down -v

# Remove all images (optional)
docker system prune -a

# Start fresh
./start.sh  # or start.bat
```

## 📊 Development Mode

For development with hot reload:

### Web App (Vue.js)
```bash
cd web
npm run dev
# Access at http://localhost:5173
```

### Backend API
```bash
cd backend
uvicorn main:app --reload
# Access at http://localhost:8000
```

## 🔐 Default Credentials

### Grafana
- **Username**: admin
- **Password**: admin

### Database
- **Host**: localhost:5432
- **Database**: dealer_dashboard
- **Username**: dealer_user
- **Password**: dealer_pass

## 📝 Notes

- First startup may take 5-10 minutes to build all containers
- Web application may take additional time to compile on first run
- All services run in Docker containers for consistency
- Data persists in Docker volumes between restarts

## 🆘 Support

If you encounter issues:

1. Check Docker is running and has sufficient resources
2. Ensure no other services are using the required ports
3. Review logs using `docker-compose logs -f`
4. Try restarting with `docker-compose restart`
5. For complete reset, use `docker-compose down -v` and restart
