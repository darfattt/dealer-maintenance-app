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
const topDealingData = ref([]);

// Computed properties
const effectiveDealerId = computed(() => {
    return props.dealerId || '12284';
});

// Methods
const fetchTopDealingData = async () => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call real API endpoint
        const response = await axios.get('/api/v1/dashboard/dealing/top-units', {
            params: {
                dealer_id: effectiveDealerId.value,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            const data = response.data.data;
            
            if (data.length === 0) {
                error.value = 'No top dealing units data found for the selected criteria';
                topDealingData.value = [];
                return;
            }

            // Transform API response to component format
            topDealingData.value = data.map((item, index) => ({
                id: index + 1,
                name: item.nama_unit || item.kode_tipe_unit,
                kode_tipe_unit: item.kode_tipe_unit,
                totalData: item.total_quantity,
                brand: 'Honda', // Default brand
                image: getUnitImage(item.kode_tipe_unit)
            }));
            
        } else {
            error.value = response.data.message || 'Failed to fetch top dealing units data';
        }
    } catch (err) {
        console.error('Error fetching top dealing data:', err);
        error.value = 'Failed to fetch top dealing data';
    } finally {
        loading.value = false;
    }
};

// Helper function to get unit image based on type
const getUnitImage = (kodeUnit) => {
    const unitImages = {
        'SCOOPY': 'https://via.placeholder.com/80x60/4CAF50/FFFFFF?text=SCOOPY',
        'VARIO': 'https://via.placeholder.com/80x60/2196F3/FFFFFF?text=VARIO', 
        'BEAT': 'https://via.placeholder.com/80x60/FF9800/FFFFFF?text=BEAT',
        'PCX': 'https://via.placeholder.com/80x60/9C27B0/FFFFFF?text=PCX',
        'GENIO': 'https://via.placeholder.com/80x60/00BCD4/FFFFFF?text=GENIO',
        'CB150R': 'https://via.placeholder.com/80x60/FF5722/FFFFFF?text=CB150R',
        'CBR150R': 'https://via.placeholder.com/80x60/F44336/FFFFFF?text=CBR150R',
        'CRF150L': 'https://via.placeholder.com/80x60/795548/FFFFFF?text=CRF150L',
        'FORZA': 'https://via.placeholder.com/80x60/607D8B/FFFFFF?text=FORZA',
        'ADV': 'https://via.placeholder.com/80x60/3F51B5/FFFFFF?text=ADV'
    };
    
    return unitImages[kodeUnit] || 'https://via.placeholder.com/80x60/cccccc/666666?text=Motor';
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchTopDealingData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchTopDealingData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <span>Top Dealing</span>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Top Dealing Items -->
            <div v-if="!error && topDealingData.length > 0" class="space-y-4">
                <div
                    v-for="item in topDealingData"
                    :key="item.id"
                    class="flex items-center space-x-4 p-3 rounded-lg border border-surface-200 hover:bg-surface-50 transition-colors"
                >
                    <!-- Motorcycle Image -->
                    <div class="flex-shrink-0">
                        <img
                            :src="item.image"
                            :alt="item.name"
                            class="w-20 h-16 object-contain rounded"
                            @error="$event.target.src = 'https://via.placeholder.com/80x60/cccccc/666666?text=Motor'"
                        />
                    </div>

                    <!-- Details -->
                    <div class="flex-grow min-w-0">
                        <h4 class="font-bold text-lg text-surface-900 truncate">{{ item.name }}</h4>
                        <p class="text-sm text-surface-600 font-medium">{{ item.totalData }} units</p>
                        <p class="text-xs text-surface-500">{{ item.kode_tipe_unit }}</p>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading...</p>
            </div>

            <!-- Empty State -->
            <div v-if="!loading && !error && topDealingData.length === 0" class="text-center py-8">
                <i class="pi pi-info-circle text-2xl text-muted-color mb-2"></i>
                <p class="text-muted-color text-sm">No dealing units data available</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* Custom styles for the widget */
.space-y-4 > * + * {
    margin-top: 1rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .flex-shrink-0 img {
        width: 3.5rem;
        height: 2.5rem;
    }

    .font-bold {
        font-size: 1rem;
    }
}
</style>
