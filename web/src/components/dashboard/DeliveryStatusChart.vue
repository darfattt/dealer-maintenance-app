<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import Message from 'primevue/message';

// Props
const props = defineProps({
    stats: {
        type: Object,
        default: () => ({})
    },
    loading: {
        type: Boolean,
        default: false
    }
});

// Reactive data
const chartData = ref({});
const chartOptions = ref({});

// Computed properties
const hasData = computed(() => {
    const stats = props.stats;
    return stats.total_requests > 0;
});

const chartTitle = computed(() => {
    const total = props.stats.total_requests || 0;
    return `WhatsApp Delivery Status (${total} total)`;
});

// Initialize chart configuration
const initChart = () => {
    const stats = props.stats;
    
    if (!hasData.value) {
        chartData.value = {};
        return;
    }

    const delivered = stats.delivered_count || 0;
    const failed = stats.failed_count || 0;
    const pending = stats.pending_count || 0;

    chartData.value = {
        labels: ['Delivered', 'Failed', 'Pending'],
        datasets: [{
            data: [delivered, failed, pending],
            backgroundColor: [
                '#10B981', // Green for delivered
                '#EF4444', // Red for failed
                '#F59E0B'  // Orange for pending
            ],
            borderWidth: 2,
            borderColor: '#ffffff'
        }]
    };

    chartOptions.value = {
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 20,
                    usePointStyle: true,
                    font: {
                        size: 12
                    }
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const value = context.parsed;
                        const total = delivered + failed + pending;
                        const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                        return `${context.label}: ${value} (${percentage}%)`;
                    }
                }
            }
        },
        responsive: true,
        maintainAspectRatio: false,
        cutout: '40%'
    };
};

// Watch for stats changes
watch(() => props.stats, initChart, { immediate: true, deep: true });

// Initialize on mount
onMounted(() => {
    initChart();
});
</script>

<template>
    <Card class="delivery-status-chart">
        <template #title>
            <h3 class="text-lg font-semibold text-surface-900 mb-2">{{ chartTitle }}</h3>
        </template>
        <template #content>
            <div v-if="loading" class="flex justify-center items-center h-64">
                <div class="text-surface-500">Loading chart data...</div>
            </div>
            
            <div v-else-if="!hasData" class="flex flex-col items-center justify-center h-64">
                <Message severity="info" :closable="false">
                    No data available for the selected period
                </Message>
            </div>
            
            <div v-else class="chart-container h-64">
                <Chart 
                    type="doughnut" 
                    :data="chartData" 
                    :options="chartOptions"
                    class="w-full h-full"
                />
            </div>

            <!-- Summary Stats -->
            <div v-if="hasData && !loading" class="mt-4 grid grid-cols-3 gap-4 text-center">
                <div class="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg border border-green-200 dark:border-green-800">
                    <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ stats.delivered_count || 0 }}</div>
                    <div class="text-sm text-green-700 dark:text-green-300">Delivered</div>
                </div>
                <div class="bg-red-50 dark:bg-red-900/20 p-3 rounded-lg border border-red-200 dark:border-red-800">
                    <div class="text-2xl font-bold text-red-600 dark:text-red-400">{{ stats.failed_count || 0 }}</div>
                    <div class="text-sm text-red-700 dark:text-red-300">Failed</div>
                </div>
                <div class="bg-orange-50 dark:bg-orange-900/20 p-3 rounded-lg border border-orange-200 dark:border-orange-800">
                    <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ stats.pending_count || 0 }}</div>
                    <div class="text-sm text-orange-700 dark:text-orange-300">Pending</div>
                </div>
            </div>

            <!-- Delivery Percentage -->
            <div v-if="hasData && !loading" class="mt-4 text-center">
                <div class="text-sm text-surface-500 dark:text-surface-400">Delivery Success Rate</div>
                <div class="text-xl font-bold text-surface-900 dark:text-surface-100">{{ stats.delivery_percentage || 0 }}%</div>
            </div>
        </template>
    </Card>
</template>

<style scoped>
.delivery-status-chart :deep(.p-card-body) {
    padding: 1.5rem;
}

.delivery-status-chart :deep(.p-card-title) {
    margin-bottom: 1rem;
}

.chart-container {
    position: relative;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .chart-container {
        height: 200px;
    }
    
    .grid-cols-3 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
        gap: 0.5rem;
    }
}
</style>