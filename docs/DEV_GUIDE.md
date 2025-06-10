# 🚀 Development Mode Guide

This guide will help you run the Dealer Dashboard Analytics application in development mode with dummy data and the real DGI API.

## 📋 Prerequisites

1. **Python 3.11+** installed
2. **PostgreSQL** running (can use Docker)
3. **Redis** running (can use Docker)

## 🔧 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start external services (PostgreSQL & Redis)
docker run -d --name postgres -p 5432:5432 \
  -e POSTGRES_DB=dealer_dashboard \
  -e POSTGRES_USER=dealer_user \
  -e POSTGRES_PASSWORD=dealer_pass \
  postgres:15-alpine

docker run -d --name redis -p 6379:6379 redis:7-alpine

# 3. Run development setup (creates dummy data)
python start_dev.py
```

### Option 2: Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database and dummy data
python dev_setup.py

# 3. Start services in separate terminals:

# Terminal 1: Backend API
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Celery Worker
celery -A celery_app worker --loglevel=info

# Terminal 3: Dashboard
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
```

## 🌐 Access URLs

- **Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 🏢 Default Configuration

The development setup creates:

- **Default Dealer ID**: `00999`
- **Dealer Name**: "Default Dealer"
- **API Credentials**: Pre-configured for DGI API
- **Sample Data**: 100 dummy prospect records with realistic data

## 📊 Testing the Application Flow

### 1. View Existing Data
1. Open dashboard at http://localhost:8501
2. Go to "Dashboard" page
3. Select "Default Dealer" 
4. View charts with dummy data

### 2. Test Manual Job Execution
1. Go to "Run Jobs" page
2. Select "Default Dealer"
3. Choose date range (last 7 days recommended)
4. Click "🔄 Run Data Fetch Job"
5. Monitor real-time progress
6. Check "Job History" for results

### 3. Test Real API Integration
The application will:
1. **First try** the real DGI API: `https://dev-gvt-gateway.eksad.com/dgi-api/v1.3/prsp/read`
2. **Fallback** to dummy data if API fails
3. **Store results** in PostgreSQL database
4. **Update dashboard** with new data

## 🔧 API Configuration

The default dealer (`00999`) is configured with:
- **API Key**: `6c796097-a453-420f-9a19-155a2a24513e`
- **API Token**: `81d7fd22c95ba5385e05563a515868905d20419df06190ab035cf8be307a1e0c`

You can modify these in the database or through the "Dealer Management" page.

## 📈 Sample Data Features

The dummy data includes:
- **100 prospect records** spread over 30 days
- **Realistic Indonesian names** and addresses
- **Various prospect statuses** (New, In Progress, Completed, Cancelled)
- **Multiple unit types** (PCX160, VARIO125, BEAT, etc.)
- **Random appointment dates** and times
- **Sample fetch logs** showing job history

## 🛠️ Development Features

### Hot Reload
- **FastAPI**: Automatically reloads on code changes
- **Streamlit**: Reloads on file save
- **Celery**: Restart worker to pick up changes

### Database Access
```python
# Direct database access for debugging
from database import SessionLocal, ProspectData

db = SessionLocal()
prospects = db.query(ProspectData).filter(ProspectData.dealer_id == "00999").all()
print(f"Found {len(prospects)} prospects")
db.close()
```

### API Testing
```bash
# Test API endpoints directly
curl http://localhost:8000/health
curl http://localhost:8000/dealers/
curl http://localhost:8000/prospect-data/analytics/00999
```

## 🐛 Troubleshooting

### Common Issues

1. **PostgreSQL Connection Error**
   ```bash
   # Check if PostgreSQL is running
   docker ps | grep postgres
   
   # Restart if needed
   docker restart postgres
   ```

2. **Redis Connection Error**
   ```bash
   # Check if Redis is running
   docker ps | grep redis
   
   # Restart if needed
   docker restart redis
   ```

3. **Celery Worker Not Processing Jobs**
   ```bash
   # Check worker status
   celery -A celery_app inspect active
   
   # Restart worker
   # Ctrl+C and restart: celery -A celery_app worker --loglevel=info
   ```

4. **Dashboard Not Loading**
   - Check if backend is running on port 8000
   - Verify BACKEND_URL in .env file
   - Check browser console for errors

### Logs and Debugging

- **Backend logs**: Check terminal running uvicorn
- **Celery logs**: Check terminal running celery worker
- **Dashboard logs**: Check terminal running streamlit
- **Database logs**: Check PostgreSQL container logs

## 🔄 Reset Development Data

To reset and regenerate dummy data:

```bash
# Stop all services
# Delete existing data and recreate
python dev_setup.py
```

## 📝 Adding New Features

1. **Backend changes**: Edit files in `main.py`, `database.py`, etc.
2. **Frontend changes**: Edit `dashboard.py`
3. **Job processing**: Edit `tasks/data_fetcher.py`
4. **Database schema**: Update `database.py` and `init.sql`

The development setup makes it easy to test the complete flow:
**UI → Job Execution → API Call → Database Storage → Dashboard Analytics**
