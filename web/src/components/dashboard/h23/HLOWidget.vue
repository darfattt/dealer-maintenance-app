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
        const response = await h23DashboardService.getHLOStatistics(props.dealerId, props.dateFrom, props.dateTo);

        if (response.success) {
            hloData.value = {
                total_hlo_documents: response.total_hlo_documents,
                total_parts: response.total_parts,
                total_records: response.total_records
            };
        } else {
            error.value = response.message || 'Failed to fetch HLO data';
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
                        <div class="text-3xl md:text-4xl font-bold text-purple-600 dark:text-purple-400 mb-1">
                            {{ hloData.total_hlo_documents }}
                        </div>
                        <div class="text-xs text-muted-color">Documents</div>
                    </div>
                    
                    <!-- Total Parts -->
                    <div class="text-center">
                        <div class="text-3xl md:text-4xl font-bold text-indigo-600 dark:text-indigo-400 mb-1">
                            {{ hloData.total_parts }}
                        </div>
                        <div class="text-xs text-muted-color">Parts</div>
                    </div>
                </div>
                
                <!-- Visual Element and Summary -->
                <!-- <div class="text-center">
                    <div class="inline-flex items-center justify-center w-16 h-16 bg-purple-50 rounded-full mb-3">
                        <i class="pi pi-list text-2xl text-purple-600"></i>
                    </div>
                    
                    
                    <div class="text-sm text-muted-color">
                        Total: {{ hloData.total_records }} HLO records
                    </div>
                </div> -->
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
                        <div class="text-3xl md:text-4xl font-bold text-gray-400 dark:text-gray-500 mb-1">0</div>
                        <div class="text-xs text-muted-color">Documents</div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl md:text-4xl font-bold text-gray-400 dark:text-gray-500 mb-1">0</div>
                        <div class="text-xs text-muted-color">Parts</div>
                    </div>
                </div>
                <div class="inline-flex items-center justify-center w-16 h-16 bg-gray-50 dark:bg-gray-800 rounded-full mb-3">
                    <i class="pi pi-list text-2xl text-gray-400 dark:text-gray-500"></i>
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
    .text-3xl {
        font-size: 1.75rem;
        line-height: 2.25rem;
    }
    
    .md\:text-4xl {
        font-size: 2rem;
        line-height: 2.5rem;
    }
}

/* Grid responsive adjustments */
@media (max-width: 640px) {
    .grid.grid-cols-2 {
        gap: 1rem;
    }
}
</style>