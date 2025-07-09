# Dashboard Integration Best Practices & Testing

This document covers best practices, testing strategies, and common patterns for dashboard widget integration.

## Best Practices

### Frontend Best Practices

#### 1. Error Handling
Always implement comprehensive error handling:

```javascript
const fetchData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        const response = await axios.get('/api/v1/dashboard/your-endpoint', {
            params: {
                dealer_id: props.dealerId,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            processData(response.data.data);
        } else {
            error.value = response.data.message || 'Failed to fetch data';
        }
    } catch (err) {
        console.error('Error fetching data:', err);
        error.value = 'Failed to fetch data';
    } finally {
        loading.value = false;
    }
};
```

#### 2. Prop Validation
Validate props before making API calls:

```javascript
const props = defineProps({
    dealerId: { 
        type: String, 
        default: '12284',
        validator: (value) => value && value.length > 0
    },
    dateFrom: { 
        type: String, 
        required: true,
        validator: (value) => /^\d{4}-\d{2}-\d{2}$/.test(value)
    },
    dateTo: { 
        type: String, 
        required: true,
        validator: (value) => /^\d{4}-\d{2}-\d{2}$/.test(value)
    },
    showTitle: { 
        type: Boolean, 
        default: false 
    }
});
```

#### 3. Reactive Updates
Use watchers for prop changes:

```javascript
// Watch for prop changes and refetch data
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchData();
}, { deep: true });
```

#### 4. Chart Configuration
Configure charts for responsiveness:

```javascript
chartOptions.value = {
    responsive: true,
    maintainAspectRatio: false,
    layout: {
        padding: { top: 20, bottom: 20, left: 20, right: 20 }
    },
    plugins: {
        legend: { 
            display: false // Use custom legend for better control
        },
        tooltip: {
            callbacks: {
                label: function(context) {
                    const label = context.label || '';
                    const value = context.parsed;
                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                    const percentage = ((value / total) * 100).toFixed(1);
                    return `${label}: ${formatValue(value)} (${percentage}%)`;
                }
            }
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            ticks: { stepSize: 1 }
        }
    }
};
```

#### 5. Conditional Titles
Implement conditional titles for reusable widgets:

```vue
<template>
    <Card class="h-full">
        <template #title v-if="showTitle">
            <span class="text-lg font-bold text-gray-800 uppercase tracking-wide">
                WIDGET TITLE
            </span>
        </template>
        
        <template #content>
            <!-- Widget content -->
        </template>
    </Card>
</template>
```

### Backend Best Practices

#### 1. Input Validation
Validate all input parameters:

```python
@router.get("/dashboard/your-endpoint", response_model=YourResponse)
async def get_your_data(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    try:
        # Validate date format
        try:
            datetime.strptime(date_from, '%Y-%m-%d')
            datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid date format. Use YYYY-MM-DD format."
            )
        
        # Validate date range
        if date_from > date_to:
            raise HTTPException(
                status_code=400, 
                detail="date_from must be less than or equal to date_to"
            )
        
        # Validate dealer_id format if needed
        if not dealer_id.isdigit():
            raise HTTPException(
                status_code=400,
                detail="Invalid dealer_id format"
            )
```

#### 2. Error Handling
Implement comprehensive error handling:

```python
    try:
        controller = DashboardController(db)
        result = await controller.get_your_data(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_your_data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
```

#### 3. Logging
Add detailed logging for debugging:

```python
async def get_your_data(self, dealer_id: str, date_from: str, date_to: str) -> YourResponse:
    try:
        logger.info(f"Getting your data for dealer {dealer_id} from {date_from} to {date_to}")
        
        # Get data from repository
        data_items = self.repository.get_your_data(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        logger.info(f"Found {len(data_items)} items")
        
        return YourResponse(
            success=True,
            message="Data retrieved successfully",
            data=data_items
        )
        
    except Exception as e:
        logger.error(f"Error getting your data: {str(e)}")
        return YourResponse(
            success=False,
            message=f"Error retrieving data: {str(e)}",
            data=[]
        )
```

#### 4. Response Format
Use consistent response format:

```python
class YourResponse(BaseModel):
    """Standard response format for dashboard endpoints"""
    success: bool
    message: str
    data: List[YourDataItem]
    total_records: int
    total_amount: Optional[float] = None
    metadata: Optional[dict] = None
```

#### 5. Database Optimization
Use efficient queries:

```python
def get_your_data(self, dealer_id: str, date_from: str, date_to: str) -> List[YourDataItem]:
    try:
        # Use efficient query with proper indexing
        query = self.db.query(
            YourModel.your_field,
            func.count(YourModel.id).label('count'),
            func.sum(YourModel.amount).label('total_amount')
        ).filter(
            YourModel.dealer_id == dealer_id,
            YourModel.created_date >= date_from,
            YourModel.created_date <= date_to
        ).group_by(YourModel.your_field)
        
        result = query.all()
        
        return [
            YourDataItem(
                field_name=item.your_field,
                count=item.count,
                amount=item.total_amount or 0
            )
            for item in result
        ]
        
    except Exception as e:
        logger.error(f"Error in get_your_data: {str(e)}")
        raise
```

## Testing Strategies

### Frontend Testing

#### 1. Component Testing
```javascript
import { mount } from '@vue/test-utils';
import { nextTick } from 'vue';
import axios from 'axios';
import YourWidget from '@/components/dashboard/YourWidget.vue';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('YourWidget', () => {
    beforeEach(() => {
        mockedAxios.get.mockClear();
    });

    it('should fetch data on mount', async () => {
        const mockResponse = {
            data: {
                success: true,
                data: [
                    { field_name: 'Test', count: 10, amount: 1000 }
                ],
                total_records: 1
            }
        };
        
        mockedAxios.get.mockResolvedValue(mockResponse);
        
        const wrapper = mount(YourWidget, {
            props: { 
                dealerId: '12284', 
                dateFrom: '2024-01-01', 
                dateTo: '2024-12-31' 
            }
        });
        
        await nextTick();
        
        expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/dashboard/your-endpoint', {
            params: { 
                dealer_id: '12284', 
                date_from: '2024-01-01', 
                date_to: '2024-12-31' 
            }
        });
    });

    it('should handle API errors gracefully', async () => {
        mockedAxios.get.mockRejectedValue(new Error('Network error'));
        
        const wrapper = mount(YourWidget, {
            props: { 
                dealerId: '12284', 
                dateFrom: '2024-01-01', 
                dateTo: '2024-12-31' 
            }
        });
        
        await nextTick();
        
        expect(wrapper.vm.error).toBe('Failed to fetch data');
    });

    it('should show loading state', async () => {
        mockedAxios.get.mockImplementation(() => new Promise(() => {})); // Never resolves
        
        const wrapper = mount(YourWidget, {
            props: { 
                dealerId: '12284', 
                dateFrom: '2024-01-01', 
                dateTo: '2024-12-31' 
            }
        });
        
        await nextTick();
        
        expect(wrapper.vm.loading).toBe(true);
        expect(wrapper.find('.pi-spinner').exists()).toBe(true);
    });
});
```

#### 2. Integration Testing
```javascript
describe('Dashboard Integration', () => {
    it('should pass correct props to widgets', () => {
        const wrapper = mount(Dashboard);
        
        const widget = wrapper.findComponent(YourWidget);
        expect(widget.props('dealerId')).toBe('12284');
        expect(widget.props('dateFrom')).toBeDefined();
        expect(widget.props('dateTo')).toBeDefined();
    });

    it('should update widgets when filters change', async () => {
        const wrapper = mount(Dashboard);
        
        // Change date filter
        await wrapper.setData({ selectedDateFrom: new Date('2024-06-01') });
        
        const widget = wrapper.findComponent(YourWidget);
        expect(widget.props('dateFrom')).toBe('2024-06-01');
    });
});
```

### Backend Testing

#### 1. Endpoint Testing
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_your_data_success():
    response = client.get(
        "/api/v1/dashboard/your-endpoint",
        params={
            "dealer_id": "12284",
            "date_from": "2024-01-01",
            "date_to": "2024-12-31"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "data" in data
    assert "total_records" in data

def test_get_your_data_invalid_date():
    response = client.get(
        "/api/v1/dashboard/your-endpoint",
        params={
            "dealer_id": "12284",
            "date_from": "invalid-date",
            "date_to": "2024-12-31"
        }
    )
    
    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]

def test_get_your_data_invalid_date_range():
    response = client.get(
        "/api/v1/dashboard/your-endpoint",
        params={
            "dealer_id": "12284",
            "date_from": "2024-12-31",
            "date_to": "2024-01-01"
        }
    )
    
    assert response.status_code == 400
    assert "date_from must be less than or equal to date_to" in response.json()["detail"]
```

#### 2. Controller Testing
```python
import pytest
from unittest.mock import Mock, AsyncMock
from app.controllers.dashboard_controller import DashboardController

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def controller(mock_db):
    return DashboardController(mock_db)

@pytest.mark.asyncio
async def test_get_your_data_success(controller):
    # Mock repository response
    controller.repository.get_your_data = Mock(return_value=[
        Mock(field_name='Test', count=10, amount=1000)
    ])
    controller.repository.get_total_records = Mock(return_value=1)
    
    result = await controller.get_your_data('12284', '2024-01-01', '2024-12-31')
    
    assert result.success == True
    assert len(result.data) == 1
    assert result.total_records == 1

@pytest.mark.asyncio
async def test_get_your_data_exception(controller):
    # Mock repository to raise exception
    controller.repository.get_your_data = Mock(side_effect=Exception('Database error'))
    
    result = await controller.get_your_data('12284', '2024-01-01', '2024-12-31')
    
    assert result.success == False
    assert 'Database error' in result.message
```

## Common Integration Patterns

### 1. Data Transformation Pattern
```javascript
// Transform API response to component format
const transformApiData = (apiData) => {
    return apiData.map(item => ({
        label: mapLabel(item.original_field),
        value: parseFloat(item.numeric_field) || 0,
        color: getColor(item.category_field),
        formattedValue: formatValue(item.numeric_field)
    }));
};
```

### 2. Chart Data Preparation Pattern
```javascript
const prepareChartData = (transformedData) => {
    const labels = transformedData.map(item => item.label);
    const values = transformedData.map(item => item.value);
    const colors = transformedData.map(item => item.color);

    return {
        labels: labels,
        datasets: [{
            data: values,
            backgroundColor: colors,
            borderColor: colors,
            borderWidth: 1
        }]
    };
};
```

### 3. Error Boundary Pattern
```javascript
const handleApiError = (error, fallbackMessage = 'An error occurred') => {
    if (error.response) {
        // Server responded with error status
        return error.response.data.message || fallbackMessage;
    } else if (error.request) {
        // Request was made but no response received
        return 'Network error - please check your connection';
    } else {
        // Something else happened
        return fallbackMessage;
    }
};
```

## Deployment Checklist

### Pre-deployment
- [ ] Frontend widget implemented with proper error handling
- [ ] Backend API endpoint created with validation
- [ ] Controller method implemented with logging
- [ ] Repository method created with efficient queries
- [ ] Schema models defined for request/response
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] API documentation updated
- [ ] Code reviewed and approved

### Post-deployment
- [ ] API endpoint accessible and responding correctly
- [ ] Widget displays data correctly in dashboard
- [ ] Error states handled gracefully
- [ ] Loading states working properly
- [ ] Performance acceptable under load
- [ ] Logs showing expected behavior
- [ ] Monitoring alerts configured

## Troubleshooting Common Issues

### 1. CORS Issues
**Problem**: Frontend can't access backend API
**Solution**: Configure CORS in FastAPI settings

### 2. Date Format Issues
**Problem**: Date validation failing
**Solution**: Ensure consistent YYYY-MM-DD format on both ends

### 3. Empty Data Handling
**Problem**: Widget crashes with empty data
**Solution**: Implement proper empty state handling

### 4. Performance Issues
**Problem**: Slow API responses
**Solution**: Add database indexing and optimize queries

### 5. Authentication Issues
**Problem**: API returns 401/403 errors
**Solution**: Ensure proper authentication headers in requests

This comprehensive guide should help you implement robust dashboard widget integrations following established patterns and best practices.
