<script setup>
import { ref, onMounted, watch } from 'vue';
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

// West Java regions data
const westJavaRegions = [
    { name: 'Arcamanik', percentage: 30, color: '#10B981', x: 60, y: 30 },
    { name: 'Astanaanyar', percentage: 15, color: '#F59E0B', x: 20, y: 40 },
    { name: 'Bandung Kidul', percentage: 3, color: '#EF4444', x: 50, y: 70 },
    { name: 'Andir', percentage: 5, color: '#3B82F6', x: 80, y: 50 },
    { name: 'Others', percentage: 2, color: '#6B7280', x: 40, y: 60 }
];

// Methods
const fetchSebaranData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Use the West Java regions data
        regionData.value = westJavaRegions;
        
        // Create scatter plot data for map-like visualization
        const scatterData = regionData.value.map(region => ({
            x: region.x,
            y: region.y,
            r: Math.max(5, region.percentage * 0.8) // Bubble size based on percentage
        }));

        chartData.value = {
            datasets: [{
                label: 'West Java Regions',
                data: scatterData,
                backgroundColor: regionData.value.map(r => r.color),
                borderColor: regionData.value.map(r => r.color),
                borderWidth: 2
            }]
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
                        title: function(context) {
                            const index = context[0].dataIndex;
                            return regionData.value[index]?.name || '';
                        },
                        label: function(context) {
                            const index = context.dataIndex;
                            const region = regionData.value[index];
                            return `${region?.percentage}% of prospects`;
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
    } catch (err) {
        console.error('Error fetching sebaran data:', err);
        error.value = 'Failed to fetch distribution data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchSebaranData();
}, { deep: true });

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
                            <h3 class="text-sm font-semibold text-muted-color">West Java Region</h3>
                        </div>
                        
                        <div v-if="Object.keys(chartData).length > 0" class="h-48">
                            <Chart
                                type="bubble"
                                :data="chartData"
                                :options="chartOptions"
                                class="h-full"
                            />
                        </div>
                    </div>
                </div>

                <!-- Legend -->
                <div class="lg:col-span-1 flex flex-col justify-center">
                    <div class="space-y-3">
                        <div
                            v-for="(region, index) in regionData"
                            :key="index"
                            class="flex items-center justify-between p-2 rounded border border-surface-200 hover:bg-surface-50 transition-colors"
                        >
                            <div class="flex items-center space-x-2">
                                <div
                                    class="w-4 h-4 rounded-full border-2 border-white shadow-sm"
                                    :style="{ backgroundColor: region.color }"
                                ></div>
                                <span class="text-xs font-medium">{{ region.name }}</span>
                            </div>
                            <div class="text-right">
                                <div 
                                    class="font-bold text-sm px-2 py-1 rounded text-white"
                                    :style="{ backgroundColor: region.color }"
                                >
                                    {{ region.percentage }}%
                                </div>
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
