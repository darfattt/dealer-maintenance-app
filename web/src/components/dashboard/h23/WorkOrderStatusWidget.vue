<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
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
const loading = ref(false);
const error = ref('');
const statusData = ref([]);

// Status color mapping for consistent styling
const getStatusColor = (statusLabel) => {
    const colorMap = {
        'Start': '#10B981', // green-500
        'Pause': '#F59E0B', // amber-500
        'Pending': '#EF4444', // red-500
        'Finish': '#3B82F6', // blue-500
        'Cancel': '#6B7280', // gray-500
        'default': '#6B7280'
    };
    return colorMap[statusLabel] || colorMap['default'];
};

// Calculate maximum count for bar height scaling
const maxCount = computed(() => {
    if (statusData.value.length === 0) return 1;
    return Math.max(...statusData.value.map(item => item.count), 1);
});

// Methods
const fetchWorkOrderStatusData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        const response = await axios.get('/api/v1/h23-dashboard/work-order/status-counts', {
            params: {
                dealer_id: props.dealerId,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            statusData.value = response.data.data || [];
        } else {
            error.value = response.data.message || 'Failed to fetch work order status data';
        }
    } catch (err) {
        console.error('Error fetching work order status data:', err);
        error.value = 'Failed to fetch work order status data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        fetchWorkOrderStatusData();
    },
    { deep: true }
);

// Lifecycle
onMounted(() => {
    fetchWorkOrderStatusData();
});
</script>

<template>
    <Card class="h-full">
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Status Chart -->
            <div v-if="!error && statusData.length > 0" class="py-4">
                <!-- Chart Container -->
                <div class="flex items-end justify-center space-x-4 h-48 mb-4">
                    <div 
                        v-for="(item, index) in statusData" 
                        :key="index"
                        class="flex flex-col items-center space-y-2 flex-1 max-w-16"
                    >
                        <!-- Bar -->
                        <div class="relative w-full flex flex-col justify-end h-32">
                            <div 
                                class="w-full rounded-t-md transition-all duration-300 hover:opacity-80 relative"
                                :style="{ 
                                    backgroundColor: getStatusColor(item.status_label),
                                    height: `${(item.count / maxCount) * 100}%`,
                                    minHeight: '20px'
                                }"
                            >
                                <!-- Count Display -->
                                <div class="absolute -top-6 left-1/2 transform -translate-x-1/2 text-xs font-bold text-surface-900">
                                    {{ item.count }}
                                </div>
                            </div>
                        </div>
                        
                        <!-- Status Label -->
                        <div class="text-xs font-medium text-surface-700 text-center leading-tight">
                            {{ item.status_label }}
                        </div>
                    </div>
                </div>

                <!-- Total Count Display -->
                <div class="text-center text-sm text-muted-color">
                    Total: {{ statusData.reduce((sum, item) => sum + item.count, 0) }} work orders
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading...</p>
            </div>

            <!-- No Data State -->
            <div v-if="!loading && !error && statusData.length === 0" class="text-center py-8">
                <div class="flex items-end justify-center space-x-4 h-48 mb-4">
                    <!-- Empty bars placeholder -->
                    <div v-for="n in 5" :key="n" class="flex flex-col items-center space-y-2 flex-1 max-w-16">
                        <div class="w-full h-32 flex flex-col justify-end">
                            <div class="w-full bg-gray-200 rounded-t-md h-5"></div>
                        </div>
                        <div class="text-xs text-gray-400">--</div>
                    </div>
                </div>
                <p class="text-muted-color text-sm">No status data available</p>
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

/* Bar chart hover effects */
.hover\:opacity-80:hover {
    opacity: 0.8;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .space-x-4 > * + * {
        margin-left: 0.5rem;
    }
    
    .max-w-16 {
        max-width: 3rem;
    }
}
</style>