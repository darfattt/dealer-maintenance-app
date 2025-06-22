<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import Message from 'primevue/message';

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
const chartData = ref({});
const chartOptions = ref({});
const loading = ref(false);
const error = ref('');
const totalRecords = ref(0);

// Chart colors matching the image
const chartColors = [
    '#E91E63', // Pink for SMS (WA/LINE)
    '#FFC107', // Yellow for Call
    '#2196F3', // Blue for Visit
    '#4CAF50'  // Green for Direct Touch
];

// Computed property for legend items
const legendItems = computed(() => {
    if (!chartData.value || !chartData.value.labels) return [];
    
    const labels = chartData.value.labels;
    const values = chartData.value.datasets[0]?.data || [];
    const colors = chartData.value.datasets[0]?.backgroundColor || [];
    const total = values.reduce((sum, val) => sum + val, 0);
    
    return labels.map((label, index) => ({
        label: label,
        count: values[index] || 0,
        percentage: total > 0 ? ((values[index] / total) * 100).toFixed(0) : '0',
        color: colors[index] || '#ccc'
    }));
});

// Methods
const fetchMetodeFollowUpData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Dummy data matching the image
        const dummyData = [
            { method: 'SMS (WA/LINE)', count: 25, percentage: 25 },
            { method: 'Call', count: 19, percentage: 19 },
            { method: 'Visit', count: 11, percentage: 11 },
            { method: 'Direct Touch', count: 45, percentage: 45 }
        ];

        totalRecords.value = dummyData.reduce((sum, item) => sum + item.count, 0);

        const labels = dummyData.map(item => item.method);
        const values = dummyData.map(item => item.count);
        const colors = chartColors.slice(0, dummyData.length);

        chartData.value = {
            labels: labels,
            datasets: [
                {
                    data: values,
                    backgroundColor: colors,
                    borderColor: colors,
                    borderWidth: 1
                }
            ]
        };

        // Chart options for pie chart
        chartOptions.value = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        };
    } catch (err) {
        console.error('Error fetching follow-up method data:', err);
        error.value = 'Failed to fetch follow-up method data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchMetodeFollowUpData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchMetodeFollowUpData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <span class="text-sm font-bold uppercase">METODE FOLLOW UP</span>
                <small v-if="totalRecords > 0" class="text-muted-color">
                    Total: {{ totalRecords }}
                </small>
            </div>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Chart and Legend Container -->
            <div v-if="!error && Object.keys(chartData).length > 0" class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <!-- Pie Chart -->
                <div class="h-48">
                    <Chart
                        type="pie"
                        :data="chartData"
                        :options="chartOptions"
                        class="h-full"
                    />
                </div>

                <!-- Custom Legend -->
                <div class="flex flex-col justify-center">
                    <div class="space-y-2">
                        <div
                            v-for="(item, index) in legendItems"
                            :key="index"
                            class="flex items-center justify-between p-2 rounded border border-surface-200"
                        >
                            <div class="flex items-center space-x-2">
                                <div
                                    class="w-3 h-3 rounded-full"
                                    :style="{ backgroundColor: item.color }"
                                ></div>
                                <span class="text-xs font-medium">{{ item.label }}</span>
                            </div>
                            <div class="text-right">
                                <div class="font-bold text-sm">{{ item.percentage }}%</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading...</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
.h-48 {
    height: 12rem;
}
</style>
