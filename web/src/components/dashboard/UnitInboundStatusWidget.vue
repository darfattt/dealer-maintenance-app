<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import Message from 'primevue/message';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

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

// Auth store
const authStore = useAuthStore();

// Reactive data
const chartData = ref({});
const chartOptions = ref({});
const loading = ref(false);
const error = ref('');
const totalRecords = ref(0);
const userDealers = ref([]); // For DEALER_USER role

// Chart colors
const chartColors = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
];

// Status mapping for unit inbound
const statusMapping = {
    '0': 'Belum Diterima',
    '1': 'Sudah Diterima'
};

// Computed properties
// Check if user is DEALER_USER role
const isDealerUser = computed(() => {
    return authStore.userRole === 'DEALER_USER';
});

// Get effective dealer ID (from props or user assignment)
const effectiveDealerId = computed(() => {
    if (isDealerUser.value && userDealers.value.length > 0) {
        return userDealers.value[0];
    }
    return props.dealerId;
});

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
        percentage: total > 0 ? ((values[index] / total) * 100).toFixed(1) : '0.0',
        color: colors[index] || '#ccc'
    }));
});

// Methods
const fetchUserDealers = async () => {
    if (!isDealerUser.value) return;

    try {
        const response = await axios.get('/api/v1/user-dealers/me/dealers');
        userDealers.value = response.data;
    } catch (err) {
        console.error('Error fetching user dealers:', err);
        error.value = 'Failed to fetch assigned dealers';
    }
};

const fetchUnitInboundStatus = async () => {
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

            // Prepare chart data - use status_label from API if available, otherwise use mapping
            const mappedData = data.map(item => ({
                status: item.status_label || statusMapping[item.status_shipping_list] || item.status_shipping_list || 'Unknown',
                count: item.count,
                originalStatus: item.status_shipping_list
            }));

            // Group by mapped status (in case multiple original statuses map to the same label)
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
                datasets: [
                    {
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
                indexAxis: 'x', // This makes it a vertical bar chart
                layout: {
                    padding: {
                        top: 20,
                        bottom: 20,
                        left: 10,
                        right: 10
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
                                const value = context.parsed.y;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} unit (${percentage}%)`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            font: {
                                size: 11
                            },
                            maxRotation: 45,
                            minRotation: 0,
                            padding: 5
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            font: {
                                size: 11
                            },
                            stepSize: 1,
                            padding: 5
                        }
                    }
                }
            };
        } else {
            error.value = response.data.message || 'Failed to fetch data';
        }
    } catch (err) {
        console.error('Error fetching unit inbound status:', err);
        error.value = 'Failed to fetch unit inbound status data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchUnitInboundStatus();
}, { deep: true });

// Lifecycle
onMounted(async () => {
    // Fetch user dealers first if DEALER_USER role
    if (isDealerUser.value) {
        await fetchUserDealers();
    }

    // Then fetch the chart data
    fetchUnitInboundStatus();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <span>Unit Inbound Status Distribution</span>
                <small v-if="totalRecords > 0" class="text-muted-color">
                    Total Records: {{ totalRecords }}
                </small>
            </div>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Chart and Legend Container -->
            <div v-if="!error && Object.keys(chartData).length > 0" class="grid grid-cols-1 lg:grid-cols-5 gap-4">
                <!-- Vertical Bar Chart -->
                <div class="lg:col-span-3">
                    <div class="h-80 p-2">
                        <Chart
                            type="bar"
                            :data="chartData"
                            :options="chartOptions"
                            class="h-full w-full"
                        />
                    </div>
                </div>

                <!-- Custom Legend -->
                <div class="lg:col-span-2 flex flex-col justify-center">
                    <h4 class="text-sm font-semibold mb-3 text-center text-surface-700">Status Distribution</h4>
                    <div class="space-y-2">
                        <div
                            v-for="(item, index) in legendItems"
                            :key="index"
                            class="flex items-center justify-between p-3 rounded-lg border border-surface-200 hover:bg-surface-50 transition-all duration-200 hover:shadow-sm"
                        >
                            <div class="flex items-center space-x-2">
                                <div
                                    class="w-4 h-4 rounded-full flex-shrink-0 shadow-sm"
                                    :style="{ backgroundColor: item.color }"
                                ></div>
                                <span class="font-medium text-xs text-surface-700 truncate">{{ item.label }}</span>
                            </div>
                            <div class="text-right ml-2">
                                <div class="font-bold text-sm text-surface-800">{{ item.count }}</div>
                                <div class="text-xs text-surface-500 font-medium">{{ item.percentage }}%</div>
                            </div>
                        </div>
                    </div>

                    <!-- Total Summary -->
                    <div class="mt-3 p-2 bg-primary-50 rounded-lg border border-primary-200">
                        <div class="flex justify-between items-center">
                            <span class="font-semibold text-xs text-primary-700">Total Units</span>
                            <span class="font-bold text-lg text-primary-700">{{ totalRecords }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- No Data State -->
            <div v-else-if="!loading && !error" class="text-center py-8">
                <i class="pi pi-chart-bar text-4xl text-muted-color mb-4"></i>
                <p class="text-muted-color">No data available for the selected criteria</p>
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
