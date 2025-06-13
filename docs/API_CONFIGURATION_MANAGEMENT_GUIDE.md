# API Configuration Management Guide

## 📋 **OVERVIEW**

This guide provides comprehensive instructions for managing API configurations in the Dealer Dashboard system. API configurations are database-stored settings that define how the system connects to external APIs, particularly the DGI (Dealer Gateway Integration) API endpoints.

## 🎯 **IMPORTANCE OF API CONFIGURATIONS**

### **Why API Configurations Matter**
- **Centralized Management**: All API endpoints managed from one location
- **Environment Flexibility**: Different URLs for dev/staging/production
- **Runtime Configuration**: No code changes needed for endpoint updates
- **Fallback Support**: Graceful degradation when configurations are missing
- **Admin Control**: Non-technical users can manage API settings

### **Common Issues Without Proper Configuration**
- ❌ `API configuration is not available` errors
- ❌ Jobs failing with connection errors
- ❌ Hardcoded URLs in multiple files
- ❌ Difficult environment management

## 🔧 **API CONFIGURATION STRUCTURE**

### **Database Schema**
```sql
CREATE TABLE api_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_name VARCHAR(100) UNIQUE NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    timeout_seconds INTEGER DEFAULT 30,
    retry_attempts INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **Configuration Fields**
| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `config_name` | String | Unique identifier | `dgi_prospect_api` |
| `base_url` | String | API base URL | `https://dev-gvt-gateway.eksad.com/dgi-api/v1.3` |
| `description` | Text | Human-readable description | `DGI API for Prospect Data` |
| `is_active` | Boolean | Enable/disable configuration | `true` |
| `timeout_seconds` | Integer | Request timeout | `30` |
| `retry_attempts` | Integer | Retry count on failure | `3` |

## 🚀 **CURRENT API CONFIGURATIONS**

### **Complete Configuration List**
| Job Type | Config Name | Endpoint | Status |
|----------|-------------|----------|--------|
| **Prospect** | `dgi_prospect_api` | `/prsp/read` | ✅ Active |
| **PKB** | `dgi_pkb_api` | `/pkb/read` | ✅ Active |
| **Parts Inbound** | `dgi_parts_inbound_api` | `/pinb/read` | ✅ Active |
| **Leasing** | `dgi_leasing_api` | `/lsng/read` | ✅ Active |
| **Document Handling** | `dgi_document_handling_api` | `/doch/read` | ✅ Active |
| **Unit Inbound** | `dgi_unit_inbound_api` | `/uinb/read` | ✅ Active |
| **Delivery Process** | `dgi_delivery_process_api` | `/bast/read` | ✅ Active |

### **Standard Configuration Template**
```python
APIConfiguration(
    config_name="dgi_[job_type]_api",
    base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
    description="DGI API for [Job Type] Data",
    is_active=True,
    timeout_seconds=30,
    retry_attempts=3
)
```

## 🔧 **IMPLEMENTATION REQUIREMENTS**

### **1. API Client Implementation**
**File: `backend/tasks/api_clients.py`**
```python
class YourAPIClient:
    """Client for Your API calls"""

    def __init__(self):
        # ✅ REQUIRED: Use fallback configuration
        self.config = APIConfigManager.get_api_config("dgi_your_api") or APIConfigManager.get_default_config()
        self.endpoint = "/your/endpoint"

    def fetch_data(self, ...):
        """Fetch data from DGI API"""
        # Check if config is valid
        if not self.config:
            raise ValueError("API configuration is not available")
        
        url = f"{self.config['base_url']}{self.endpoint}"
        timeout = self.config.get('timeout_seconds', 30)
        
        # Use configuration in HTTP client
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, ...)
```

### **2. Configuration Initialization**
**File: `backend/tasks/api_clients.py`**
```python
def initialize_default_api_configs():
    """Initialize default API configurations in database"""
    db = SessionLocal()
    try:
        # Check if configurations already exist
        existing_configs = db.query(APIConfiguration).count()
        if existing_configs > 0:
            logger.info("API configurations already exist, skipping initialization")
            return
        
        # ✅ REQUIRED: Add your configuration
        configs = [
            # ... existing configs
            APIConfiguration(
                config_name="dgi_your_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Your Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            )
        ]
        
        for config in configs:
            db.add(config)
        
        db.commit()
        logger.info("Default API configurations initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize API configurations: {e}")
        db.rollback()
    finally:
        db.close()
```

### **3. Configuration Controller Updates**
**File: `backend/controllers/configuration_controller.py`**
```python
@router.post("/api-configurations/initialize", response_model=CountResponse)
async def initialize_api_configurations(db: Session = Depends(get_db)):
    """Initialize default API configurations"""
    # ✅ REQUIRED: Add your configuration to default_configs list
    default_configs = [
        # ... existing configs
        APIConfiguration(
            config_name="dgi_your_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for Your Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        )
    ]

@router.post("/api-configurations/force-reinitialize", response_model=CountResponse)
async def force_reinitialize_api_configurations(db: Session = Depends(get_db)):
    """Force re-initialization of API configurations"""
    # ✅ REQUIRED: Include your configuration in force re-initialization
    # Same configuration list as above
```

## 🎛️ **MANAGEMENT METHODS**

### **Method 1: Admin Panel (Recommended)**
**URL**: http://localhost:8502 → Configuration → API Configuration

#### **Standard Initialization**
1. Click **"🔧 Initialize Default Configurations"**
2. Initializes configurations if none exist
3. Skips if configurations already present

#### **Force Re-initialization**
1. Click **"🔄 Force Re-initialize All"**
2. Deletes all existing configurations
3. Creates fresh set with latest definitions
4. **Use this when adding new job types**

#### **Manual Management**
1. **View**: See all current configurations
2. **Edit**: Modify URLs, timeouts, descriptions
3. **Add**: Create custom configurations
4. **Delete**: Remove unused configurations

### **Method 2: API Endpoints**
```bash
# Check existing configurations
curl "http://localhost:8000/api-configurations/"

# Initialize default configurations
curl -X POST "http://localhost:8000/api-configurations/initialize"

# Force re-initialize all configurations
curl -X POST "http://localhost:8000/api-configurations/force-reinitialize"

# Add new configuration
curl -X POST "http://localhost:8000/api-configurations/" \
  -H "Content-Type: application/json" \
  -d '{
    "config_name": "dgi_your_api",
    "base_url": "https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
    "description": "DGI API for Your Data",
    "is_active": true,
    "timeout_seconds": 30,
    "retry_attempts": 3
  }'
```

### **Method 3: Automatic Initialization**
**File: `backend/tasks/data_fetcher_router.py`**
```python
# Initialize API configurations on module load
try:
    initialize_default_api_configs()
except Exception as e:
    logger.warning(f"Failed to initialize API configs: {e}")
```

**Triggers**: Automatic initialization runs when:
- Backend service starts up
- Data fetcher router module is imported
- Celery worker processes start

## 🔍 **TROUBLESHOOTING**

### **Issue: "API configuration is not available"**
**Symptoms**: Jobs fail with configuration error
**Diagnosis**:
```bash
# Check if configuration exists
curl "http://localhost:8000/api-configurations/" | grep "your_config_name"

# Check database directly
docker-compose exec postgres psql -U dealer_user -d dealer_dashboard -c "SELECT config_name, is_active FROM api_configurations;"
```

**Solutions**:
1. **Force Re-initialize**: Admin Panel → "🔄 Force Re-initialize All"
2. **Manual Add**: Admin Panel → Add New API Configuration
3. **Restart Backend**: `docker-compose restart backend`

### **Issue: Configuration Exists But Still Fails**
**Symptoms**: Configuration visible in admin panel but jobs still fail
**Diagnosis**:
```python
# Check API client implementation
class YourAPIClient:
    def __init__(self):
        # ❌ WRONG: No fallback
        self.config = APIConfigManager.get_api_config("dgi_your_api")
        
        # ✅ CORRECT: With fallback
        self.config = APIConfigManager.get_api_config("dgi_your_api") or APIConfigManager.get_default_config()
```

**Solution**: Ensure API client uses fallback configuration

### **Issue: New Job Type Configuration Missing**
**Symptoms**: New job type works with dummy data but fails with real API
**Solution**: Update ALL configuration initialization points:
1. `backend/tasks/api_clients.py` → `initialize_default_api_configs()`
2. `backend/controllers/configuration_controller.py` → both endpoints
3. Force re-initialize configurations

## ✅ **VERIFICATION CHECKLIST**

### **After Adding New Job Type Configuration**
- [ ] Configuration appears in admin panel
- [ ] API client uses fallback configuration
- [ ] Configuration included in all initialization methods
- [ ] Job executes without "configuration not available" error
- [ ] Real API calls work (not just dummy data)

### **Configuration Health Check**
```bash
# 1. Count configurations (should be 7+ for all job types)
curl "http://localhost:8000/api-configurations/" | jq length

# 2. Check specific configuration
curl "http://localhost:8000/api-configurations/" | jq '.[] | select(.config_name=="dgi_your_api")'

# 3. Test job execution
curl -X POST "http://localhost:8000/jobs/run" \
  -H "Content-Type: application/json" \
  -d '{"dealer_id": "12284", "fetch_type": "your_type", "from_time": "2024-01-15 00:00:00", "to_time": "2024-01-16 23:59:00"}'
```

## 🎯 **BEST PRACTICES**

### **Configuration Naming**
- **Pattern**: `dgi_[job_type]_api`
- **Examples**: `dgi_prospect_api`, `dgi_leasing_api`
- **Consistency**: Use snake_case matching job type codes

### **URL Management**
- **Development**: `https://dev-gvt-gateway.eksad.com/dgi-api/v1.3`
- **Production**: Update base_url through admin panel
- **Avoid**: Hardcoded URLs in API clients

### **Error Handling**
- **Always**: Use fallback configuration in API clients
- **Graceful**: Handle missing configurations without crashing
- **Logging**: Log configuration issues for debugging

### **Maintenance**
- **Regular**: Verify configurations after system updates
- **Documentation**: Update this guide when adding new job types
- **Testing**: Test configuration changes in development first

**API configurations are the foundation of reliable job execution. Proper management ensures smooth operation across all job types!** 🚀
