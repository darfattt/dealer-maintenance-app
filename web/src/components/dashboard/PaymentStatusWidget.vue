<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import Card from 'primevue/card';
import Chart from 'primevue/chart';
import Message from 'primevue/message';
import axios from 'axios';

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

// Default colors for payment status chart
const statusColors = {
    'New': '#4CAF50',
    'Process': '#FF9800',
    'Accepted': '#FFC107',
    'Close': '#E0E0E0'
};

const statusBorderColors = {
    'New': '#388E3C',
    'Process': '#F57C00',
    'Accepted': '#FFA000',
    'Close': '#BDBDBD'
};

// Methods
const fetchPaymentStatusData = async () => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call real API endpoint
        const response = await axios.get('/api/v1/dashboard/payment-status/statistics', {
            params: {
                dealer_id: effectiveDealerId.value,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (!response.data.success) {
            throw new Error(response.data.message || 'Failed to fetch payment status data');
        }

        // Process API response
        const apiData = response.data.data || [];

        if (apiData.length === 0) {
            // Handle empty data case
            chartData.value = {
                labels: [],
                datasets: []
            };
            return;
        }

        // Transform API data to chart format
        const labels = apiData.map(item => item.status_label || 'Unknown');
        const data = apiData.map(item => item.count);
        const backgroundColor = labels.map(label => statusColors[label] || '#9E9E9E');
        const borderColor = labels.map(label => statusBorderColors[label] || '#757575');

        // Setup chart data
        chartData.value = {
            labels: labels,
            datasets: [
                {
                    label: 'Payment Status',
                    data: data,
                    backgroundColor: backgroundColor,
                    borderColor: borderColor,
                    borderWidth: 1
                }
            ]
        };

        // Setup chart options
        chartOptions.value = {
            indexAxis: 'y', // This makes it horizontal
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed.x}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        display: true,
                        color: '#E5E7EB'
                    },
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                }
            }
        };

    } catch (err) {
        console.error('Error fetching payment status data:', err);
        error.value = err.response?.data?.message || err.message || 'Failed to fetch payment status data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchPaymentStatusData();
}, { immediate: false });

// Lifecycle
onMounted(() => {
    fetchPaymentStatusData();
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
                <div v-if="loading" class="flex items-center justify-center h-48">
                    <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                </div>

                <!-- Horizontal Bar Chart -->
                <div v-else class="h-48">
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
                <p class="text-muted-color text-sm">No payment status data available</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
.chart-container {
    width: 100%;
    height: 100%;
    min-height: 200px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .chart-container {
        min-height: 180px;
    }
}
</style>
