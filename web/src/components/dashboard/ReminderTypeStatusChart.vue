<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';
import CustomerService from '@/service/CustomerService';

// Props from parent
const props = defineProps({
    stats: {
        type: Object,
        default: () => ({})
    },
    loading: {
        type: Boolean,
        default: false
    },
    dateFrom: {
        type: String,
        required: true
    },
    dateTo: {
        type: String,
        required: true
    },
    dealerId: {
        type: String,
        default: null
    },
    reminderTarget: {
        type: String,
        default: null
    }
});

// Reactive data
const chartLoading = ref(false);
const chartError = ref('');
const chartData = ref({});
const chartOptions = ref({});

// Chart type state
const chartType = ref('bar');

// Load chart data from API
const loadChartData = async () => {
    chartLoading.value = true;
    chartError.value = '';
    
    try {
        const response = await CustomerService.getReminderTypeWhatsAppStatusStats(
            props.dateFrom,
            props.dateTo,
            props.dealerId,
            props.reminderTarget
        );
        
        if (response.success && response.data) {
            updateChartData(response.data);
        } else {
            throw new Error(response.message || 'Failed to fetch chart data');
        }
    } catch (error) {
        console.error('Error loading reminder type status chart data:', error);
        chartError.value = 'Failed to load chart data';
        
        // Use fallback mock data
        updateChartData({
            'KPB-1': { 'SENT': 15, 'FAILED': 2, 'NOT_SENT': 1 },
            'KPB-2': { 'SENT': 8, 'FAILED': 1 },
            'Non KPB': { 'SENT': 5, 'FAILED': 3, 'NOT_SENT': 2 }
        });
    } finally {
        chartLoading.value = false;
    }
};

// Update chart data structure
const updateChartData = (apiData) => {
    // Extract reminder types and status types
    const reminderTypes = Object.keys(apiData);
    const statusTypes = ['SENT', 'FAILED', 'NOT_SENT'];
    
    // Create datasets for each WhatsApp status
    const datasets = statusTypes.map(status => {
        const statusLabel = getStatusLabel(status);
        const statusColor = getStatusColor(status);
        
        return {
            label: statusLabel,
            data: reminderTypes.map(type => apiData[type]?.[status] || 0),
            backgroundColor: statusColor,
            borderColor: statusColor,
            borderWidth: 1
        };
    }).filter(dataset => dataset.data.some(value => value > 0)); // Only include datasets with data
    
    chartData.value = {
        labels: reminderTypes.map(type => getReminderTypeLabel(type)),
        datasets: datasets
    };
};

// Get status label for display
const getStatusLabel = (status) => {
    switch (status) {
        case 'SENT':
            return 'Terkirim';
        case 'FAILED':
            return 'Gagal';
        case 'NOT_SENT':
            return 'Belum Dikirim';
        default:
            return status;
    }
};

// Get status color
const getStatusColor = (status) => {
    switch (status) {
        case 'SENT':
            return '#22C55E'; // Green
        case 'FAILED':
            return '#EF4444'; // Red
        case 'NOT_SENT':
            return '#94A3B8'; // Gray
        default:
            return '#64748B'; // Default gray
    }
};

// Get reminder type label for display
const getReminderTypeLabel = (type) => {
    if (!type) return 'Unknown';
    
    // Handle KPB types
    if (type.includes('KPB')) {
        return type.replace('-', ' ');
    }
    
    return type;
};

// Setup chart options
const setupChartOptions = () => {
    chartOptions.value = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: true,
                text: '',
                font: {
                    size: 16,
                    weight: 'bold'
                },
                padding: 20
            },
            legend: {
                display: true,
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 20
                }
            },
            tooltip: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(context) {
                        return `${context.dataset.label}: ${context.parsed.y}`;
                    }
                }
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Reminder Type'
                },
                grid: {
                    display: false
                }
            },
            y: {
                title: {
                    display: true,
                    text: ''
                },
                beginAtZero: true,
                ticks: {
                    stepSize: 1
                }
            }
        },
        interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
        }
    };
};

// Watch for prop changes
watch([() => props.dateFrom, () => props.dateTo, () => props.dealerId, () => props.reminderTarget], () => {
    loadChartData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    setupChartOptions();
    loadChartData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <h3 class="text-lg font-semibold text-surface-900">FOLLOW UP LEADS</h3>
                <div class="flex items-center gap-2">
                    <!-- Loading indicator -->
                    <ProgressSpinner 
                        v-if="chartLoading" 
                        style="width: 20px; height: 20px" 
                        strokeWidth="4"
                    />
                </div>
            </div>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message 
                v-if="chartError && !chartLoading" 
                severity="warn" 
                :closable="false" 
                class="mb-4"
            >
                {{ chartError }}
            </Message>

            <!-- Chart Container -->
            <div class="chart-container" style="height: 400px;">
                <Chart
                    v-if="!chartLoading && chartData.labels && chartData.labels.length > 0"
                    :type="chartType"
                    :data="chartData"
                    :options="chartOptions"
                    class="w-full h-full"
                />
                
                <!-- Loading State -->
                <div v-else-if="chartLoading" class="flex flex-col items-center justify-center h-full">
                    <ProgressSpinner style="width: 50px; height: 50px" strokeWidth="4" />
                    <p class="text-muted-color text-sm mt-4">Loading chart data...</p>
                </div>
                
                <!-- Empty State -->
                <div v-else class="flex flex-col items-center justify-center h-full">
                    <i class="pi pi-chart-bar text-4xl text-muted-color mb-4"></i>
                    <p class="text-muted-color text-sm">No data available for chart</p>
                </div>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* Chart container styling */
.chart-container {
    width: 100%;
    position: relative;
}

/* Loading and empty state styling */
.flex {
    display: flex;
}

.flex-col {
    flex-direction: column;
}

.items-center {
    align-items: center;
}

.justify-center {
    justify-content: center;
}

.justify-between {
    justify-content: space-between;
}

.h-full {
    height: 100%;
}

.w-full {
    width: 100%;
}

.text-center {
    text-align: center;
}

.mb-4 {
    margin-bottom: 1rem;
}

.mt-4 {
    margin-top: 1rem;
}

.gap-2 {
    gap: 0.5rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .chart-container {
        height: 300px;
    }
    
    :deep(.p-chart) canvas {
        max-height: 300px;
    }
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
    .chart-container {
        background-color: var(--surface-card);
    }
}
</style>