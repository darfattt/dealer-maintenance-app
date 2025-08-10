# Customer Service

Customer validation microservice with WhatsApp integration via Fonnte API.

## Overview

This service handles customer phone validation requests and sends WhatsApp notifications to customers using per-dealer Fonnte API configurations.

## Features

- ✅ Customer data validation and storage
- ✅ Per-dealer Fonnte API key management
- ✅ WhatsApp message sending via Fonnte API
- ✅ Request status tracking
- ✅ Comprehensive logging and error handling
- ✅ Health check endpoints
- ✅ API documentation with Swagger/OpenAPI

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Client    │───▶│   Customer   │───▶│  Database   │
│  Request    │    │   Service    │    │  (Customer  │
│             │    │   (8300)     │    │   Schema)   │
└─────────────┘    └──────────────┘    └─────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │   Fonnte     │
                   │   WhatsApp   │
                   │     API      │
                   └──────────────┘
```

## API Endpoints

### Main Endpoint
- **POST** `/api/v1/customer/validate-customer` - Process customer validation request

### Management Endpoints
- **GET** `/api/v1/customer/request/{request_id}` - Get specific request
- **GET** `/api/v1/customer/dealer/{dealer_id}/requests` - Get dealer requests
- **GET** `/api/v1/customer/dealer/{dealer_id}/stats` - Get dealer statistics
- **POST** `/api/v1/customer/dealer/{dealer_id}/test-whatsapp` - Test WhatsApp config

### System Endpoints
- **GET** `/api/v1/health/` - Basic health check
- **GET** `/api/v1/health/detailed` - Detailed health with DB check
- **GET** `/docs` - API documentation

## Request Format

```json
{
  "namaPembawa": "Adit",
  "noTelp": "082148523421", 
  "tipeUnit": "BeAT Street",
  "noPol": "D 123 AD",
  "createdTime": "31/12/2019 15:40:50",
  "modifiedTime": "31/12/2019 15:40:50",
  "dealerId": "0009999"
}
```

## Response Format

```json
{
  "status": 1,
  "message": {
    "confirmation": "Data berhasil disimpan"
  },
  "data": null
}
```

## Database Schema

### customer_validation_request Table
```sql
CREATE TABLE customer.customer_validation_request (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dealer_id VARCHAR(10) NOT NULL,
    request_date DATE NOT NULL,
    request_time TIME NOT NULL,
    nama_pembawa VARCHAR(255) NOT NULL,
    no_telp VARCHAR(20) NOT NULL,
    tipe_unit VARCHAR(100) NOT NULL,
    no_pol VARCHAR(20) NOT NULL,
    request_status VARCHAR(20) DEFAULT 'PENDING',
    whatsapp_status VARCHAR(20) DEFAULT 'NOT_SENT',
    fonnte_response JSON,
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT NOW(),
    last_modified_by VARCHAR(100),
    last_modified_date TIMESTAMP DEFAULT NOW()
);
```

### Dealer Configuration (Extended)
Fonnte configuration is stored in the existing `dealer_integration.dealers` table:
- `fonnte_api_key` - Dealer's Fonnte API key
- `fonnte_api_url` - Fonnte API URL (default: https://api.fonnte.com/send)

## Setup and Installation

### 1. Using Docker Compose
```bash
# Start the customer service with other microservices
cd backend-microservices
docker-compose up customer-service
```

### 2. Manual Setup
```bash
# Navigate to service directory
cd backend-microservices/services/customer

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard"
export DB_SCHEMA="customer"
export SERVICE_PORT=8300

# Run the service
python main.py
```

## Configuration

### Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `DB_SCHEMA` - Database schema name (default: "customer")
- `SERVICE_PORT` - Service port (default: 8300)
- `LOG_LEVEL` - Logging level (default: "INFO")
- `FONNTE_DEFAULT_API_URL` - Default Fonnte API URL

### Dealer Configuration
Each dealer needs Fonnte configuration in the `dealers` table:

```sql
UPDATE dealer_integration.dealers 
SET 
    fonnte_api_key = 'your-fonnte-api-key',
    fonnte_api_url = 'https://api.fonnte.com/send'
WHERE dealer_id = '0009999';
```

## Testing

### Run Unit Tests
```bash
cd backend-microservices/services/customer
python -m pytest tests/ -v
```

### Test Service Setup
```bash
cd backend-microservices/services/customer
python test_setup.py
```

### Manual API Testing
```bash
# Health check
curl http://localhost:8300/api/v1/health/

# Test customer validation
curl -X POST http://localhost:8300/api/v1/customer/validate-customer \
  -H "Content-Type: application/json" \
  -d '{
    "namaPembawa": "Test Customer",
    "noTelp": "082148523421",
    "tipeUnit": "BeAT Street", 
    "noPol": "D 123 AD",
    "createdTime": "31/12/2019 15:40:50",
    "modifiedTime": "31/12/2019 15:40:50",
    "dealerId": "0009999"
  }'
```

## WhatsApp Message Template

The service sends a formatted WhatsApp message to customers:

```
Halo {customer_name},

Terima kasih telah melakukan validasi customer untuk unit {unit_type} dengan nomor polisi {license_plate}.

Data Anda telah kami terima dan sedang dalam proses verifikasi oleh tim {dealer_name}.

Kami akan menghubungi Anda kembali untuk proses selanjutnya.

Terima kasih atas kepercayaan Anda.

Best regards,
{dealer_name}
```

## Error Handling

The service handles various error scenarios:

- **Dealer not found** - Returns status 0 with appropriate message
- **Missing Fonnte configuration** - Returns status 0 with configuration error
- **Database errors** - Logged and return generic error message
- **WhatsApp API failures** - Request still saved, status updated accordingly
- **Validation errors** - Returns 422 with detailed validation messages

## Monitoring and Logging

- All operations are logged with appropriate levels
- Health check endpoints for monitoring
- Request/response tracking in database
- WhatsApp delivery status tracking

## Security Considerations

- API keys stored securely in database
- Input validation on all endpoints
- SQL injection protection via SQLAlchemy ORM
- CORS configuration for frontend access
- Rate limiting can be added via middleware

## Future Enhancements

- [ ] Message template customization per dealer
- [ ] Multiple message templates support
- [ ] WhatsApp delivery confirmation webhooks
- [ ] Rate limiting and throttling
- [ ] Message scheduling
- [ ] Bulk customer validation processing
- [ ] Analytics and reporting endpoints