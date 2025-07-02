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
const topUnits = ref([]);

// Computed properties
const effectiveDealerId = computed(() => {
    return props.dealerId || '12284';
});

// Mock data for demonstration (will be replaced with real API later)
const mockTopUnitsData = [
    {
        id: 1,
        unit_name: 'Scoopy Black',
        unit_image: 'https://via.placeholder.com/48x48/000000/ffffff?text=SB',
        total_units: 341
    },
    {
        id: 2,
        unit_name: 'Vario 160 Navy',
        unit_image: 'https://via.placeholder.com/48x48/000080/ffffff?text=VN',
        total_units: 210
    },
    {
        id: 3,
        unit_name: 'Beat Cream',
        unit_image: 'https://via.placeholder.com/48x48/F5F5DC/000000?text=BC',
        total_units: 100
    },
    {
        id: 4,
        unit_name: 'Beat Cream',
        unit_image: 'https://via.placeholder.com/48x48/F5F5DC/000000?text=BC',
        total_units: 84
    },
    {
        id: 5,
        unit_name: 'Scoopy Black',
        unit_image: 'https://via.placeholder.com/48x48/000000/ffffff?text=SB',
        total_units: 64
    }
];

// Methods
const fetchTopUnitsData = async () => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // TODO: Replace with real API call when backend is ready
        // const response = await axios.get('/api/v1/dashboard/unit-inbound/top-units', {
        //     params: {
        //         dealer_id: effectiveDealerId.value,
        //         date_from: props.dateFrom,
        //         date_to: props.dateTo
        //     }
        // });

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Use mock data for now
        topUnits.value = mockTopUnitsData.map((item, index) => ({
            id: item.id,
            rank: index + 1,
            name: item.unit_name,
            image: item.unit_image,
            totalUnits: item.total_units,
            description: `${item.total_units} Units`
        }));

    } catch (err) {
        console.error('Error fetching top units data:', err);
        error.value = 'Failed to fetch top units data';
    } finally {
        loading.value = false;
    }
};

// Get unit image based on unit name
const getUnitImage = (unitName) => {
    const unitImages = {
        'Scoopy Black': 'https://via.placeholder.com/48x48/000000/ffffff?text=SB',
        'Vario 160 Navy': 'https://via.placeholder.com/48x48/000080/ffffff?text=VN',
        'Beat Cream': 'https://via.placeholder.com/48x48/F5F5DC/000000?text=BC'
    };
    return unitImages[unitName] || 'https://via.placeholder.com/48x48/FF5722/FFFFFF?text=🏍️';
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchTopUnitsData();
}, { immediate: false });

// Lifecycle
onMounted(() => {
    fetchTopUnitsData();
});
</script>

<template>
    <Card class="h-full">
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Top Units List -->
            <div v-if="!error && topUnits.length > 0" class="space-y-4">
                <div
                    v-for="unit in topUnits"
                    :key="unit.id"
                    class="flex items-center space-x-4 p-3 rounded-lg border border-surface-200 hover:bg-surface-50 transition-colors"
                >
                    <!-- Unit Image -->
                    <div class="flex-shrink-0">
                        <img
                            :src="unit.image"
                            :alt="unit.name"
                            class="w-12 h-12 object-cover rounded-lg border-2 border-surface-200"
                            @error="$event.target.src = 'https://via.placeholder.com/48x48/FF5722/FFFFFF?text=🏍️'"
                        />
                    </div>

                    <!-- Unit Details -->
                    <div class="flex-grow min-w-0">
                        <h4 class="font-bold text-base text-surface-900 truncate">{{ unit.name }}</h4>
                        <p class="text-sm text-surface-600">{{ unit.description }}</p>
                    </div>

                    <!-- Total Units -->
                    <div class="flex-shrink-0 text-right">
                        <div class="text-2xl font-bold text-red-500">{{ unit.totalUnits }}</div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading units...</p>
            </div>

            <!-- Empty State -->
            <div v-if="!loading && !error && topUnits.length === 0" class="text-center py-8">
                <i class="pi pi-info-circle text-2xl text-muted-color mb-2"></i>
                <p class="text-muted-color text-sm">No unit data available</p>
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
    
    .text-2xl {
        font-size: 1.25rem;
    }
}
</style>
