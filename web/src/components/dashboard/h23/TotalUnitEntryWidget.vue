<script setup>
import { ref, onMounted, watch } from 'vue';
import Card from 'primevue/card';
import Message from 'primevue/message';
import h23DashboardService from '@/service/H23DashboardService';

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
const unitEntryData = ref({});

// Methods
const fetchTotalUnitEntryData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        const response = await h23DashboardService.getTotalUnitEntry(props.dealerId, props.dateFrom, props.dateTo);

        if (response.success) {
            unitEntryData.value = {
                count: response.count,
                previous_count: response.previous_count,
                trend: response.trend,
                percentage: response.percentage
            };
        } else {
            error.value = response.message || 'Failed to fetch total unit entry data';
        }
    } catch (err) {
        console.error('Error fetching total unit entry data:', err);
        error.value = 'Failed to fetch total unit entry data';
    } finally {
        loading.value = false;
    }
};

// Get trend icon based on trend direction
const getTrendIcon = (trend) => {
    switch (trend) {
        case 'up': return 'pi pi-arrow-up';
        case 'down': return 'pi pi-arrow-down';
        default: return 'pi pi-minus';
    }
};

// Get trend color based on trend direction
const getTrendColor = (trend) => {
    switch (trend) {
        case 'up': return '#10B981'; // green-500
        case 'down': return '#EF4444'; // red-500
        default: return '#6B7280'; // gray-500
    }
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        fetchTotalUnitEntryData();
    },
    { deep: true }
);

// Lifecycle
onMounted(() => {
    fetchTotalUnitEntryData();
});
</script>

<template>
    <Card class="h-full">
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Unit Entry Data -->
            <div v-if="!error && Object.keys(unitEntryData).length > 0" class="text-center py-6">
                <div class="relative inline-block mb-4">
                    <div
                        class="text-6xl font-bold rounded-full w-32 h-32 flex items-center justify-center mx-auto bg-blue-50 dark:bg-blue-400/10 text-blue-600 dark:text-blue-400"
                    >
                        {{ unitEntryData.count }}
                    </div>
                    <!-- Trend Indicator -->
                    <div 
                        v-if="unitEntryData.trend !== 'stable'" 
                        class="absolute -bottom-2 -right-2 rounded-full p-2 text-white text-xs"
                        :style="{ backgroundColor: getTrendColor(unitEntryData.trend) }"
                    >
                        <i :class="getTrendIcon(unitEntryData.trend)"></i>
                    </div>
                </div>
                
                <!-- Trend Information -->
                <div class="text-sm text-muted-color">
                    <div v-if="unitEntryData.trend !== 'stable'" class="flex items-center justify-center space-x-2">
                        <span :class="{ 
                            'text-green-600 dark:text-green-400': unitEntryData.trend === 'up', 
                            'text-red-600 dark:text-red-400': unitEntryData.trend === 'down' 
                        }">
                            <i :class="getTrendIcon(unitEntryData.trend)" class="mr-1"></i>
                            {{ unitEntryData.percentage.toFixed(1) }}%
                        </span>
                        <span>from previous month</span>
                    </div>
                    <div v-else>
                        No change from previous month
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading...</p>
            </div>

            <!-- No Data State -->
            <div v-if="!loading && !error && Object.keys(unitEntryData).length === 0" class="text-center py-6">
                <div class="text-6xl font-bold rounded-full w-32 h-32 flex items-center justify-center mx-auto bg-gray-50 dark:bg-gray-800 text-gray-400 dark:text-gray-500 mb-4">
                    0
                </div>
                <p class="text-muted-color text-sm">No data available</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* Additional custom styles if needed */
.p-card {
    height: 100%;
}

.p-card :deep(.p-card-content) {
    padding: 1.5rem;
}
</style>