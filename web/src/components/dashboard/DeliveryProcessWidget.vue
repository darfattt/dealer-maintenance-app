<script setup>
import { ref, onMounted, watch } from 'vue';
import Card from 'primevue/card';
import ProgressBar from 'primevue/progressbar';
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
const deliveryData = ref([]);

// Methods
const fetchDeliveryProcessData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Dummy data for now
        deliveryData.value = [
            { 
                status: 'READY', 
                count: 72, 
                color: '#FBBF24',
                bgColor: '#FEF3C7'
            },
            { 
                status: 'IN PROGRESS', 
                count: 143, 
                color: '#06B6D4',
                bgColor: '#CFFAFE'
            },
            { 
                status: 'BACK TO DEALER', 
                count: 53, 
                color: '#F59E0B',
                bgColor: '#FEF3C7'
            },
            { 
                status: 'COMPLETED', 
                count: 213, 
                color: '#10B981',
                bgColor: '#D1FAE5'
            }
        ];
    } catch (err) {
        console.error('Error fetching delivery process data:', err);
        error.value = 'Failed to fetch delivery process data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchDeliveryProcessData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchDeliveryProcessData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <span>Delivery Process</span>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Delivery Data -->
            <div v-if="!error && deliveryData.length > 0" class="space-y-4">
                <div
                    v-for="(delivery, index) in deliveryData"
                    :key="index"
                    class="space-y-2"
                >
                    <div class="flex justify-between items-center">
                        <span class="text-sm font-medium">{{ delivery.status }}</span>
                        <span 
                            class="text-lg font-bold"
                            :style="{ color: delivery.color }"
                        >
                            {{ delivery.count }}
                        </span>
                    </div>
                    <div class="relative">
                        <div 
                            class="h-6 rounded-full flex items-center justify-center text-xs font-medium"
                            :style="{ 
                                backgroundColor: delivery.bgColor,
                                color: delivery.color
                            }"
                        >
                            {{ delivery.status }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading...</p>
            </div>
        </template>
    </Card>
</template>
