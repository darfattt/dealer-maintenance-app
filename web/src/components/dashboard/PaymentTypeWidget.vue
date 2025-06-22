<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import Message from 'primevue/message';
import axios from 'axios';

// Props from parent dashboard
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
const paymentData = ref([]);
const chartData = ref({});
const chartOptions = ref({});
const totalAmount = ref(0);

// Chart colors for payment types
const chartColors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'];

// Computed property for legend items
const legendItems = computed(() => {
    if (!chartData.value || !chartData.value.labels) return [];

    const labels = chartData.value.labels;
    const values = chartData.value.datasets[0]?.data || [];
    const colors = chartData.value.datasets[0]?.backgroundColor || [];
    const total = values.reduce((sum, val) => sum + val, 0);

    return labels.map((label, index) => ({
        label: label,
        amount: values[index] || 0,
        percentage: total > 0 ? ((values[index] / total) * 100).toFixed(1) : '0.0',
        color: colors[index] || '#ccc',
        formattedAmount: formatAmount(values[index] || 0)
    }));
});

// Methods
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
                    datasets: [
                        {
                            data: values,
                            backgroundColor: colors,
                            borderColor: colors,
                            borderWidth: 2
                        }
                    ]
                };

                // Chart options
                chartOptions.value = {
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {
                        padding: {
                            top: 20,
                            bottom: 20,
                            left: 20,
                            right: 20
                        }
                    },
                    plugins: {
                        legend: {
                            display: false // Hide default legend since we're using custom legend
                        },
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
        if (err.response?.status === 404) {
            error.value = 'Payment type data not available for this dealer';
        } else if (err.response?.status === 500) {
            error.value = 'Server error while fetching payment type data';
        } else {
            error.value = 'Failed to fetch payment type data';
        }
    } finally {
        loading.value = false;
    }
};

// Helper function to map payment type codes to labels
const mapPaymentType = (tipeCode) => {
    const typeMap = {
        '1': 'CASH',
        '2': 'CREDIT',
        '3': 'LEASING',
        'CASH': 'CASH',
        'CREDIT': 'CREDIT',
        'LEASING': 'LEASING'
    };
    return typeMap[tipeCode] || tipeCode || 'UNKNOWN';
};

// Helper function to get color for payment type
const getPaymentTypeColor = (paymentType) => {
    const colorMap = {
        '1': '#10B981',      // Cash - Green
        '2': '#3B82F6',      // Credit - Blue
        '3': '#F59E0B',      // Leasing - Orange
        'CASH': '#10B981',
        'CREDIT': '#3B82F6',
        'LEASING': '#F59E0B',
        'OTHER': '#6B7280'
    };
    return colorMap[paymentType] || '#6B7280';
};

// Helper function to format amount
const formatAmount = (amount) => {
    if (!amount || amount === 0) return '0';

    // Convert to millions for better readability
    const millions = amount / 1000000;

    if (millions >= 1000) {
        // Show in billions
        return `${(millions / 1000).toFixed(1)}B`;
    } else if (millions >= 1) {
        // Show in millions
        return `${millions.toFixed(0)}M`;
    } else {
        // Show in thousands
        return `${(amount / 1000).toFixed(0)}K`;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchPaymentTypeData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchPaymentTypeData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <span>Tipe Pembayaran</span>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Chart and Legend Container -->
            <div v-if="!error && Object.keys(chartData).length > 0" class="grid grid-cols-1 lg:grid-cols-5 gap-4">
                <!-- Pie Chart -->
                <div class="lg:col-span-3">
                    <div class="h-80 p-2">
                        <Chart
                            type="pie"
                            :data="chartData"
                            :options="chartOptions"
                            class="h-full w-full"
                        />
                    </div>
                </div>

                <!-- Custom Legend -->
                <div class="lg:col-span-2 flex flex-col justify-center">
                    <h4 class="text-sm font-semibold mb-3 text-center text-surface-700">Payment Distribution</h4>
                    <div class="space-y-2">
                        <div
                            v-for="(item, index) in legendItems"
                            :key="index"
                            class="flex items-center justify-between p-3 rounded-lg border border-surface-200 hover:bg-surface-50 transition-all duration-200 hover:shadow-sm"
                        >
                            <div class="flex items-center space-x-2 min-w-0">
                                <div
                                    class="w-4 h-4 rounded-full flex-shrink-0 shadow-sm"
                                    :style="{ backgroundColor: item.color }"
                                ></div>
                                <span class="font-medium text-xs text-surface-700 truncate">{{ item.label }}</span>
                            </div>
                            <div class="text-right ml-2 flex-shrink-0">
                                <div class="font-bold text-sm text-surface-800">{{ item.formattedAmount }}</div>
                                <div class="text-xs text-surface-500 font-medium">{{ item.percentage }}%</div>
                            </div>
                        </div>
                    </div>

                    <!-- Total Summary -->
                    <div class="mt-3 p-2 bg-primary-50 rounded-lg border border-primary-200">
                        <div class="flex justify-between items-center">
                            <span class="font-semibold text-xs text-primary-700">Total Amount</span>
                            <span class="font-bold text-lg text-primary-700">{{ formatAmount(totalAmount) }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- No Data State -->
            <div v-else-if="!loading && !error" class="text-center py-8">
                <i class="pi pi-chart-pie text-4xl text-muted-color mb-4"></i>
                <p class="text-muted-color">No payment data available for the selected criteria</p>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-4xl text-primary mb-4"></i>
                <p class="text-muted-color">Loading chart data...</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
.h-80 {
    height: 20rem;
}

/* Ensure chart container doesn't overflow */
:deep(.p-chart) {
    position: relative;
    overflow: hidden;
}

/* Responsive text sizing */
@media (max-width: 1024px) {
    .h-80 {
        height: 16rem;
    }
}

@media (max-width: 768px) {
    .h-80 {
        height: 14rem;
    }
}
</style>
