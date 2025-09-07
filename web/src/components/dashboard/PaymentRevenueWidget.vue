<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import Card from 'primevue/card';
import Message from 'primevue/message';
import axios from 'axios';

// Props from parent
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
const totalRevenue = ref(0);

// Computed properties
const effectiveDealerId = computed(() => {
    return props.dealerId || '12284';
});

const formattedRevenue = computed(() => {
    if (!totalRevenue.value) return 'Rp 0';

    // Format number with Indonesian currency format
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(totalRevenue.value);
});

// Methods
const fetchRevenueData = async () => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        console.log('Fetching revenue data for:', {
            dealer_id: effectiveDealerId.value,
            date_from: props.dateFrom,
            date_to: props.dateTo
        });

        const response = await axios.get('/api/v1/dashboard/payment-revenue/total', {
            params: {
                dealer_id: effectiveDealerId.value,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        console.log('Revenue API response:', response.data);

        if (response.data && response.data.success) {
            totalRevenue.value = response.data.total_revenue || 0;
        } else {
            throw new Error(response.data?.message || 'Invalid response format');
        }
    } catch (err) {
        console.error('Error fetching revenue data:', err);
        if (err.response) {
            error.value = `API Error: ${err.response.data?.detail || err.response.statusText}`;
        } else if (err.request) {
            error.value = 'Network error: Unable to connect to server';
        } else {
            error.value = err.message || 'Failed to fetch revenue data';
        }
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        fetchRevenueData();
    },
    { immediate: false }
);

// Lifecycle
onMounted(() => {
    fetchRevenueData();
});
</script>

<template>
    <Card class="h-full">
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Revenue Display -->
            <div v-if="!error" class="revenue-container">
                <!-- Loading State -->
                <div v-if="loading" class="flex flex-col items-center justify-center h-48">
                    <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                    <p class="text-sm text-muted-color">Loading revenue data...</p>
                </div>

                <!-- Revenue Amount -->
                <div v-else class="flex flex-col items-center justify-center h-48 text-center">
                    <div class="revenue-amount text-4xl md:text-5xl font-bold text-surface-900 mb-2">
                        {{ formattedRevenue }}
                    </div>
                    <div class="revenue-label text-sm text-muted-color uppercase tracking-wide">Total Revenue</div>
                    <div class="revenue-period text-xs text-muted-color mt-1">{{ props.dateFrom }} to {{ props.dateTo }}</div>
                </div>
            </div>

            <!-- Empty State -->
            <div v-if="!loading && !error && totalRevenue === 0" class="text-center py-8">
                <i class="pi pi-info-circle text-2xl text-muted-color mb-2"></i>
                <p class="text-muted-color text-sm">No revenue data available</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
.revenue-container {
    width: 100%;
    height: 100%;
    min-height: 200px;
}

.revenue-amount {
    line-height: 1.1;
    word-break: break-word;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .revenue-amount {
        font-size: 2rem !important;
    }

    .revenue-container {
        min-height: 180px;
    }
}

@media (max-width: 480px) {
    .revenue-amount {
        font-size: 1.75rem !important;
    }
}

/* Animation for revenue amount */
.revenue-amount {
    transition: all 0.3s ease-in-out;
}

.revenue-amount:hover {
    transform: scale(1.02);
}
</style>
