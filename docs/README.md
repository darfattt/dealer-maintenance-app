# Dashboard Integration Documentation

This directory contains comprehensive documentation for integrating frontend dashboard widgets with backend APIs in the Dealer Management Application.

## Documentation Overview

### 📋 [DASHBOARD_INTEGRATION_GUIDE.md](./DASHBOARD_INTEGRATION_GUIDE.md)
**Main integration guide covering:**
- Architecture overview and data flow
- Frontend widget structure and implementation
- Backend API development (routes, controllers, repositories, schemas)
- Dashboard integration patterns
- Step-by-step implementation guide

### 🔧 [DASHBOARD_API_EXAMPLES.md](./DASHBOARD_API_EXAMPLES.md)
**Detailed examples of working integrations:**
- Complete UnitInboundStatusWidget implementation
- Complete PaymentTypeWidget implementation
- API request/response examples
- Frontend and backend code samples
- Testing examples

### 📚 [DASHBOARD_BEST_PRACTICES.md](./DASHBOARD_BEST_PRACTICES.md)
**Best practices and testing strategies:**
- Frontend and backend best practices
- Error handling patterns
- Testing strategies (unit, integration)
- Common integration patterns
- Deployment checklist
- Troubleshooting guide

## Quick Start

### For New Widget Development

1. **Read the Integration Guide**: Start with [DASHBOARD_INTEGRATION_GUIDE.md](./DASHBOARD_INTEGRATION_GUIDE.md) for architecture understanding
2. **Study Working Examples**: Review [DASHBOARD_API_EXAMPLES.md](./DASHBOARD_API_EXAMPLES.md) for reference implementations
3. **Follow Best Practices**: Implement using patterns from [DASHBOARD_BEST_PRACTICES.md](./DASHBOARD_BEST_PRACTICES.md)

### Reference Implementations

We have two fully integrated widgets that serve as reference:

#### 1. UnitInboundStatusWidget
- **Purpose**: Unit inbound status distribution (vertical bar chart)
- **Files**: 
  - Frontend: `web/src/components/dashboard/UnitInboundStatusWidget.vue`
  - Backend: `/api/v1/dashboard/unit-inbound/status-counts`
- **Features**: Status mapping, responsive charts, error handling

#### 2. PaymentTypeWidget
- **Purpose**: Payment type distribution (pie chart)
- **Files**:
  - Frontend: `web/src/components/dashboard/PaymentTypeWidget.vue`
  - Backend: `/api/v1/dashboard/payment-type/statistics`
- **Features**: Amount formatting, color mapping, custom legends

## Architecture Overview

```
Dashboard.vue → Widget Components → API Endpoints → Controllers → Repositories → Database
```

### Frontend Stack
- **Vue.js 3** with Composition API
- **PrimeVue** for UI components
- **Chart.js** via PrimeVue Chart component
- **Axios** for API communication

### Backend Stack
- **FastAPI** for REST API
- **SQLAlchemy** for database ORM
- **Pydantic** for data validation
- **PostgreSQL** database

## Key Features

### Dashboard Layout
- **2-Column Layout**: Sales (left) and Inventory (right) sections
- **External Titles**: Clickable titles outside widget cards
- **Conditional Titles**: Widgets show internal titles only in detail views
- **Responsive Design**: Adapts to different screen sizes

### Widget Features
- **Real-time Data**: Fetches data based on dealer and date filters
- **Error Handling**: Comprehensive error states and messages
- **Loading States**: Visual feedback during data fetching
- **Empty States**: Proper handling of no-data scenarios
- **Chart Visualization**: Interactive charts with tooltips and legends

### API Features
- **RESTful Design**: Clean, predictable endpoint structure
- **Input Validation**: Comprehensive parameter validation
- **Error Handling**: Proper HTTP status codes and error messages
- **Logging**: Detailed logging for debugging and monitoring
- **Documentation**: Auto-generated API docs via FastAPI

## Implementation Checklist

### Frontend Widget
- [ ] Create Vue component with proper structure
- [ ] Implement API integration with error handling
- [ ] Add loading and empty states
- [ ] Configure chart visualization
- [ ] Add conditional title support
- [ ] Integrate with Dashboard.vue
- [ ] Write unit tests

### Backend API
- [ ] Create API route with validation
- [ ] Implement controller method
- [ ] Create repository method with efficient queries
- [ ] Define Pydantic schemas
- [ ] Add comprehensive error handling
- [ ] Add logging
- [ ] Write unit tests
- [ ] Update API documentation

### Integration
- [ ] Test end-to-end functionality
- [ ] Verify error handling
- [ ] Check performance under load
- [ ] Validate responsive design
- [ ] Test with different data scenarios
- [ ] Deploy and monitor

## File Structure

```
dealer-management-app/
├── web/src/
│   ├── views/
│   │   ├── Dashboard.vue                    # Main dashboard layout
│   │   ├── DeliveryProcessDetail.vue        # Detail view example
│   │   └── DealingProcess.vue               # Detail view example
│   └── components/dashboard/
│       ├── UnitInboundStatusWidget.vue      # Reference implementation
│       ├── PaymentTypeWidget.vue            # Reference implementation
│       ├── StatusSPKWidget.vue              # Reusable widget
│       ├── DeliveryProcessWidget.vue        # Reusable widget
│       └── [YourNewWidget].vue              # Your new widget
├── backend-microservices/services/dashboard-dealer/
│   └── app/
│       ├── routes/dashboard.py              # API routes
│       ├── controllers/dashboard_controller.py  # Business logic
│       ├── repositories/dashboard_repository.py # Data access
│       └── schemas/dashboard.py             # Data models
└── docs/
    ├── README.md                            # This file
    ├── DASHBOARD_INTEGRATION_GUIDE.md       # Main guide
    ├── DASHBOARD_API_EXAMPLES.md            # Working examples
    └── DASHBOARD_BEST_PRACTICES.md          # Best practices
```

## API Endpoints

### Existing Endpoints
- `GET /api/v1/dashboard/unit-inbound/status-counts` - Unit inbound status distribution
- `GET /api/v1/dashboard/payment-type/statistics` - Payment type statistics

### Standard Parameters
All dashboard endpoints accept these parameters:
- `dealer_id` (string): Dealer ID to filter by
- `date_from` (string): Start date in YYYY-MM-DD format
- `date_to` (string): End date in YYYY-MM-DD format

### Standard Response Format
```json
{
    "success": boolean,
    "message": string,
    "data": array,
    "total_records": number,
    "total_amount": number (optional)
}
```

## Testing

### Frontend Testing
```bash
cd web
npm run test:unit
```

### Backend Testing
```bash
cd backend-microservices/services/dashboard-dealer
pytest
```

### Integration Testing
```bash
# Start backend
cd backend-microservices/services/dashboard-dealer
uvicorn app.main:app --reload

# Start frontend
cd web
npm run dev

# Test manually at http://localhost:5173
```

## Support and Troubleshooting

### Common Issues
1. **CORS Issues**: Check backend CORS configuration
2. **Date Format Issues**: Ensure YYYY-MM-DD format
3. **Empty Data**: Implement proper empty state handling
4. **Performance**: Add database indexing for large datasets
5. **Authentication**: Include proper auth headers

### Getting Help
- Review the documentation files in this directory
- Check the reference implementations
- Look at existing working widgets
- Test with the provided examples

### Contributing
When adding new widgets:
1. Follow the established patterns
2. Update documentation
3. Add tests
4. Follow the deployment checklist

## Version History

- **v1.0**: Initial dashboard implementation with UnitInboundStatusWidget and PaymentTypeWidget
- **v1.1**: Added conditional titles and reusable widget patterns
- **v1.2**: Implemented 2-column dashboard layout with external titles
- **v1.3**: Added DeliveryProcessDetail and DealingProcess views
- **v1.4**: Comprehensive documentation and best practices guide

---

For detailed implementation guidance, please refer to the specific documentation files linked above.
