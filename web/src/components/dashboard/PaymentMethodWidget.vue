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
const mockPaymentMethodData = {
    cash: 60,
    transfer: 40
};

// Methods
const fetchPaymentMethodData = async () => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // TODO: Replace with real API call when backend is ready
        // const response = await axios.get('/api/v1/dashboard/payment/method-distribution', {
        //     params: {
        //         dealer_id: effectiveDealerId.value,
        //         date_from: props.dateFrom,
        //         date_to: props.dateTo
        //     }
        // });

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Use mock data for now
        const data = mockPaymentMethodData;
        
        // Setup chart data
        chartData.value = {
            labels: ['Cash', 'Transfer'],
            datasets: [
                {
                    data: [data.cash, data.transfer],
                    backgroundColor: ['#00BCD4', '#2196F3'],
                    borderColor: ['#00ACC1', '#1976D2'],
                    borderWidth: 2
                }
            ]
        };

        // Setup chart options
        chartOptions.value = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${percentage}%`;
                        }
                    }
                }
            }
        };

    } catch (err) {
        console.error('Error fetching payment method data:', err);
        error.value = 'Failed to fetch payment method data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchPaymentMethodData();
}, { immediate: false });

// Lifecycle
onMounted(() => {
    fetchPaymentMethodData();
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

                <!-- Pie Chart -->
                <div v-else class="h-48">
                    <Chart 
                        type="pie" 
                        :data="chartData" 
                        :options="chartOptions"
                        class="w-full h-full"
                    />
                </div>
            </div>

            <!-- Empty State -->
            <div v-if="!loading && !error && (!chartData.datasets || chartData.datasets.length === 0)" class="text-center py-8">
                <i class="pi pi-info-circle text-2xl text-muted-color mb-2"></i>
                <p class="text-muted-color text-sm">No payment method data available</p>
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
