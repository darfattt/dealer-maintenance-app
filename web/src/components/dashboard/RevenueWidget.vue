<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import axios from 'axios';
import Card from 'primevue/card';
import Message from 'primevue/message';

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
    if (totalRevenue.value === 0) return 'Rp 0';
    
    // Format number with Indonesian currency format
    const formatter = new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
    
    return formatter.format(totalRevenue.value);
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
        // Call real API endpoint
        const response = await axios.get('/api/v1/dashboard/revenue', {
            params: {
                dealer_id: effectiveDealerId.value,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            totalRevenue.value = response.data.total_revenue || 0;
            
            if (totalRevenue.value === 0) {
                error.value = 'No revenue data found for the selected criteria';
            }
        } else {
            error.value = response.data.message || 'Failed to fetch revenue data';
        }
    } catch (err) {
        console.error('Error fetching revenue data:', err);
        error.value = 'Failed to fetch revenue data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchRevenueData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchRevenueData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <span class="text-lg font-semibold text-surface-700">REVENUE</span>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Revenue Display -->
            <div v-if="!error" class="flex items-center justify-center h-full min-h-[120px]">
                <div class="text-center">
                    <div class="text-4xl md:text-5xl lg:text-6xl font-bold text-surface-900 mb-2">
                        {{ formattedRevenue }}
                    </div>
                    <div class="text-sm text-surface-600 font-medium">
                        Total Revenue
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading revenue...</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* Custom styles for the revenue widget */
.min-h-[120px] {
    min-height: 120px;
}

/* Responsive font sizing */
@media (max-width: 1024px) {
    .text-4xl.md\:text-5xl.lg\:text-6xl {
        font-size: 2.5rem;
    }
}

@media (max-width: 768px) {
    .text-4xl.md\:text-5xl.lg\:text-6xl {
        font-size: 2rem;
    }
}

@media (max-width: 640px) {
    .text-4xl.md\:text-5xl.lg\:text-6xl {
        font-size: 1.75rem;
    }
}

/* Ensure the card content is centered */
:deep(.p-card-content) {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 120px;
}
</style>
