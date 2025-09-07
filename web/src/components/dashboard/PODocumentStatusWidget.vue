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
    },
    showTitle: {
        type: Boolean,
        default: false
    }
});

// Reactive data
const loading = ref(false);
const error = ref('');
const poStatusData = ref([]);
const totalRecords = ref(0);

// Status color mapping
const statusColorMapping = {
    'Pengajuan PO': {
        color: '#F59E0B', // Amber
        bgColor: '#FEF3C7'
    },
    'Pembuatan PO': {
        color: '#06B6D4', // Cyan
        bgColor: '#CFFAFE'
    },
    'Pengiriman PO': {
        color: '#10B981', // Green
        bgColor: '#D1FAE5'
    }
};

// Computed properties for stacked bar
const totalCount = computed(() => {
    return poStatusData.value.reduce((sum, item) => sum + item.count, 0);
});

const stackedBarData = computed(() => {
    if (totalCount.value === 0) return [];

    return poStatusData.value.map((item) => ({
        ...item,
        percentage: Math.round((item.count / totalCount.value) * 100)
    }));
});

// Methods
const fetchPOStatusData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call the PO document status API
        const response = await axios.get('/api/v1/dashboard/leasing/po-document-status', {
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
                error.value = 'No PO status data found for the selected criteria';
                poStatusData.value = [];
                return;
            }

            poStatusData.value = data.map((item) => ({
                status: item.status_label?.toUpperCase() || 'UNKNOWN',
                count: item.count,
                color: statusColorMapping[item.status_label]?.color || '#9CA3AF',
                bgColor: statusColorMapping[item.status_label]?.bgColor || '#F3F4F6',
                originalStatus: item.status_code
            }));
        } else {
            error.value = response.data.message || 'Failed to fetch PO status data';
        }
    } catch (err) {
        console.error('Error fetching PO status data:', err);
        error.value = 'Failed to fetch PO status data';

        // Use mock data as fallback for development
        const mockData = [
            {
                status: 'PENGAJUAN PO',
                count: 240,
                color: statusColorMapping['Pengajuan PO'].color,
                bgColor: statusColorMapping['Pengajuan PO'].bgColor,
                originalStatus: 1
            },
            {
                status: 'PEMBUATAN PO',
                count: 189,
                color: statusColorMapping['Pembuatan PO'].color,
                bgColor: statusColorMapping['Pembuatan PO'].bgColor,
                originalStatus: 2
            },
            {
                status: 'PENGIRIMAN PO',
                count: 73,
                color: statusColorMapping['Pengiriman PO'].color,
                bgColor: statusColorMapping['Pengiriman PO'].bgColor,
                originalStatus: 3
            }
        ];

        poStatusData.value = mockData;
        totalRecords.value = mockData.reduce((sum, item) => sum + item.count, 0);
    } finally {
        loading.value = false;
    }
};

// Force refresh method
const forceRefresh = () => {
    fetchPOStatusData();
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        fetchPOStatusData();
    },
    { deep: true }
);

// Lifecycle
onMounted(() => {
    fetchPOStatusData();
});
</script>

<template>
    <Card class="h-full">
        <template #title v-if="showTitle">
            <div class="flex items-center">
                <span class="text-lg font-bold text-gray-800 uppercase tracking-wide">PO DOCUMENT STATUS</span>
            </div>
        </template>

        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Total Records Info and Refresh Button -->
            <div v-if="totalRecords > 0" class="flex justify-between items-center mb-4">
                <!-- <button
                    @click="forceRefresh"
                    class="text-xs text-primary hover:text-primary-600 transition-colors"
                    :disabled="loading"
                    title="Refresh data"
                > -->
                <i></i>

                <!-- </button> -->
                <small class="text-muted-color"> Total Records: {{ totalRecords.toLocaleString() }} </small>
            </div>

            <!-- Stacked Bar Chart -->
            <div v-if="!error && poStatusData.length > 0" class="space-y-6">
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
                    <div v-for="(item, index) in poStatusData" :key="index" class="flex items-center justify-between py-3 px-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors duration-200">
                        <div class="flex items-center space-x-3">
                            <div class="w-4 h-4 rounded flex-shrink-0" :style="{ backgroundColor: item.color }"></div>
                            <span class="font-medium text-gray-700 text-sm uppercase tracking-wide">
                                {{ item.status }}
                            </span>
                        </div>
                        <div class="flex items-center space-x-2">
                            <span class="text-lg font-bold px-3 py-1 rounded-md text-white" :style="{ backgroundColor: item.color }">
                                {{ item.count }}
                            </span>
                        </div>
                    </div>
                </div>

                <!-- Total Summary -->
                <!-- <div class="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div class="flex justify-between items-center">
                        <span class="font-semibold text-gray-700">Total PO Documents</span>
                        <span class="text-xl font-bold text-primary">{{ totalCount.toLocaleString() }}</span>
                    </div>
                </div> -->
            </div>

            <!-- Loading State -->
            <div v-else-if="loading" class="flex justify-center items-center h-64">
                <i class="pi pi-spinner pi-spin text-2xl text-primary"></i>
            </div>

            <!-- No Data State -->
            <div v-else-if="!loading && !error && poStatusData.length === 0" class="flex flex-col items-center justify-center h-64 text-surface-500">
                <i class="pi pi-file-o text-4xl mb-4"></i>
                <p class="text-lg font-medium">No PO Status Data</p>
                <p class="text-sm">No data available for the selected period</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* Custom styles if needed */
</style>
