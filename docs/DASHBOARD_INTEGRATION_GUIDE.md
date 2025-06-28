# Dashboard Integration Guide

This document provides comprehensive guidance for integrating frontend dashboard widgets with backend APIs in the Dealer Management Application.

## Overview

The dashboard system follows a layered architecture:
- **Frontend**: Vue.js widgets that display data
- **Backend**: FastAPI microservice that provides data through REST endpoints
- **Database**: PostgreSQL with data repositories

## Architecture Flow

```
Dashboard.vue → Widget Components → API Endpoints → Controllers → Repositories → Database
```

## Sample Integration Examples

We have two fully integrated widgets that serve as reference implementations:

### 1. UnitInboundStatusWidget
- **Purpose**: Displays unit inbound status distribution as a vertical bar chart
- **API Endpoint**: `/api/v1/dashboard/unit-inbound/status-counts`
- **Data Source**: Unit inbound data grouped by shipping status

### 2. PaymentTypeWidget  
- **Purpose**: Displays payment type distribution as a pie chart
- **API Endpoint**: `/api/v1/dashboard/payment-type/statistics`
- **Data Source**: Billing process data grouped by payment type

## Frontend Implementation

### Widget Structure

Each dashboard widget follows this standard structure:

```vue
<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import axios from 'axios';
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import Message from 'primevue/message';

// Props from parent dashboard
const props = defineProps({
    dealerId: { type: String, default: '12284' },
    dateFrom: { type: String, required: true },
    dateTo: { type: String, required: true },
    showTitle: { type: Boolean, default: false } // For conditional titles
});

// Reactive data
const loading = ref(false);
const error = ref('');
const chartData = ref({});
const chartOptions = ref({});

// API call method
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
            // Process response data
            processChartData(response.data.data);
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

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchData();
});
</script>

<template>
    <Card class="h-full">
        <template #title v-if="showTitle">
            <span class="text-lg font-bold text-gray-800 uppercase tracking-wide">
                WIDGET TITLE
            </span>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Chart or Data Display -->
            <div v-if="!error && Object.keys(chartData).length > 0" class="h-80">
                <Chart
                    type="pie"
                    :data="chartData"
                    :options="chartOptions"
                    class="h-full"
                />
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading...</p>
            </div>

            <!-- Empty State -->
            <div v-if="!loading && !error && Object.keys(chartData).length === 0" class="text-center py-8">
                <i class="pi pi-info-circle text-2xl text-muted-color mb-2"></i>
                <p class="text-muted-color text-sm">No data available</p>
            </div>
        </template>
    </Card>
</template>
```

### Dashboard Integration

Add your widget to the Dashboard.vue:

```vue
<!-- Import the widget -->
import YourWidget from '@/components/dashboard/YourWidget.vue';

<!-- Use in template with external title -->
<div>
    <!-- External Title -->
    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
        <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
            Your Widget Title
        </h3>
    </div>
    <!-- Widget -->
    <div class="widget-with-title">
        <YourWidget
            :dealerId="selectedDealer"
            :dateFrom="formattedDateFrom"
            :dateTo="formattedDateTo"
        />
    </div>
</div>
```

## Backend Implementation

### 1. API Route (`routes/dashboard.py`)

```python
@router.get("/dashboard/your-endpoint", response_model=YourResponse)
async def get_your_data(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get your data for dashboard visualization
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        YourResponse: Contains your data and metadata
        
    Example:
        GET /api/v1/dashboard/your-endpoint?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
    """
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
        
        # Create controller and get data
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
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
```

### 2. Controller (`controllers/dashboard_controller.py`)

```python
async def get_your_data(
    self, 
    dealer_id: str, 
    date_from: str, 
    date_to: str
) -> YourResponse:
    """
    Get your data for dashboard
    
    Args:
        dealer_id: Dealer ID to filter by
        date_from: Start date (YYYY-MM-DD format)
        date_to: End date (YYYY-MM-DD format)
        
    Returns:
        YourResponse with your data
    """
    try:
        logger.info(f"Getting your data for dealer {dealer_id} from {date_from} to {date_to}")
        
        # Get data from repository
        data_items = self.repository.get_your_data(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        # Get total records if needed
        total_records = self.repository.get_total_records(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        logger.info(f"Found {len(data_items)} items with total {total_records} records")
        
        return YourResponse(
            success=True,
            message="Data retrieved successfully",
            data=data_items,
            total_records=total_records
        )
        
    except Exception as e:
        logger.error(f"Error getting your data: {str(e)}")
        return YourResponse(
            success=False,
            message=f"Error retrieving data: {str(e)}",
            data=[],
            total_records=0
        )
```

### 3. Repository (`repositories/dashboard_repository.py`)

```python
def get_your_data(self, dealer_id: str, date_from: str, date_to: str) -> List[YourDataItem]:
    """
    Get your data from database

    Args:
        dealer_id: Dealer ID to filter by
        date_from: Start date (YYYY-MM-DD format)
        date_to: End date (YYYY-MM-DD format)

    Returns:
        List of YourDataItem objects
    """
    try:
        query = self.db.query(YourModel).filter(
            YourModel.dealer_id == dealer_id,
            YourModel.created_date >= date_from,
            YourModel.created_date <= date_to
        )

        # Group by your criteria and count
        result = query.group_by(YourModel.your_field).all()

        return [
            YourDataItem(
                field_name=item.your_field,
                count=item.count,
                amount=item.total_amount  # if applicable
            )
            for item in result
        ]

    except Exception as e:
        logger.error(f"Error in get_your_data: {str(e)}")
        raise
```

### 4. Schema (`schemas/dashboard.py`)

```python
from pydantic import BaseModel
from typing import List, Optional

class YourDataItem(BaseModel):
    """Individual data item"""
    field_name: str
    count: int
    amount: Optional[float] = None

class YourResponse(BaseModel):
    """Response model for your endpoint"""
    success: bool
    message: str
    data: List[YourDataItem]
    total_records: int
    total_amount: Optional[float] = None
```
