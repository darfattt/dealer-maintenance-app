<script setup>
import { ref, onMounted, computed, watch } from 'vue';
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

// Methods
const fetchTopDriversData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Dummy data matching the image design
        const dummyData = [
            {
                id: 1,
                rank: 1,
                name: 'Muhammad Naufal',
                image: 'https://via.placeholder.com/60x60/4CAF50/FFFFFF?text=MN',
                totalDocuments: 145,
                description: '145 Dokumen'
            },
            {
                id: 2,
                rank: 2,
                name: 'Anton Rahmad',
                image: 'https://via.placeholder.com/60x60/2196F3/FFFFFF?text=AR',
                totalDocuments: 110,
                description: '110 Dokumen'
            },
            {
                id: 3,
                rank: 3,
                name: 'Valentio Nurul',
                image: 'https://via.placeholder.com/60x60/FF9800/FFFFFF?text=VN',
                totalDocuments: 90,
                description: '90 Dokumen'
            }
        ];

        topDrivers.value = dummyData;
    } catch (err) {
        console.error('Error fetching top drivers data:', err);
        error.value = 'Failed to fetch top drivers data';
    } finally {
        loading.value = false;
    }
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
