<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import axios from 'axios';
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

// Chart colors for status prospect (ordered by priority)
const chartColors = [
    '#EF4444', // Red for Low
    '#F59E0B', // Orange for Medium
    '#FCD34D', // Yellow for Hot
    '#10B981', // Green for Deal
    '#6B7280' // Gray for Not Deal
];

// Computed property for legend items
const legendItems = computed(() => {
    if (!chartData.value || !chartData.value.labels) return [];

    const labels = chartData.value.labels;
    const values = chartData.value.datasets[0]?.data || [];
    const colors = chartData.value.datasets[0]?.backgroundColor || [];

    return labels.map((label, index) => ({
        label: label,
        count: values[index] || 0,
        color: colors[index] || '#ccc'
    }));
});

// Methods
const fetchStatusProspectData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call the new status prospect API
        const response = await axios.get('/api/v1/dashboard/prospect/status-counts', {
            params: {
                dealer_id: props.dealerId,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            const data = response.data.data;
            totalRecords.value = response.data.total_records;

            if (data.length === 0) {
                error.value = 'No status prospect data found for the selected criteria';
                chartData.value = {};
                return;
            }

            // Transform API response to component format
            const mappedData = data.map((item) => ({
                status: item.status_label || item.status_prospect || 'Unknown',
                count: item.count,
                originalStatus: item.status_prospect
            }));

            // Sort by count descending for better visualization
            mappedData.sort((a, b) => b.count - a.count);

            const labels = mappedData.map((item) => item.status);
            const values = mappedData.map((item) => item.count);
            const colors = chartColors.slice(0, mappedData.length);

            chartData.value = {
                labels: labels,
                datasets: [
                    {
                        label: 'Prospect Count',
                        data: values,
                        backgroundColor: colors,
                        borderColor: colors,
                        borderWidth: 1
                    }
                ]
            };

            // Chart options for vertical bar chart
            chartOptions.value = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const label = context.label || '';
                                const value = context.parsed.y;
                                return `${label}: ${value} prospects`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: Math.max(1, Math.ceil(Math.max(...values) / 10))
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 0
                        }
                    }
                }
            };
        } else {
            error.value = response.data.message || 'Failed to fetch status prospect data';
        }
    } catch (err) {
        console.error('Error fetching prospect status:', err);
        error.value = 'Failed to fetch prospect status data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        fetchStatusProspectData();
    },
    { deep: true }
);

// Lifecycle
onMounted(() => {
    fetchStatusProspectData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <span class="text-sm font-bold uppercase">STATUS PROSPECT</span>
                <small v-if="totalRecords > 0" class="text-muted-color"> Total: {{ totalRecords }} </small>
            </div>
        </template>

        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Chart Container -->
            <div v-if="!error && Object.keys(chartData).length > 0" class="space-y-4">
                <!-- Vertical Bar Chart -->
                <div class="h-64">
                    <Chart type="bar" :data="chartData" :options="chartOptions" class="h-full" />
                </div>

                <!-- Legend Below Chart -->
                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
                    <div v-for="(item, index) in legendItems" :key="index" class="flex items-center space-x-2 p-2 rounded border border-surface-200">
                        <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: item.color }"></div>
                        <div class="text-center">
                            <div class="text-xs font-medium">{{ item.label }}</div>
                            <div class="font-bold text-sm">{{ item.count }}</div>
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
.h-64 {
    height: 16rem;
}
</style>
