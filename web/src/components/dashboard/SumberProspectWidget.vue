<script setup>
import { ref, onMounted, watch } from 'vue';
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
const prospectSources = ref([]);
const totalRecords = ref(0);

// Methods
const fetchSumberProspectData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Dummy data matching the image
        const dummyData = [
            { source: 'Walk In', percentage: 65, color: '#22D3EE' },
            { source: 'Website', percentage: 15, color: '#22D3EE' },
            { source: 'Customer RO H1', percentage: 5, color: '#22D3EE' },
            { source: 'Customer RO H23', percentage: 5, color: '#22D3EE' },
            { source: 'Showroom Event', percentage: 3, color: '#22D3EE' },
            { source: 'Others', percentage: 2.5, color: '#22D3EE' }
        ];

        prospectSources.value = dummyData;
        totalRecords.value = dummyData.reduce((sum, item) => sum + item.percentage, 0);

    } catch (err) {
        console.error('Error fetching prospect sources:', err);
        error.value = 'Failed to fetch prospect sources data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchSumberProspectData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchSumberProspectData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <span class="text-sm font-bold uppercase">SUMBER PROSPECT</span>
                <small v-if="totalRecords > 0" class="text-muted-color">
                    Total: {{ totalRecords.toFixed(1) }}%
                </small>
            </div>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Prospect Sources List -->
            <div v-if="!error && prospectSources.length > 0" class="space-y-3">
                <div
                    v-for="(source, index) in prospectSources"
                    :key="index"
                    class="flex items-center justify-between p-3 rounded-lg border border-surface-200 hover:bg-surface-50 transition-colors"
                >
                    <div class="flex items-center space-x-3">
                        <div
                            class="w-4 h-4 rounded-full"
                            :style="{ backgroundColor: source.color }"
                        ></div>
                        <span class="font-medium text-sm">{{ source.source }}</span>
                    </div>
                    <div class="text-right">
                        <div 
                            class="font-bold text-lg px-3 py-1 rounded-full text-white"
                            :style="{ backgroundColor: source.color }"
                        >
                            {{ source.percentage }}%
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading...</p>
            </div>

            <!-- Empty State -->
            <div v-if="!loading && !error && prospectSources.length === 0" class="text-center py-8">
                <i class="pi pi-chart-bar text-4xl text-muted-color mb-2"></i>
                <p class="text-muted-color text-sm">No prospect source data available</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* Additional styling for better visual hierarchy */
.prospect-source-item {
    transition: all 0.2s ease-in-out;
}

.prospect-source-item:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
