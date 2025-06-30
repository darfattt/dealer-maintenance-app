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
const topDrivers = ref([]);

// Computed properties
const effectiveDealerId = computed(() => {
    return props.dealerId || '12284';
});

// Methods
const fetchTopDriversData = async () => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call real API endpoint
        const response = await axios.get('/api/v1/dashboard/delivery/top-drivers', {
            params: {
                dealer_id: effectiveDealerId.value,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            const data = response.data.data;
            
            if (data.length === 0) {
                error.value = 'No top driver data found for the selected criteria';
                topDrivers.value = [];
                return;
            }

            // Transform API response to component format
            topDrivers.value = data.map((item, index) => ({
                id: index + 1,
                rank: index + 1,
                name: item.nama_driver || item.id_driver,
                id_driver: item.id_driver,
                image: getDriverImage(item.id_driver),
                totalDocuments: item.total_deliveries,
                description: `${item.total_deliveries} Deliveries`
            }));
            
        } else {
            error.value = response.data.message || 'Failed to fetch top driver data';
        }
    } catch (err) {
        console.error('Error fetching top drivers data:', err);
        error.value = 'Failed to fetch top drivers data';
    } finally {
        loading.value = false;
    }
};

// Helper function to get driver image based on driver ID
const getDriverImage = (idDriver) => {
    const colors = ['4CAF50', '2196F3', 'FF9800', '9C27B0', '00BCD4'];
    const colorIndex = Math.abs(idDriver ? idDriver.hashCode() : 0) % colors.length;
    const color = colors[colorIndex];
    const initials = idDriver ? idDriver.substring(0, 2).toUpperCase() : 'DR';
    
    return `https://via.placeholder.com/60x60/${color}/FFFFFF?text=${initials}`;
};

// String hash function for consistent color assignment
String.prototype.hashCode = function() {
    let hash = 0;
    for (let i = 0; i < this.length; i++) {
        const char = this.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchTopDriversData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchTopDriversData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <span class="text-lg font-semibold text-surface-900">DRIVER</span>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Top Drivers List -->
            <div v-if="!error && topDrivers.length > 0" class="space-y-4">
                <div
                    v-for="driver in topDrivers"
                    :key="driver.id"
                    class="flex items-center space-x-4 p-3 rounded-lg border border-surface-200 hover:bg-surface-50 transition-colors"
                >
                    <!-- Rank Number -->
                    <div class="flex-shrink-0 w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-bold text-sm">
                        {{ driver.rank }}
                    </div>

                    <!-- Driver Image -->
                    <div class="flex-shrink-0">
                        <img
                            :src="driver.image"
                            :alt="driver.name"
                            class="w-12 h-12 object-cover rounded-full border-2 border-surface-200"
                            @error="$event.target.src = 'https://via.placeholder.com/48x48/cccccc/666666?text=D'"
                        />
                    </div>

                    <!-- Driver Details -->
                    <div class="flex-grow min-w-0">
                        <h4 class="font-bold text-base text-surface-900 truncate">{{ driver.name }}</h4>
                        <p class="text-sm text-surface-600">{{ driver.description }}</p>
                        <p class="text-xs text-surface-500">{{ driver.id_driver }}</p>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading drivers...</p>
            </div>

            <!-- Empty State -->
            <div v-if="!loading && !error && topDrivers.length === 0" class="text-center py-8">
                <i class="pi pi-info-circle text-2xl text-muted-color mb-2"></i>
                <p class="text-muted-color text-sm">No driver data available</p>
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
        width: 2.5rem;
        height: 2.5rem;
    }
    
    .font-bold {
        font-size: 0.875rem;
    }
    
    .text-sm {
        font-size: 0.75rem;
    }
}
</style>
