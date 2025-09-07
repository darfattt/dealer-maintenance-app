<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import Card from 'primevue/card';
import Message from 'primevue/message';
import Chart from 'primevue/chart';

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
const regionData = ref([]);
const chartData = ref({});
const chartOptions = ref({});

// Chart colors for different regions
const chartColors = ['#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#8B5CF6'];

// Methods
const fetchSebaranData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call real API endpoint
        const response = await axios.get('/api/v1/dashboard/prospect/sebaran-kecamatan', {
            params: {
                dealer_id: props.dealerId,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            const data = response.data.data;

            if (data.length === 0) {
                error.value = 'No sebaran prospect data found for the selected criteria';
                regionData.value = [];
                chartData.value = {};
                return;
            }

            // Calculate percentages for each region
            const totalCount = response.data.total_records;

            // Transform API response to component format
            regionData.value = data.map((item, index) => ({
                name: item.nama_kecamatan || `Kecamatan ${item.kode_kecamatan}`,
                kode_kecamatan: item.kode_kecamatan,
                count: item.count,
                percentage: Math.round((item.count / totalCount) * 100),
                color: chartColors[index % chartColors.length],
                // Use coordinates from API or generate positions for visualization
                x: item.latitude ? parseFloat(item.latitude) * 10 : (index + 1) * 15,
                y: item.longitude ? parseFloat(item.longitude) * 10 : (index + 1) * 20
            }));

            // Create scatter plot data for map-like visualization
            const scatterData = regionData.value.map((region) => ({
                x: region.x,
                y: region.y,
                r: Math.max(8, region.percentage * 1.2) // Bubble size based on percentage
            }));

            chartData.value = {
                datasets: [
                    {
                        label: 'Sebaran Prospect by Kecamatan',
                        data: scatterData,
                        backgroundColor: regionData.value.map((r) => r.color),
                        borderColor: regionData.value.map((r) => r.color),
                        borderWidth: 2
                    }
                ]
            };

            chartOptions.value = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function (context) {
                                const index = context[0].dataIndex;
                                return regionData.value[index]?.name || '';
                            },
                            label: function (context) {
                                const index = context.dataIndex;
                                const region = regionData.value[index];
                                return `${region?.count} prospects (${region?.percentage}%)`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        min: 0,
                        max: 100,
                        display: false
                    },
                    y: {
                        min: 0,
                        max: 100,
                        display: false
                    }
                }
            };
        } else {
            error.value = response.data.message || 'Failed to fetch sebaran prospect data';
        }
    } catch (err) {
        console.error('Error fetching sebaran prospect data:', err);
        error.value = 'Failed to fetch sebaran prospect data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        fetchSebaranData();
    },
    { deep: true }
);

// Lifecycle
onMounted(() => {
    fetchSebaranData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <span class="text-sm font-bold uppercase">SEBARAN DATA PROSPECT</span>
            </div>
        </template>

        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Chart and Legend Container -->
            <div v-if="!error" class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <!-- Bubble Chart (Map-like) -->
                <div class="lg:col-span-2">
                    <div class="h-64 w-full rounded-lg border border-surface-200 bg-surface-50 p-4 relative">
                        <div class="text-center mb-2">
                            <h3 class="text-sm font-semibold text-muted-color">Prospect Distribution by Kecamatan</h3>
                        </div>

                        <div v-if="Object.keys(chartData).length > 0" class="h-48">
                            <Chart type="bubble" :data="chartData" :options="chartOptions" class="h-full" />
                        </div>
                    </div>
                </div>

                <!-- Legend -->
                <div class="lg:col-span-1 flex flex-col justify-center">
                    <div class="space-y-3">
                        <div v-for="(region, index) in regionData" :key="index" class="flex items-center justify-between p-2 rounded border border-surface-200 hover:bg-surface-50 transition-colors">
                            <div class="flex items-center space-x-2">
                                <div class="w-4 h-4 rounded-full border-2 border-white shadow-sm" :style="{ backgroundColor: region.color }"></div>
                                <span class="text-xs font-medium">{{ region.name }}</span>
                            </div>
                            <div class="text-right">
                                <div class="text-xs text-muted-color mb-1">{{ region.count }} prospects</div>
                                <div class="font-bold text-sm px-2 py-1 rounded text-white" :style="{ backgroundColor: region.color }">{{ region.percentage }}%</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading distribution data...</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* Custom styling for the chart container */
:deep(.p-chart) {
    position: relative;
    height: 100%;
}
</style>
