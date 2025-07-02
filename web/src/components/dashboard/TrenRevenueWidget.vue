<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import Card from 'primevue/card';
import Chart from 'primevue/chart';
import Message from 'primevue/message';

// Props from parent
const props = defineProps({
    dealerId: {
        type: String,
        default: '12284'
    },
    dateFrom: {
        type: String,
        required: true
    },
    dateTo: {
        type: String,
        required: true
    }
});

// Reactive data
const loading = ref(false);
const error = ref('');
const chartData = ref({});
const chartOptions = ref({});

// Computed properties
const effectiveDealerId = computed(() => {
    return props.dealerId || '12284';
});

// Mock data for demonstration (will be replaced with real API later)
const mockTrenRevenueData = {
    months: ['Jan', 'Feb', 'March', 'Apr', 'May', 'Jun'],
    revenue_bars: [50, 35, 60, 30, 25, 35], // Bar chart data (in millions)
    revenue_line: [52, 38, 58, 28, 22, 37]  // Line chart data (in millions)
};

// Methods
const fetchTrenRevenueData = async () => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // TODO: Replace with real API call when backend is ready
        // const response = await axios.get('/api/v1/dashboard/payment/revenue-trend', {
        //     params: {
        //         dealer_id: effectiveDealerId.value,
        //         date_from: props.dateFrom,
        //         date_to: props.dateTo
        //     }
        // });

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1200));

        // Use mock data for now
        const data = mockTrenRevenueData;
        
        // Setup chart data with mixed chart types
        chartData.value = {
            labels: data.months,
            datasets: [
                {
                    type: 'bar',
                    label: 'Revenue (Bar)',
                    data: data.revenue_bars,
                    backgroundColor: '#4CAF50',
                    borderColor: '#388E3C',
                    borderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    type: 'line',
                    label: 'Revenue Trend (Line)',
                    data: data.revenue_line,
                    borderColor: '#F44336',
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointBackgroundColor: '#F44336',
                    pointBorderColor: '#D32F2F',
                    pointRadius: 4,
                    yAxisID: 'y'
                }
            ]
        };

        // Setup chart options
        chartOptions.value = {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 11
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            return `${label}: ${value}M`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    max: 80,
                    grid: {
                        color: '#E5E7EB'
                    },
                    ticks: {
                        font: {
                            size: 10
                        },
                        callback: function(value) {
                            return value + 'M';
                        }
                    }
                }
            }
        };

    } catch (err) {
        console.error('Error fetching revenue trend data:', err);
        error.value = 'Failed to fetch revenue trend data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchTrenRevenueData();
}, { immediate: false });

// Lifecycle
onMounted(() => {
    fetchTrenRevenueData();
});
</script>

<template>
    <Card class="h-full">
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Chart Container -->
            <div v-if="!error" class="chart-container">
                <!-- Loading State -->
                <div v-if="loading" class="flex items-center justify-center h-64">
                    <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                </div>

                <!-- Mixed Chart (Line + Bar) -->
                <div v-else class="h-64">
                    <Chart 
                        type="bar" 
                        :data="chartData" 
                        :options="chartOptions"
                        class="w-full h-full"
                    />
                </div>
            </div>

            <!-- Empty State -->
            <div v-if="!loading && !error && (!chartData.datasets || chartData.datasets.length === 0)" class="text-center py-8">
                <i class="pi pi-info-circle text-2xl text-muted-color mb-2"></i>
                <p class="text-muted-color text-sm">No revenue trend data available</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
.chart-container {
    width: 100%;
    height: 100%;
    min-height: 280px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .chart-container {
        min-height: 250px;
    }
}
</style>
