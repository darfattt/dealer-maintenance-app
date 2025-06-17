# CORS and Login Issues - Resolution Guide

## Problem Description

The web application was experiencing CORS (Cross-Origin Resource Sharing) errors when trying to authenticate users:

### Error Messages
```
Access to XMLHttpRequest at 'http://localhost:8080/api/v1/auth/login' from origin 'http://localhost:5000' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.

Access to XMLHttpRequest at 'http://localhost:8080/api/v1/auth/login' from origin 'http://localhost:5173' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### Root Causes
1. **Missing CORS Origin**: The API Gateway CORS configuration was missing `http://localhost:5000` (production web app port)
2. **Incorrect Login Credentials**: Documentation showed incorrect default credentials

## Solution Implemented

### 1. Fixed CORS Configuration

**File**: `backend-microservices/api-gateway/config.py`

**Before**:
```python
allowed_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:5173,http://localhost:5174,http://localhost:8501,http://localhost:8502"
```

**After**:
```python
allowed_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:5000,http://localhost:5173,http://localhost:5174,http://localhost:8501,http://localhost:8502"
```

**Changes Made**:
- Added `http://localhost:5000` to the allowed origins list
- This allows the production web app (running on port 5000) to make API requests

### 2. Rebuilt and Restarted API Gateway

```bash
# Rebuild API Gateway with updated CORS configuration
docker-compose build api_gateway

# Restart API Gateway to apply changes
docker-compose restart api_gateway
```

### 3. Verified Correct Login Credentials

**Default Admin User Credentials**:
- **Email**: `admin@dealer-dashboard.com`
- **Password**: `Admin123!`

**Location**: `backend-microservices/services/account/app/config.py`
```python
admin_email: str = "admin@dealer-dashboard.com"
admin_password: str = "Admin123!"
admin_full_name: str = "System Administrator"
```

### 4. Updated Documentation

**File**: `docs/web-quick-start.md`

**Updated Default Login Credentials**:
```markdown
## Default Login Credentials
- **Email**: admin@dealer-dashboard.com
- **Password**: Admin123!
```

## Verification Steps

### 1. Test API Directly
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/v1/auth/login" -Method POST -ContentType "application/json" -Body '{"email":"admin@dealer-dashboard.com","password":"Admin123!"}'
```

**Expected Response**:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "79fa5fc2-50cb-4d75-8638-98c92faf1bdd",
    "email": "admin@dealer-dashboard.com",
    "full_name": "System Administrator",
    "role": "SUPER_ADMIN",
    "is_active": true
  }
}
```

### 2. Test Web Applications

**Production Web App (Port 5000)**:
1. Open: http://localhost:5000
2. Login with: admin@dealer-dashboard.com / Admin123!
3. Should successfully authenticate and redirect to dashboard

**Development Web App (Port 5173)**:
1. Open: http://localhost:5173
2. Login with: admin@dealer-dashboard.com / Admin123!
3. Should successfully authenticate and redirect to dashboard

## Technical Details

### CORS Configuration
The API Gateway uses FastAPI's CORSMiddleware with the following settings:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Authentication Flow
1. User submits email/password via web form
2. Frontend sends POST request to `/api/v1/auth/login`
3. API Gateway forwards request to Account Service
4. Account Service validates credentials and returns JWT tokens
5. Frontend stores tokens and redirects to dashboard

### Default User Creation
The Account Service automatically creates a default admin user on startup:
```python
async def create_default_admin():
    """Create default admin user if not exists"""
    admin_data = UserCreate(
        email=settings.admin_email,
        password=settings.admin_password,
        full_name=settings.admin_full_name,
        role=UserRole.SUPER_ADMIN,
        is_active=True
    )
```

## Current Status

✅ **CORS Issues Resolved**: All web application origins are now allowed
✅ **Authentication Working**: Login successful with correct credentials
✅ **Production App**: Running on port 5000 with Nginx
✅ **Development App**: Running on port 5173 with Vite dev server
✅ **Documentation Updated**: Correct credentials documented

## Troubleshooting

### If CORS Issues Persist
1. Check API Gateway logs: `docker logs dealer_api_gateway`
2. Verify CORS configuration: Check `backend-microservices/api-gateway/config.py`
3. Restart API Gateway: `docker-compose restart api_gateway`

### If Login Still Fails
1. Verify API Gateway is healthy: `curl http://localhost:8080/api/v1/health`
2. Test login API directly with correct credentials
3. Check Account Service logs: `docker logs dealer_account_service`
4. Verify database connection and admin user creation

### If Web App Not Loading
1. Check container status: `docker ps --filter "name=dealer_web"`
2. Check container logs: `docker logs dealer_web_primevue` or `docker logs dealer_web_app_dev`
3. Verify port availability: `netstat -an | findstr :5000` or `netstat -an | findstr :5173`

## Next Steps

1. **Test Complete Authentication Flow**: Login → Dashboard → Logout
2. **Verify Protected Routes**: Ensure authentication guards work correctly
3. **Test Token Refresh**: Verify automatic token refresh functionality
4. **Add More Users**: Create additional test users if needed
5. **Implement User Management**: Add user creation/management features
