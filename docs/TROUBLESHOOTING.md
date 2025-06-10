# 🔧 Troubleshooting Guide - Split Architecture

This guide helps resolve common issues with the split Dealer Dashboard architecture.

## 🚨 Common Issues & Solutions

### 1. **Pandas DataFrame Boolean Evaluation Error**

**Error:**
```
ValueError: The truth value of a DataFrame is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all()
```

**Cause:** Streamlit/Pandas compatibility issue when checking DataFrame truthiness.

**Solution:**
```bash
# Run the fix script
python fix_pandas_issues.py

# Or manually fix in code:
# Change: if dataframe:
# To: if len(dataframe) > 0:
```

**Manual Fix Example:**
```python
# ❌ Wrong
if df_logs:
    last_fetch = df_logs.iloc[0]

# ✅ Correct  
if len(df_logs) > 0:
    last_fetch = df_logs.iloc[0]
```

### 2. **Database Connection Issues**

**Error:** `Connection refused` or `Database not found`

**Solutions:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Start PostgreSQL if not running
docker run -d --name postgres -p 5432:5432 \
  -e POSTGRES_DB=dealer_dashboard \
  -e POSTGRES_USER=dealer_user \
  -e POSTGRES_PASSWORD=dealer_pass \
  postgres:15-alpine

# Wait for startup
sleep 10

# Test connection
python -c "import psycopg2; psycopg2.connect('postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard')"
```

### 3. **Redis Connection Issues**

**Error:** `Connection refused` on Redis

**Solutions:**
```bash
# Check if Redis is running
docker ps | grep redis

# Start Redis if not running
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Test connection
python -c "import redis; redis.Redis(host='localhost', port=6379).ping()"
```

### 4. **Port Already in Use**

**Error:** `Port 8501/8502 already in use`

**Solutions:**
```bash
# Find process using the port
netstat -ano | findstr :8501
netstat -ano | findstr :8502

# Kill the process (Windows)
taskkill /PID <process_id> /F

# Or use different ports
streamlit run dashboard_analytics.py --server.port 8503
streamlit run admin_app.py --server.port 8504
```

### 5. **Module Import Errors**

**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Solutions:**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or install specific modules
pip install streamlit pandas plotly sqlalchemy psycopg2-binary

# Check Python path
python -c "import sys; print(sys.path)"
```

### 6. **API Connection Timeout**

**Error:** Admin panel can't connect to backend API

**Solutions:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check backend logs
docker logs dealer_backend

# Restart backend
docker restart dealer_backend

# Or start manually
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. **Streamlit Cache Issues**

**Error:** Stale data or cache errors

**Solutions:**
```python
# Clear cache in Streamlit app
st.cache_data.clear()

# Or restart with cache cleared
streamlit run dashboard_analytics.py --server.port 8501 --server.runOnSave true
```

### 8. **Docker Container Issues**

**Error:** Container won't start or crashes

**Solutions:**
```bash
# Check container status
docker ps -a

# View container logs
docker logs dealer_backend
docker logs dealer_postgres

# Restart containers
docker restart dealer_backend dealer_postgres dealer_redis

# Remove and recreate if needed
docker rm -f dealer_backend
docker-compose -f docker-compose.split.yml up -d
```

## 🔍 Diagnostic Commands

### **Check Service Status**
```bash
# Check all containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check specific services
curl http://localhost:8000/health
curl http://localhost:8501/_stcore/health
curl http://localhost:8502/_stcore/health
```

### **Check Database**
```bash
# Connect to database
docker exec -it dealer_postgres psql -U dealer_user -d dealer_dashboard

# Check tables
\dt

# Check data
SELECT COUNT(*) FROM dealers;
SELECT COUNT(*) FROM prospect_data;
```

### **Check Logs**
```bash
# Backend logs
docker logs dealer_backend -f

# Database logs  
docker logs dealer_postgres -f

# Celery logs
docker logs dealer_celery_worker -f
```

## 🚀 Quick Recovery Steps

### **Complete Reset**
```bash
# Stop all services
docker stop dealer_backend dealer_postgres dealer_redis dealer_celery_worker

# Remove containers
docker rm dealer_backend dealer_postgres dealer_redis dealer_celery_worker

# Remove volumes (WARNING: This deletes all data)
docker volume rm dealer_postgres_data

# Restart everything
python start_split_services.py
```

### **Partial Reset (Keep Data)**
```bash
# Stop only application containers
docker stop dealer_backend dealer_celery_worker

# Restart application
docker-compose -f docker-compose.split.yml up -d backend celery_worker
```

### **Reset Sample Data**
```bash
# Insert fresh sample data
python insert_sample_data.py more

# Or connect to database and reset
docker exec -it dealer_postgres psql -U dealer_user -d dealer_dashboard
DELETE FROM prospect_data WHERE dealer_id = '00999';
\q

python insert_sample_data.py more
```

## 📊 Performance Issues

### **Slow Analytics Dashboard**
```python
# Increase cache TTL
@st.cache_data(ttl=600)  # 10 minutes instead of 5

# Optimize database queries
# Add indexes if needed
CREATE INDEX idx_prospect_dealer_date ON prospect_data(dealer_id, tanggal_prospect);
```

### **High Memory Usage**
```bash
# Monitor memory usage
docker stats

# Restart services periodically
docker restart dealer_backend
```

## 🔐 Security Issues

### **Database Password in Code**
```python
# Use environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")

# Set in environment
export DATABASE_URL="postgresql://dealer_user:secure_password@localhost:5432/dealer_dashboard"
```

### **API Security**
```python
# Add authentication to admin panel
# Implement API key validation
# Use HTTPS in production
```

## 📱 Browser Issues

### **Dashboard Not Loading**
1. **Clear browser cache**
2. **Try incognito/private mode**
3. **Check browser console for errors**
4. **Try different browser**

### **Charts Not Displaying**
1. **Check if data exists in database**
2. **Verify dealer selection**
3. **Clear Streamlit cache**
4. **Check browser JavaScript console**

## 🔄 Service Dependencies

### **Startup Order**
1. PostgreSQL (database)
2. Redis (message broker)
3. Backend API (business logic)
4. Celery Worker (background jobs)
5. Analytics Dashboard (direct DB)
6. Admin Panel (API-based)

### **Dependency Check Script**
```bash
# Create dependency_check.py
python -c "
import requests
import psycopg2
import redis

# Check database
try:
    psycopg2.connect('postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard')
    print('✅ Database OK')
except: print('❌ Database FAIL')

# Check Redis
try:
    redis.Redis(host='localhost', port=6379).ping()
    print('✅ Redis OK')
except: print('❌ Redis FAIL')

# Check API
try:
    requests.get('http://localhost:8000/health', timeout=5)
    print('✅ API OK')
except: print('❌ API FAIL')
"
```

## 📞 Getting Help

### **Log Collection**
```bash
# Collect all logs
mkdir logs
docker logs dealer_backend > logs/backend.log 2>&1
docker logs dealer_postgres > logs/postgres.log 2>&1
docker logs dealer_celery_worker > logs/celery.log 2>&1
```

### **System Information**
```bash
# System info
docker version
python --version
pip list | grep -E "(streamlit|pandas|sqlalchemy)"
```

### **Configuration Check**
```bash
# Environment variables
echo $DATABASE_URL
echo $BACKEND_URL

# Port usage
netstat -ano | findstr ":8000\|:8501\|:8502\|:5432\|:6379"
```

## ✅ Health Check Checklist

- [ ] PostgreSQL running on port 5432
- [ ] Redis running on port 6379  
- [ ] Backend API responding on port 8000
- [ ] Analytics Dashboard loading on port 8501
- [ ] Admin Panel loading on port 8502
- [ ] Sample data exists (dealer 00999)
- [ ] Database connections working
- [ ] API endpoints responding
- [ ] Charts displaying data
- [ ] Job execution working

Use this checklist to verify your split architecture is working correctly!
