<script setup>
import { ref, onMounted, watch } from 'vue';
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
        const response = await axios.get('/api/v1/h23-dashboard/pembayaran/njb-statistics', {
            params: {
                dealer_id: props.dealerId,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            njbData.value = {
                total_amount: response.data.total_amount,
                total_records: response.data.total_records
            };
        } else {
            error.value = response.data.message || 'Failed to fetch NJB data';
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
            <div v-if="!error && Object.keys(njbData).length > 0" class="text-center py-6">
                <!-- Main Amount Display -->
                <div class="mb-4">
                    <div class="text-3xl md:text-4xl font-bold text-blue-600 leading-tight mb-2">
                        {{ formatCurrency(njbData.total_amount) }}
                    </div>
                </div>
                
                <!-- Records Information -->
                <div class="text-sm text-muted-color">
                    <span>{{ njbData.total_records }} NJB records</span>
                </div>
                
                <!-- Visual Element - icon or graphic representation -->
                <div class="mt-4">
                    <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-50 rounded-full">
                        <i class="pi pi-file-edit text-2xl text-blue-600"></i>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading...</p>
            </div>

            <!-- No Data State -->
            <div v-if="!loading && !error && Object.keys(njbData).length === 0" class="text-center py-8">
                <div class="text-3xl md:text-4xl font-bold text-gray-400 leading-tight mb-2">
                    Rp 0
                </div>
                <p class="text-muted-color text-sm">No NJB data available</p>
                <div class="mt-4">
                    <div class="inline-flex items-center justify-center w-16 h-16 bg-gray-50 rounded-full">
                        <i class="pi pi-file-edit text-2xl text-gray-400"></i>
                    </div>
                </div>
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
    .text-3xl {
        font-size: 1.75rem;
        line-height: 2.25rem;
    }
    
    .md\:text-4xl {
        font-size: 2rem;
        line-height: 2.5rem;
    }
}
</style>