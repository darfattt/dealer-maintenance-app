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
const revenueData = ref({});

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
const fetchWorkOrderRevenueData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        const response = await h23DashboardService.getWorkOrderRevenue(props.dealerId, props.dateFrom, props.dateTo);

        if (response.success) {
            revenueData.value = {
                total_revenue: response.total_revenue,
                total_records: response.total_records
            };
        } else {
            error.value = response.message || 'Failed to fetch work order revenue data';
        }
    } catch (err) {
        console.error('Error fetching work order revenue data:', err);
        error.value = 'Failed to fetch work order revenue data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        fetchWorkOrderRevenueData();
    },
    { deep: true }
);

// Lifecycle
onMounted(() => {
    fetchWorkOrderRevenueData();
});
</script>

<template>
    <Card class="h-full">
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Revenue Data -->
            <div v-if="!error && Object.keys(revenueData).length > 0" class="text-center py-6">
                <div class="mb-4">
                    <div class="text-4xl md:text-5xl font-bold text-green-600 dark:text-green-400 leading-tight">
                        {{ formatCurrency(revenueData.total_revenue) }}
                    </div>
                </div>
                
                <!-- Records Information -->
                <div class="text-sm text-muted-color">
                    <span>{{ revenueData.total_records }} work orders</span>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading...</p>
            </div>

            <!-- No Data State -->
            <div v-if="!loading && !error && Object.keys(revenueData).length === 0" class="text-center py-6">
                <div class="mb-4">
                    <div class="text-4xl md:text-5xl font-bold text-gray-400 dark:text-gray-500 leading-tight">
                        Rp 0
                    </div>
                </div>
                <p class="text-muted-color text-sm">No revenue data available</p>
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
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Responsive font sizes */
@media (max-width: 768px) {
    .text-4xl {
        font-size: 2rem;
        line-height: 2.5rem;
    }
    
    .md\:text-5xl {
        font-size: 2.25rem;
        line-height: 2.75rem;
    }
}
</style>