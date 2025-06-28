# Dashboard API Integration Examples

This document provides detailed examples of the two fully integrated dashboard widgets that serve as reference implementations.

## Reference Implementation Examples

### 1. UnitInboundStatusWidget Integration

#### Frontend Implementation

**File**: `web/src/components/dashboard/UnitInboundStatusWidget.vue`

```javascript
// API call method
const fetchUnitInboundStatusData = async () => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        const response = await axios.get('/api/v1/dashboard/unit-inbound/status-counts', {
            params: {
                dealer_id: effectiveDealerId.value,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            const data = response.data.data;
            totalRecords.value = response.data.total_records;

            if (data.length === 0) {
                error.value = 'No data found for the selected criteria';
                chartData.value = {};
                return;
            }

            // Prepare chart data - use status_label from API if available
            const mappedData = data.map(item => ({
                status: item.status_label || statusMapping[item.status_shipping_list] || item.status_shipping_list || 'Unknown',
                count: item.count,
                originalStatus: item.status_shipping_list
            }));

            // Group by mapped status
            const groupedData = mappedData.reduce((acc, item) => {
                const existing = acc.find(x => x.status === item.status);
                if (existing) {
                    existing.count += item.count;
                } else {
                    acc.push({ status: item.status, count: item.count });
                }
                return acc;
            }, []);

            const labels = groupedData.map(item => item.status);
            const values = groupedData.map(item => item.count);
            const colors = chartColors.slice(0, groupedData.length);

            chartData.value = {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderColor: colors,
                    borderWidth: 1
                }]
            };

            // Chart options for vertical bar chart
            chartOptions.value = {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'x', // Vertical bar chart
                layout: {
                    padding: { top: 20, bottom: 20, left: 20, right: 20 }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed.y;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    },
                    x: {
                        ticks: { maxRotation: 45, minRotation: 0 }
                    }
                }
            };
        } else {
            error.value = response.data.message || 'Failed to fetch unit inbound status data';
        }
    } catch (err) {
        console.error('Error fetching unit inbound status data:', err);
        error.value = 'Failed to fetch unit inbound status data';
    } finally {
        loading.value = false;
    }
};
```

#### Backend Implementation

**Route**: `backend-microservices/services/dashboard-dealer/app/routes/dashboard.py`

```python
@router.get("/dashboard/unit-inbound/status-counts", response_model=UnitInboundStatusResponse)
async def get_unit_inbound_status_counts(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get unit inbound data count grouped by status_shipping_list for pie chart visualization
    
    This endpoint returns statistics about unit inbound data grouped by shipping list status
    for a specific dealer within a date range. The data is suitable for pie chart visualization.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        UnitInboundStatusResponse: Contains status counts and total records
        
    Example:
        GET /api/v1/dashboard/unit-inbound/status-counts?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_unit_inbound_status_statistics(
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

**Controller**: `backend-microservices/services/dashboard-dealer/app/controllers/dashboard_controller.py`

```python
async def get_unit_inbound_status_statistics(
    self, 
    dealer_id: str, 
    date_from: str, 
    date_to: str
) -> UnitInboundStatusResponse:
    """
    Get unit inbound status statistics for pie chart
    
    Args:
        dealer_id: Dealer ID to filter by
        date_from: Start date (YYYY-MM-DD format)
        date_to: End date (YYYY-MM-DD format)
        
    Returns:
        UnitInboundStatusResponse with status counts
    """
    try:
        logger.info(f"Getting unit inbound status statistics for dealer {dealer_id} from {date_from} to {date_to}")
        
        # Get status counts
        status_items = self.repository.get_unit_inbound_status_counts(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        # Get total records
        total_records = self.repository.get_total_unit_inbound_records(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        logger.info(f"Found {len(status_items)} different statuses with total {total_records} records")
        
        return UnitInboundStatusResponse(
            success=True,
            message="Unit inbound status statistics retrieved successfully",
            data=status_items,
            total_records=total_records
        )
        
    except Exception as e:
        logger.error(f"Error getting unit inbound status statistics: {str(e)}")
        return UnitInboundStatusResponse(
            success=False,
            message=f"Error retrieving data: {str(e)}",
            data=[],
            total_records=0
        )
```

### 2. PaymentTypeWidget Integration

#### Frontend Implementation

**File**: `web/src/components/dashboard/PaymentTypeWidget.vue`

```javascript
// API call method
const fetchPaymentTypeData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call real API endpoint
        const response = await axios.get('/api/v1/dashboard/payment-type/statistics', {
            params: {
                dealer_id: props.dealerId,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            // Transform API response to component format
            paymentData.value = response.data.data.map(item => ({
                type: mapPaymentType(item.tipe_pembayaran),
                amount: parseFloat(item.total_amount) || 0,
                color: getPaymentTypeColor(item.tipe_pembayaran)
            }));

            // Calculate total amount
            totalAmount.value = paymentData.value.reduce((sum, item) => sum + item.amount, 0);

            // Prepare chart data
            if (paymentData.value.length > 0) {
                const labels = paymentData.value.map(item => item.type);
                const values = paymentData.value.map(item => item.amount);
                const colors = paymentData.value.map((_, index) =>
                    chartColors[index % chartColors.length]
                );

                chartData.value = {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: colors,
                        borderColor: colors,
                        borderWidth: 2
                    }]
                };

                // Chart options
                chartOptions.value = {
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {
                        padding: { top: 20, bottom: 20, left: 20, right: 20 }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${formatAmount(value)} (${percentage}%)`;
                                }
                            }
                        }
                    }
                };
            } else {
                chartData.value = {};
                error.value = 'No payment type data found for the selected criteria';
            }
        } else {
            error.value = response.data.message || 'Failed to fetch payment type data';
        }
    } catch (err) {
        console.error('Error fetching payment type data:', err);
        error.value = 'Failed to fetch payment type data';
    } finally {
        loading.value = false;
    }
};

// Helper functions
const mapPaymentType = (type) => {
    const mapping = {
        'CASH': 'Cash',
        'CREDIT': 'Credit',
        'KREDIT': 'Credit'
    };
    return mapping[type?.toUpperCase()] || type || 'Unknown';
};

const getPaymentTypeColor = (type) => {
    const colorMapping = {
        'CASH': '#4CAF50',
        'CREDIT': '#FF9800',
        'KREDIT': '#FF9800'
    };
    return colorMapping[type?.toUpperCase()] || '#9E9E9E';
};

const formatAmount = (amount) => {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
};
```
