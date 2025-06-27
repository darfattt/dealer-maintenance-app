<script setup>
import { ref, onMounted, watch, computed } from 'vue';
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
    },
    showTitle: {
        type: Boolean,
        default: false
    }
});

// Reactive data
const loading = ref(false);
const error = ref('');
const deliveryData = ref([]);

// Computed properties for stacked bar
const totalCount = computed(() => {
    return deliveryData.value.reduce((sum, item) => sum + item.count, 0);
});

const stackedBarData = computed(() => {
    if (totalCount.value === 0) return [];

    return deliveryData.value.map(item => ({
        ...item,
        percentage: ((item.count / totalCount.value) * 100).toFixed(1)
    }));
});

// Methods
const fetchDeliveryProcessData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Dummy data for now - matching the design colors
        deliveryData.value = [
            {
                status: 'READY',
                count: 72,
                color: '#FCD34D', // Yellow
                bgColor: '#FEF3C7'
            },
            {
                status: 'IN PROGRESS',
                count: 143,
                color: '#22D3EE', // Cyan
                bgColor: '#CFFAFE'
            },
            {
                status: 'BACK TO DEALER',
                count: 53,
                color: '#D1D5DB', // Gray
                bgColor: '#F3F4F6'
            },
            {
                status: 'COMPLETED',
                count: 213,
                color: '#10B981', // Green
                bgColor: '#D1FAE5'
            }
        ];
    } catch (err) {
        console.error('Error fetching delivery process data:', err);
        error.value = 'Failed to fetch delivery process data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchDeliveryProcessData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchDeliveryProcessData();
});
</script>

<template>
    <Card class="h-full">
        <template #title v-if="showTitle">
            <div class="flex items-center">
                <span class="text-lg font-bold text-gray-800 uppercase tracking-wide">DELIVERY PROCESS</span>
            </div>
        </template>

        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Stacked Bar Chart -->
            <div v-if="!error && deliveryData.length > 0" class="space-y-6">
                <!-- Horizontal Stacked Bar -->
                <div class="w-full">
                    <div class="flex h-8 rounded-lg overflow-hidden shadow-sm border border-gray-200">
                        <div
                            v-for="(item, index) in stackedBarData"
                            :key="index"
                            class="flex items-center justify-center text-xs font-medium text-white transition-all duration-300 hover:opacity-80"
                            :style="{
                                backgroundColor: item.color,
                                width: item.percentage + '%',
                                minWidth: item.percentage > 5 ? 'auto' : '0'
                            }"
                            :title="`${item.status}: ${item.count} (${item.percentage}%)`"
                        >
                            <span v-if="item.percentage > 8" class="text-xs font-semibold">
                                {{ item.count }}
                            </span>
                        </div>
                    </div>
                </div>

                <!-- Legend Below -->
                <div class="grid grid-cols-1 gap-3">
                    <div
                        v-for="(item, index) in deliveryData"
                        :key="index"
                        class="flex items-center justify-between py-3 px-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors duration-200"
                    >
                        <div class="flex items-center space-x-3">
                            <div
                                class="w-4 h-4 rounded flex-shrink-0"
                                :style="{ backgroundColor: item.color }"
                            ></div>
                            <span class="font-medium text-gray-700 text-sm uppercase tracking-wide">
                                {{ item.status }}
                            </span>
                        </div>
                        <div class="flex items-center space-x-2">
                            <span
                                class="text-lg font-bold px-3 py-1 rounded-md text-white"
                                :style="{ backgroundColor: item.color }"
                            >
                                {{ item.count }}
                            </span>
                        </div>
                    </div>
                </div>

                <!-- Total Summary -->
                <div class="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div class="flex justify-between items-center">
                        <span class="font-semibold text-gray-700">Total Deliveries</span>
                        <span class="font-bold text-xl text-gray-800">{{ totalCount }}</span>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-4xl text-primary mb-4"></i>
                <p class="text-muted-color">Loading delivery process data...</p>
            </div>

            <!-- No Data State -->
            <div v-else-if="!loading && !error && deliveryData.length === 0" class="text-center py-8">
                <i class="pi pi-chart-bar text-4xl text-muted-color mb-4"></i>
                <p class="text-muted-color">No delivery process data available</p>
            </div>
        </template>
    </Card>
</template>
