# Docker Testing Commands for Dashboard Dealer Service

## Build and Test Commands

### 1. Build the Dashboard Dealer Service
```bash
cd backend-microservices
docker-compose build dashboard-dealer-service
```

### 2. Test Module Imports in Container
```bash
# Run the import test script inside the container
docker-compose run --rm dashboard-dealer-service python test_imports.py
```

### 3. Start Services and Test Health Check
```bash
# Start all microservices
docker-compose up -d

# Check dashboard-dealer service health
curl -f http://localhost:8200/api/v1/health

# View logs
docker-compose logs dashboard-dealer-service
```

### 4. Test Excel Export Functionality
```bash
# Test pandas/openpyxl imports directly
docker-compose exec dashboard-dealer-service python -c "
import pandas as pd
import openpyxl
print(f'pandas: {pd.__version__}')
print(f'openpyxl: {openpyxl.__version__}')
print('✅ Excel modules working!')
"
```

## Expected Results

After the fixes:
- ✅ pandas>=1.5.0 should be installed
- ✅ openpyxl>=3.0.0 should be installed  
- ✅ curl should be available for health checks
- ✅ Service should start on port 8200
- ✅ Utils modules should be importable
- ✅ Excel export functionality should work

## Issues Fixed

1. **Added missing openpyxl to root requirements.txt**
2. **Aligned pandas version to >=1.5.0 in both requirements files**
3. **Added curl to Dockerfile for health checks**
4. **Added dashboard-dealer service to microservices docker-compose.yml**
5. **Created test script to validate imports**