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
const hloData = ref({});

// Methods
const fetchHLOData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        const response = await axios.get('/api/v1/h23-dashboard/pembayaran/hlo-statistics', {
            params: {
                dealer_id: props.dealerId,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            hloData.value = {
                total_hlo_documents: response.data.total_hlo_documents,
                total_parts: response.data.total_parts,
                total_records: response.data.total_records
            };
        } else {
            error.value = response.data.message || 'Failed to fetch HLO data';
        }
    } catch (err) {
        console.error('Error fetching HLO data:', err);
        error.value = 'Failed to fetch HLO data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        fetchHLOData();
    },
    { deep: true }
);

// Lifecycle
onMounted(() => {
    fetchHLOData();
});
</script>

<template>
    <Card class="h-full">
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- HLO Data -->
            <div v-if="!error && Object.keys(hloData).length > 0" class="py-4">
                <!-- Main Statistics Display -->
                <div class="grid grid-cols-2 gap-4 mb-4">
                    <!-- HLO Documents -->
                    <div class="text-center">
                        <div class="text-2xl md:text-3xl font-bold text-purple-600 mb-1">
                            {{ hloData.total_hlo_documents }}
                        </div>
                        <div class="text-xs text-muted-color">Documents</div>
                    </div>
                    
                    <!-- Total Parts -->
                    <div class="text-center">
                        <div class="text-2xl md:text-3xl font-bold text-indigo-600 mb-1">
                            {{ hloData.total_parts }}
                        </div>
                        <div class="text-xs text-muted-color">Parts</div>
                    </div>
                </div>
                
                <!-- Visual Element and Summary -->
                <div class="text-center">
                    <div class="inline-flex items-center justify-center w-16 h-16 bg-purple-50 rounded-full mb-3">
                        <i class="pi pi-list text-2xl text-purple-600"></i>
                    </div>
                    
                    <!-- Total Records -->
                    <div class="text-sm text-muted-color">
                        Total: {{ hloData.total_records }} HLO records
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading...</p>
            </div>

            <!-- No Data State -->
            <div v-if="!loading && !error && Object.keys(hloData).length === 0" class="text-center py-8">
                <div class="grid grid-cols-2 gap-4 mb-4">
                    <div class="text-center">
                        <div class="text-2xl md:text-3xl font-bold text-gray-400 mb-1">0</div>
                        <div class="text-xs text-muted-color">Documents</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl md:text-3xl font-bold text-gray-400 mb-1">0</div>
                        <div class="text-xs text-muted-color">Parts</div>
                    </div>
                </div>
                <div class="inline-flex items-center justify-center w-16 h-16 bg-gray-50 rounded-full mb-3">
                    <i class="pi pi-list text-2xl text-gray-400"></i>
                </div>
                <p class="text-muted-color text-sm">No HLO data available</p>
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