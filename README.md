# 🏢 Dealer Dashboard Analytics - 3-Folder Architecture

A comprehensive dealer dashboard system with **3-folder application architecture** featuring independent Backend API, Analytics Dashboard, and Admin Panel applications with perfect separation of concerns.

## 📁 Project Structure

```
dealer-dashboard/
├── 📄 Core Application Files
│   ├── admin_app.py              # Admin panel (modular architecture)
│   ├── dashboard_analytics.py    # Analytics dashboard
│   ├── main.py                   # FastAPI backend
│   ├── database.py               # Database models
│   ├── celery_app.py             # Celery configuration
│   └── requirements.txt          # Python dependencies
│
├── 🧩 Components (Modular Admin Panel)
│   ├── components/
│   │   ├── api_utils.py          # API communication utilities
│   │   ├── navigation.py         # Navigation and routing
│   │   ├── dealer_management.py  # Dealer CRUD operations
│   │   ├── run_jobs.py           # Job execution components
│   │   ├── job_history.py        # Job history and analytics
│   │   └── configuration.py      # System configuration
│
├── 🐳 Docker & Infrastructure
│   ├── docker/
│   │   ├── Dockerfile            # Application container
│   │   ├── docker-compose.yml    # Main deployment (split architecture)
│   │   ├── docker-compose.simple.yml  # Simple deployment
│   │   ├── docker-compose.split.yml   # Split architecture
│   │   ├── init.sql              # Database initialization
│   │   └── monitoring/           # Prometheus & Grafana configs
│
├── 📜 Scripts & Utilities
│   ├── scripts/
│   │   ├── start*.bat            # Windows startup scripts
│   │   ├── start*.py             # Python startup scripts
│   │   ├── dev_setup.py          # Development setup
│   │   ├── fix_pandas_issues.py  # Pandas compatibility fixes
│   │   └── insert_sample_data.py # Sample data generation
│
├── 🧪 Tests
│   ├── tests/
│   │   ├── test_api.py           # API endpoint tests
│   │   ├── test_app.py           # Application tests
│   │   ├── test_services.py      # Service integration tests
│   │   └── quick_test.py         # Quick functionality tests
│
├── 📚 Documentation
│   ├── docs/
│   │   ├── README.md             # Main documentation
│   │   ├── MODULAR_ARCHITECTURE.md  # Architecture guide
│   │   ├── ADMIN_PANEL_FEATURES.md  # Admin panel features
│   │   ├── TROUBLESHOOTING.md    # Issue resolution guide
│   │   ├── DEV_GUIDE.md          # Development guide
│   │   └── api-specs/            # API specifications
│
├── 🔧 Utilities & Tasks
│   ├── tasks/                    # Celery background tasks
│   ├── utils/                    # Utility functions
│   └── logs/                     # Application logs
│
└── 🚀 Quick Start
    ├── start.bat                 # Main startup script
    ├── docker-compose.yml        # Main deployment config
    └── Makefile                  # Build automation
```

## 🚀 Quick Start

### Option 1: One-Click Startup (Recommended)
```cmd
# Windows
start.bat

# The script will:
# 1. Check Docker status
# 2. Build and start all services
# 3. Verify service health
# 4. Open both dashboards
```

### Option 2: Docker Compose
```bash
# Start all services
docker-compose up -d

# Wait for services to start (2-3 minutes)
# Access the applications
```

### Option 3: Development Mode
```bash
# Use development scripts
python scripts/start_dev.py
scripts/start_dev.bat  # Windows
```

## 🌐 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| 📊 **Analytics Dashboard** | http://localhost:8501 | Real-time charts, metrics, data visualization |
| ⚙️ **Admin Panel** | http://localhost:8502 | Dealer management, job execution, configuration |
| 🔧 **Backend API** | http://localhost:8000 | RESTful endpoints, business logic |
| 📚 **API Documentation** | http://localhost:8000/docs | Swagger/OpenAPI documentation |
| 📊 **Prometheus** | http://localhost:9090 | Metrics collection and monitoring |
| 📈 **Grafana** | http://localhost:3000 | Performance dashboards (admin/admin) |

## 🏗️ Architecture Overview

```
📊 Analytics Dashboard (8501)          ⚙️ Admin Panel (8502)
├─ Direct Database Connection          ├─ API-based Communication
├─ Real-time Charts & Metrics          ├─ Modular Components
├─ Cached Queries (5min TTL)           ├─ Dealer Management
├─ Independent Service                 ├─ Job Execution & Monitoring
└─ Optimized Performance               └─ Job History & Configuration
                    │                                │
                    └────────────────┬───────────────┘
                                     │
                            🔧 Backend API (8000)
                            ├─ RESTful Endpoints
                            ├─ Business Logic
                            ├─ Job Orchestration
                            └─ Database Operations
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
            💾 PostgreSQL      🔴 Redis        📊 Monitoring
            ├─ Dealers         ├─ Job Queue    ├─ Prometheus (9090)
            ├─ Prospects       ├─ Results      └─ Grafana (3000)
            └─ Job Logs        └─ Cache
```

## ⚙️ Admin Panel Features (Modular Architecture)

### **🖱️ Clickable Navigation**
- Button-based sidebar navigation
- Visual feedback for current page
- Persistent state management

### **🏢 Dealer Management**
- ✅ **View Dealers**: Interactive list with status indicators
- ✅ **Add Dealers**: Form-based creation with validation
- ✅ **Edit Dealers**: Pre-populated forms with update functionality
- ✅ **Quick Edit**: Direct edit access from dealer list

### **🚀 Job Execution**
- ✅ **Single Dealer Jobs**: Individual dealer job execution
- ✅ **Bulk Operations**: Run jobs for all active dealers
- ✅ **Real-time Monitoring**: Progress tracking and status updates
- ✅ **Results Display**: Comprehensive success/failure reporting

### **📋 Job History**
- ✅ **Execution Logs**: Filterable job history display
- ✅ **Performance Metrics**: Success rates and analytics
- ✅ **Search & Filter**: Advanced filtering capabilities
- ✅ **Data Export**: CSV export functionality

## 📊 Analytics Dashboard Features

### **Direct Database Connection**
- ✅ **Real-time Data**: Direct PostgreSQL queries for maximum performance
- ✅ **Optimized Queries**: Database-level aggregations and indexing
- ✅ **Smart Caching**: 5-minute TTL for expensive analytics operations
- ✅ **Independent Operation**: Works without API dependencies

### **Visualization Features**
- 📈 **Daily Prospect Trends**: Line charts showing prospect counts over time
- 📊 **Status Distribution**: Pie charts for prospect status breakdown
- 🏍️ **Unit Type Analysis**: Bar charts for motorcycle unit preferences
- 🔢 **Key Metrics**: Total, recent, and active prospect counts

## 🛠️ Development

### **Local Development**
```bash
# Start development environment
python scripts/start_dev.py

# Or use specific scripts
python scripts/dev_setup.py
scripts/start_split.bat  # Windows
```

### **Testing**
```bash
# Run all tests
python tests/test_services.py

# Insert sample data
python scripts/insert_sample_data.py more

# Fix common issues
python scripts/fix_pandas_issues.py
```

### **Docker Development**
```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f [service_name]

# Stop services
docker-compose down
```

## 🔧 API Integration

### **Honda DGI API**
- **Endpoint**: `https://dev-gvt-gateway.eksad.com/dgi-api/v1.3/prsp/read`
- **Authentication**: API Key + Token per dealer
- **Data**: Prospect information, customer details, unit preferences
- **Fallback**: Intelligent dummy data generation for development/demo

## 📋 Troubleshooting

### **Common Issues**
- **Pandas DataFrame Errors**: Run `python scripts/fix_pandas_issues.py`
- **Port Conflicts**: Check `docker ps` and stop conflicting services
- **Database Connection**: Verify PostgreSQL is running and accessible

### **Service Health Checks**
```bash
# Check all services
python tests/test_services.py

# Individual service checks
curl http://localhost:8000/health
curl http://localhost:8501/_stcore/health
curl http://localhost:8502/_stcore/health
```

### **Log Analysis**
```bash
# View service logs
docker-compose logs -f analytics_dashboard
docker-compose logs -f admin_panel
docker-compose logs -f backend
```

## 🎯 Benefits of Clean Structure

✅ **Organization**: Clear separation of concerns with logical folder structure  
✅ **Maintainability**: Easy to locate and modify specific functionality  
✅ **Scalability**: Modular components can be developed independently  
✅ **Testing**: Isolated test files for focused testing  
✅ **Documentation**: Centralized documentation for easy reference  
✅ **Deployment**: Clean Docker configuration management  

## 📞 Support

For issues, questions, or contributions:
1. Check the troubleshooting guide: `docs/TROUBLESHOOTING.md`
2. Review service logs for error details
3. Test individual services using scripts in `tests/`
4. Consult API documentation at `/docs` endpoint

---

**🎉 Your clean, organized dealer dashboard is ready for production use!**
