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
const mockPaymentStatusData = {
    new: 45,
    process: 126,
    accepted: 85,
    done: 143
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
        // TODO: Replace with real API call when backend is ready
        // const response = await axios.get('/api/v1/dashboard/payment/status-distribution', {
        //     params: {
        //         dealer_id: effectiveDealerId.value,
        //         date_from: props.dateFrom,
        //         date_to: props.dateTo
        //     }
        // });

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Use mock data for now
        const data = mockPaymentStatusData;
        
        // Setup chart data
        chartData.value = {
            labels: ['New', 'Process', 'Accepted', 'Done'],
            datasets: [
                {
                    label: 'Payment Status',
                    data: [data.new, data.process, data.accepted, data.done],
                    backgroundColor: ['#4CAF50', '#FF9800', '#FFC107', '#E0E0E0'],
                    borderColor: ['#388E3C', '#F57C00', '#FFA000', '#BDBDBD'],
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
        error.value = 'Failed to fetch payment status data';
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
