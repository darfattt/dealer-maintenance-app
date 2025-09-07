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
const prospectSources = ref([]);
const totalRecords = ref(0);

// Color mapping for different sources (top 5)
const colorMapping = [
    '#3B82F6', // Blue
    '#10B981', // Green
    '#F59E0B', // Amber
    '#EF4444', // Red
    '#8B5CF6' // Purple
];

// Methods
const fetchSumberProspectData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call the new sumber prospect top 5 API
        const response = await axios.get('/api/v1/dashboard/prospect/sumber-top5', {
            params: {
                dealer_id: props.dealerId,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            const data = response.data.data;
            totalRecords.value = response.data.total_records;

            if (data.length === 0) {
                error.value = 'No sumber prospect data found for the selected criteria';
                prospectSources.value = [];
                return;
            }

            // Calculate total count for percentage calculation
            const totalCount = data.reduce((sum, item) => sum + item.count, 0);

            // Transform API response to component format
            prospectSources.value = data.map((item, index) => {
                const sumberLabel = item.sumber_label || item.sumber_prospect || 'Unknown';
                const percentage = totalCount > 0 ? ((item.count / totalCount) * 100).toFixed(1) : 0;

                return {
                    source: sumberLabel,
                    count: item.count,
                    percentage: parseFloat(percentage),
                    color: colorMapping[index % colorMapping.length]
                };
            });

            // Data is already sorted by count descending from API (top 5)
        } else {
            error.value = response.data.message || 'Failed to fetch sumber prospect data';
        }
    } catch (err) {
        console.error('Error fetching sumber prospect data:', err);
        error.value = 'Failed to fetch sumber prospect data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        fetchSumberProspectData();
    },
    { deep: true }
);

// Lifecycle
onMounted(() => {
    fetchSumberProspectData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <span class="text-sm font-bold uppercase">TOP 5 SUMBER PROSPECT</span>
                <small v-if="totalRecords > 0" class="text-muted-color"> Total Records: {{ totalRecords }} </small>
            </div>
        </template>

        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Prospect Sources List -->
            <div v-if="!error && prospectSources.length > 0" class="space-y-3">
                <div v-for="(source, index) in prospectSources" :key="index" class="flex items-center justify-between p-3 rounded-lg border border-surface-200 hover:bg-surface-50 transition-colors">
                    <div class="flex items-center space-x-3">
                        <div class="w-4 h-4 rounded-full" :style="{ backgroundColor: source.color }"></div>
                        <span class="font-medium text-sm">{{ source.source }}</span>
                    </div>
                    <div class="text-right">
                        <div class="flex flex-col items-end space-y-1">
                            <div class="font-bold text-lg px-3 py-1 rounded-full text-white" :style="{ backgroundColor: source.color }">{{ source.percentage }}%</div>
                            <small class="text-muted-color text-xs"> {{ source.count }} records </small>
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
                <p class="text-muted-color text-sm">No sumber prospect data available</p>
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
