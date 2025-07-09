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
const locationData = ref([]);

// Computed properties
const effectiveDealerId = computed(() => {
    return props.dealerId || '12284';
});

// Methods
const fetchLocationData = async () => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call real API endpoint
        const response = await axios.get('/api/v1/dashboard/delivery/locations', {
            params: {
                dealer_id: effectiveDealerId.value,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            const data = response.data.data;
            
            if (data.length === 0) {
                error.value = 'No delivery location data found for the selected criteria';
                locationData.value = [];
                return;
            }

            // Transform API response to component format with colors
            const colors = ['#4CAF50', '#F44336', '#FF9800', '#2196F3', '#9C27B0'];
            
            locationData.value = data.map((item, index) => ({
                id: index + 1,
                name: item.location_name || item.lokasi_pengiriman,
                percentage: item.percentage,
                delivery_count: item.delivery_count,
                color: colors[index] || '#9E9E9E'
            }));
            
        } else {
            error.value = response.data.message || 'Failed to fetch delivery location data';
        }
    } catch (err) {
        console.error('Error fetching location data:', err);
        error.value = 'Failed to fetch location data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchLocationData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchLocationData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <span class="text-lg font-semibold text-surface-900">LOKASI PENGIRIMAN</span>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Location Data -->
            <div v-if="!error && locationData.length > 0" class="space-y-4">
                <!-- Map Placeholder -->
                <div class="relative bg-surface-100 rounded-lg p-4 mb-6" style="height: 200px;">
                    <!-- Simple Indonesia Map Representation -->
                    <div class="absolute inset-0 flex items-center justify-center">
                        <div class="relative">
                            <!-- Map placeholder with dots representing locations -->
                            <svg width="200" height="120" viewBox="0 0 200 120" class="text-surface-400">
                                <!-- Simple Indonesia outline -->
                                <path d="M20,60 Q40,40 80,45 Q120,50 160,55 Q180,60 170,80 Q150,90 100,85 Q60,80 20,60 Z" 
                                      fill="currentColor" opacity="0.3"/>
                                <!-- Location dots -->
                                <circle cx="60" cy="65" r="3" :fill="locationData[0]?.color || '#4CAF50'"/>
                                <circle cx="90" cy="55" r="3" :fill="locationData[1]?.color || '#F44336'"/>
                                <circle cx="120" cy="70" r="3" :fill="locationData[2]?.color || '#FF9800'"/>
                                <circle cx="140" cy="60" r="3" :fill="locationData[3]?.color || '#2196F3'"/>
                            </svg>
                        </div>
                    </div>
                </div>

                <!-- Location Statistics -->
                <div class="space-y-3">
                    <div
                        v-for="location in locationData"
                        :key="location.id"
                        class="flex items-center justify-between p-2 rounded border border-surface-200"
                    >
                        <div class="flex items-center space-x-3">
                            <div
                                class="w-3 h-3 rounded-full"
                                :style="{ backgroundColor: location.color }"
                            ></div>
                            <span class="text-sm font-medium text-surface-900">{{ location.name }}</span>
                        </div>
                        <div class="text-right">
                            <span 
                                class="font-bold text-sm"
                                :style="{ color: location.color }"
                            >
                                {{ location.percentage }}%
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading location data...</p>
            </div>

            <!-- Empty State -->
            <div v-if="!loading && !error && locationData.length === 0" class="text-center py-8">
                <i class="pi pi-info-circle text-2xl text-muted-color mb-2"></i>
                <p class="text-muted-color text-sm">No location data available</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* Custom styles for the widget */
.space-y-4 > * + * {
    margin-top: 1rem;
}

.space-y-3 > * + * {
    margin-top: 0.75rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .relative[style*="height: 200px"] {
        height: 150px !important;
    }
    
    svg {
        width: 150px;
        height: 90px;
    }
}
</style>
