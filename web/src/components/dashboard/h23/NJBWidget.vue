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
const njbData = ref({});

// Method to format currency to IDR
const formatCurrency = (amount) => {
    if (amount === null || amount === undefined || amount === 0) {
        return 'Rp 0';
    }
    
    // Convert to number and format with thousands separators
    const formatted = new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
    
    return formatted;
};

// Methods
const fetchNJBData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        const response = await h23DashboardService.getNJBStatistics(props.dealerId, props.dateFrom, props.dateTo);

        if (response.success) {
            njbData.value = {
                total_amount: response.total_amount,
                total_records: response.total_records
            };
        } else {
            error.value = response.message || 'Failed to fetch NJB data';
        }
    } catch (err) {
        console.error('Error fetching NJB data:', err);
        error.value = 'Failed to fetch NJB data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        fetchNJBData();
    },
    { deep: true }
);

// Lifecycle
onMounted(() => {
    fetchNJBData();
});
</script>

<template>
    <Card class="h-full">
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- NJB Data -->
            <div v-if="!error && Object.keys(njbData).length > 0" class="py-4">
                <!-- Main Statistics Display -->
                <div class="grid grid-cols-2 gap-4 mb-4">
                    <!-- Amount -->
                    <div class="text-center">
                        <div class="text-2xl md:text-3xl font-bold text-blue-600 dark:text-blue-400 mb-1">
                            {{ formatCurrency(njbData.total_amount) }}
                        </div>
                        <div class="text-xs text-muted-color">Amount</div>
                    </div>
                    
                    <!-- Total Records -->
                    <div class="text-center">
                        <div class="text-2xl md:text-3xl font-bold text-indigo-600 dark:text-indigo-400 mb-1">
                            {{ njbData.total_records }}
                        </div>
                        <div class="text-xs text-muted-color">Records</div>
                    </div>
                </div>
                
                <!-- Visual Element and Summary -->
                <!-- <div class="text-center">
                    <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-50 rounded-full mb-3">
                        <i class="pi pi-file-edit text-2xl text-blue-600"></i>
                    </div>
                    
                    <div class="text-sm text-muted-color">
                        Total: {{ njbData.total_records }} NJB records
                    </div>
                </div> -->
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading...</p>
            </div>

            <!-- No Data State -->
            <div v-if="!loading && !error && Object.keys(njbData).length === 0" class="text-center py-8">
                <div class="grid grid-cols-2 gap-4 mb-4">
                    <div class="text-center">
                        <div class="text-2xl md:text-3xl font-bold text-gray-400 dark:text-gray-500 mb-1">Rp 0</div>
                        <div class="text-xs text-muted-color">Amount</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl md:text-3xl font-bold text-gray-400 dark:text-gray-500 mb-1">0</div>
                        <div class="text-xs text-muted-color">Records</div>
                    </div>
                </div>
                <div class="inline-flex items-center justify-center w-16 h-16 bg-gray-50 dark:bg-gray-800 rounded-full mb-3">
                    <i class="pi pi-file-edit text-2xl text-gray-400 dark:text-gray-500"></i>
                </div>
                <p class="text-muted-color text-sm">No NJB data available</p>
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

/* Responsive font sizes */
@media (max-width: 768px) {
    .text-2xl {
        font-size: 1.5rem;
        line-height: 2rem;
    }
    
    .md\:text-3xl {
        font-size: 1.75rem;
        line-height: 2.25rem;
    }
}

/* Grid responsive adjustments */
@media (max-width: 640px) {
    .grid.grid-cols-2 {
        gap: 1rem;
    }
}
</style>