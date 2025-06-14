# 🏗️ Dealer Dashboard - Split Architecture

This project implements a **split service architecture** for the Dealer Dashboard Analytics application, separating concerns into independent services.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Split Service Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Analytics Dashboard (Port 8501)                            │
│  ├─ Direct Database Connection                                  │
│  ├─ Real-time Charts & Metrics                                 │
│  ├─ Cached Data (5min TTL)                                     │
│  └─ Read-only Operations                                        │
│                                                                 │
│  ⚙️ Admin Panel (Port 8502)                                     │
│  ├─ API-based Communication                                     │
│  ├─ Dealer Management                                           │
│  ├─ Job Execution & Monitoring                                  │
│  └─ Configuration Management                                     │
│                                                                 │
│  🔧 Backend API (Port 8000)                                     │
│  ├─ RESTful API Endpoints                                       │
│  ├─ Business Logic                                              │
│  ├─ Database Operations                                         │
│  └─ Job Orchestration                                           │
│                                                                 │
│  🔄 Celery Worker                                               │
│  ├─ Background Job Processing                                   │
│  ├─ Data Fetching from DGI API                                 │
│  ├─ Database Updates                                            │
│  └─ Error Handling & Logging                                   │
│                                                                 │
│  💾 PostgreSQL Database                                         │
│  ├─ Dealers, Prospects, Units                                  │
│  ├─ Job Logs & Configuration                                   │
│  └─ Centralized Data Storage                                   │
│                                                                 │
│  🔴 Redis                                                       │
│  ├─ Celery Message Broker                                      │
│  ├─ Task Queue Management                                      │
│  └─ Result Backend                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Service Separation Benefits

### 📊 **Analytics Dashboard (Port 8501)**
- **Direct DB Access**: Faster data retrieval, no API overhead
- **Real-time Updates**: Live charts and metrics
- **Independent Scaling**: Can scale separately from admin functions
- **Optimized Queries**: Database-level optimizations for analytics
- **Caching**: Built-in data caching for performance

### ⚙️ **Admin Panel (Port 8502)**
- **API-based**: Consistent with microservice architecture
- **Job Management**: Centralized job execution and monitoring
- **Security**: API-level authentication and authorization
- **Audit Trail**: All operations logged through API
- **Flexibility**: Easy to replace or extend admin functionality

## 🚀 Quick Start

### Option 1: Automated Script (Recommended)
```bash
# Windows
start_split.bat

# Linux/Mac
python start_split_services.py
```

### Option 2: Docker Compose
```bash
docker-compose -f docker-compose.split.yml up -d
```

### Option 3: Manual Setup
```bash
# 1. Start external services
docker run -d --name postgres -p 5432:5432 \
  -e POSTGRES_DB=dealer_dashboard \
  -e POSTGRES_USER=dealer_user \
  -e POSTGRES_PASSWORD=dealer_pass \
  postgres:15-alpine

docker run -d --name redis -p 6379:6379 redis:7-alpine

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup sample data
python insert_sample_data.py more

# 4. Start services (separate terminals):
uvicorn main:app --reload --host 0.0.0.0 --port 8000
celery -A celery_app worker --loglevel=info
streamlit run dashboard_analytics.py --server.port 8501
streamlit run admin_app.py --server.port 8502
```

## 🌐 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| 📊 **Analytics Dashboard** | http://localhost:8501 | Charts, metrics, data visualization |
| ⚙️ **Admin Panel** | http://localhost:8502 | Dealer management, job execution |
| 🔧 **Backend API** | http://localhost:8000 | RESTful API endpoints |
| 📚 **API Documentation** | http://localhost:8000/docs | Swagger/OpenAPI docs |
| 📈 **Health Check** | http://localhost:8000/health | Service health status |

## 📊 Analytics Dashboard Features

### **Direct Database Connection**
- ✅ **Real-time Data**: Direct queries to PostgreSQL
- ✅ **Optimized Performance**: Database-level aggregations
- ✅ **Caching**: 5-minute TTL for expensive queries
- ✅ **Independent**: No dependency on API service

### **Analytics Features**
- 📈 **Daily Prospect Trends**: Line charts showing daily counts
- 📊 **Status Distribution**: Pie charts for prospect statuses
- 🏍️ **Unit Type Analysis**: Bar charts for unit preferences
- 🔢 **Key Metrics**: Total, recent, and active prospects
- 🕒 **Recent Activity**: Latest data fetch operations

### **User Experience**
- 🔄 **Auto-refresh**: Data updates every 5 minutes
- 📱 **Responsive**: Works on desktop and mobile
- 🎨 **Modern UI**: Clean, professional design
- ⚡ **Fast Loading**: Optimized queries and caching

## ⚙️ Admin Panel Features

### **Dealer Management**
- ➕ **Add Dealers**: Create new dealer accounts
- 📋 **View Dealers**: List all active dealers
- 🔧 **API Configuration**: Set DGI API credentials
- ✅ **Status Management**: Activate/deactivate dealers

### **Job Execution**
- 🚀 **Manual Jobs**: Run data fetch jobs on-demand
- 📅 **Date Range**: Specify custom date ranges
- 🔄 **Real-time Monitoring**: Watch job progress live
- 📊 **Progress Tracking**: Visual progress indicators

### **Job History**
- 📋 **Execution Logs**: Complete job history
- 🔍 **Filtering**: Filter by dealer, status, date
- 📈 **Metrics**: Success rates, duration statistics
- 🚨 **Error Tracking**: Detailed error messages

### **Configuration**
- ⚙️ **System Settings**: API endpoints, database URLs
- 🔧 **Future Features**: Scheduling, notifications

## 🔧 Technical Implementation

### **Analytics Dashboard (dashboard_analytics.py)**
```python
# Direct database connection
@st.cache_resource
def get_database_connection():
    engine = create_engine(DATABASE_URL)
    return sessionmaker(bind=engine)

# Cached analytics queries
@st.cache_data(ttl=300)
def get_prospect_analytics(dealer_id):
    # Direct SQL queries for performance
    return analytics_data
```

### **Admin Panel (admin_app.py)**
```python
# API-based operations
def run_manual_job(dealer_id, from_time, to_time):
    response = requests.post(f"{BACKEND_URL}/jobs/run", json=payload)
    return response.json()

# Real-time job monitoring
def monitor_job_progress(task_id):
    # Poll job status and update UI
    pass
```

## 📊 Data Flow

### **Analytics Dashboard Flow**
```
User Request → Streamlit → Direct DB Query → Cache → Charts → User
```

### **Admin Panel Flow**
```
User Action → Streamlit → API Request → Backend → Database → Response → UI Update
```

### **Job Execution Flow**
```
Admin Panel → API → Celery Task → DGI API → Database → Job Log → Admin Panel
```

## 🔒 Security & Performance

### **Security**
- 🔐 **Database**: Connection string with credentials
- 🛡️ **API**: CORS configuration for cross-origin requests
- 🔑 **Environment**: Sensitive data in environment variables

### **Performance**
- ⚡ **Caching**: 5-minute TTL for analytics queries
- 🚀 **Direct DB**: No API overhead for analytics
- 📊 **Optimized Queries**: Database-level aggregations
- 🔄 **Connection Pooling**: Efficient database connections

## 🧪 Testing the Split Architecture

### **1. Test Analytics Dashboard**
```bash
# Open analytics dashboard
http://localhost:8501

# Verify:
- Dealer selection works
- Charts display data
- Metrics are accurate
- Data refreshes properly
```

### **2. Test Admin Panel**
```bash
# Open admin panel
http://localhost:8502

# Verify:
- Dealer management works
- Job execution functions
- Job history displays
- Real-time monitoring works
```

### **3. Test Independence**
```bash
# Stop admin panel
# Analytics dashboard should still work

# Stop analytics dashboard  
# Admin panel should still work
```

## 🗄️ Database Structure & Migrations

### **Latest Dealers Table Structure**
```sql
CREATE TABLE dealers (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    dealer_name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) NULL,
    api_token VARCHAR(255) NULL,
    secret_key VARCHAR(255) NULL,  -- NEW FIELD
    is_active BOOLEAN NULL DEFAULT true,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT dealers_dealer_id_key UNIQUE (dealer_id),
    CONSTRAINT dealers_pkey PRIMARY KEY (id)
);
```

### **Sample Dealer Data**
The system includes a sample dealer for testing:
- **Dealer ID**: `12284`
- **UUID**: `e3a18c82-c500-450f-b6e1-5c5fbe68bf41`
- **Name**: `Sample Dealer`
- **Purpose**: Testing and development

### **Database Migration**

#### **New Installation**
```bash
# Use Docker Compose (includes latest schema)
docker-compose up -d

# Or manual setup with updated init.sql
psql -U dealer_user -d dealer_dashboard -f docker/init.sql
```

#### **Existing Installation**
```bash
# Run migration script (recommended)
python scripts/run_migrations.py

# Or manual migration
psql -U dealer_user -d dealer_dashboard -f docker/migrations/001_add_secret_key_and_sample_dealer.sql
```

#### **Migration Features**
- ✅ **Safe Updates**: Preserves existing data
- ✅ **Automatic Tracking**: Prevents duplicate migrations
- ✅ **Verification**: Confirms successful changes
- ✅ **Rollback Safe**: Non-destructive operations

## 🔄 Migration from Monolithic

If migrating from the original single dashboard:

1. **Backup Data**: Export existing data
2. **Run Database Migration**: Update schema with new fields
3. **Deploy Split Services**: Use provided scripts
4. **Update Bookmarks**: New URLs for each service
5. **Train Users**: Different URLs for different functions

## 🚀 Deployment Options

### **Development**
- Use provided scripts for local development
- Services run on localhost with different ports

### **Production**
- Use Docker Compose for container deployment
- Configure reverse proxy (nginx) for single domain
- Set up proper environment variables
- Configure monitoring and logging

## 📈 Monitoring & Maintenance

### **Health Checks**
- Analytics Dashboard: `http://localhost:8501/_stcore/health`
- Admin Panel: `http://localhost:8502/_stcore/health`
- Backend API: `http://localhost:8000/health`

### **Logs**
- Each service logs to its own terminal/container
- Centralized logging can be configured for production

### **Performance Monitoring**
- Database query performance
- API response times
- Cache hit rates
- Job execution metrics

## 🎯 Benefits Summary

✅ **Separation of Concerns**: Analytics vs Administration  
✅ **Independent Scaling**: Scale services based on usage  
✅ **Performance**: Direct DB access for analytics  
✅ **Maintainability**: Easier to update individual services  
✅ **User Experience**: Specialized interfaces for different users  
✅ **Reliability**: Service failures don't affect other services  

This split architecture provides a robust, scalable foundation for the Dealer Dashboard system while maintaining the simplicity of the original design.
