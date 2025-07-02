<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import Card from 'primevue/card';
import Chart from 'primevue/chart';
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
const loading = ref(false);
const error = ref('');
const poCreationData = ref([]);
const totalRecords = ref(0);

// Chart configuration
const chartData = ref({});
const chartOptions = ref({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false
        },
        tooltip: {
            callbacks: {
                label: function(context) {
                    return `PO Created: ${context.parsed.y}`;
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
                    size: 11
                }
            }
        },
        y: {
            beginAtZero: true,
            grid: {
                color: '#f1f5f9'
            },
            ticks: {
                font: {
                    size: 11
                },
                stepSize: 50
            }
        }
    }
});

// Methods
const fetchPOCreationData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // TODO: Replace with real API endpoint
        const response = await axios.get('/api/v1/dashboard/leasing/po-creation-monthly', {
            params: {
                dealer_id: props.dealerId,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            const data = response.data.data;
            totalRecords.value = response.data.total_records || 0;

            if (data.length === 0) {
                error.value = 'No PO creation data found for the selected criteria';
                poCreationData.value = [];
                updateChartData([]);
                return;
            }

            poCreationData.value = data;
            updateChartData(data);
        } else {
            error.value = response.data.message || 'Failed to fetch PO creation data';
        }
    } catch (err) {
        console.error('Error fetching PO creation data:', err);
        
        // Mock data for development
        const mockData = [
            { month: 'Jan', count: 350 },
            { month: 'Feb', count: 380 },
            { month: 'Mar', count: 370 },
            { month: 'Apr', count: 360 },
            { month: 'May', count: 375 },
            { month: 'Jun', count: 340 },
            { month: 'Jul', count: 365 },
            { month: 'Aug', count: 0 },
            { month: 'Sep', count: 0 },
            { month: 'Oct', count: 0 },
            { month: 'Nov', count: 0 },
            { month: 'Dec', count: 0 }
        ];
        
        poCreationData.value = mockData;
        totalRecords.value = mockData.reduce((sum, item) => sum + item.count, 0);
        updateChartData(mockData);
        error.value = '';
    } finally {
        loading.value = false;
    }
};

const updateChartData = (data) => {
    chartData.value = {
        labels: data.map(item => item.month),
        datasets: [
            {
                data: data.map(item => item.count),
                backgroundColor: '#F59E0B', // Amber color matching the design
                borderColor: '#D97706',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false,
            }
        ]
    };
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchPOCreationData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchPOCreationData();
});
</script>

<template>
    <Card class="h-full">
        <template #content>
            <!-- Total Records Info -->
            <div v-if="totalRecords > 0" class="flex justify-end mb-4">
                <small class="text-muted-color">
                    Total: {{ totalRecords.toLocaleString() }}
                </small>
            </div>
            
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Loading State -->
            <div v-if="loading" class="flex justify-center items-center h-64">
                <i class="pi pi-spinner pi-spin text-2xl text-primary"></i>
            </div>

            <!-- Chart -->
            <div v-else-if="!error && poCreationData.length > 0" class="h-64">
                <Chart 
                    type="bar" 
                    :data="chartData" 
                    :options="chartOptions"
                    class="h-full"
                />
            </div>

            <!-- No Data State -->
            <div v-else-if="!loading && !error && poCreationData.length === 0" 
                 class="flex flex-col items-center justify-center h-64 text-surface-500">
                <i class="pi pi-chart-bar text-4xl mb-4"></i>
                <p class="text-lg font-medium">No PO Creation Data</p>
                <p class="text-sm">No data available for the selected period</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* Custom styles if needed */
</style>
