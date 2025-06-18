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
const leasingData = ref([]);

// Methods
const fetchTopLeasingData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Dummy data for now
        leasingData.value = [
            { 
                name: 'PT. Federasi International Finance', 
                count: 285, 
                color: '#3B82F6',
                logo: '🏦'
            },
            { 
                name: 'Adira Finance', 
                count: 146, 
                color: '#10B981',
                logo: '🏛️'
            },
            { 
                name: 'PT. Summit Oto Finance', 
                count: 120, 
                color: '#F59E0B',
                logo: '🏢'
            },
            { 
                name: 'PT. Mega Finance', 
                count: 98, 
                color: '#EF4444',
                logo: '🏪'
            },
            { 
                name: 'PT. BCA Finance', 
                count: 56, 
                color: '#8B5CF6',
                logo: '🏬'
            }
        ];
    } catch (err) {
        console.error('Error fetching top leasing data:', err);
        error.value = 'Failed to fetch top leasing data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchTopLeasingData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchTopLeasingData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <span>Top 5 Leasing</span>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Leasing Data -->
            <div v-if="!error && leasingData.length > 0" class="space-y-3">
                <div
                    v-for="(leasing, index) in leasingData"
                    :key="index"
                    class="flex items-center justify-between p-3 rounded-lg border border-surface-200 hover:bg-surface-50 transition-colors"
                >
                    <div class="flex items-center space-x-3">
                        <div class="text-2xl">{{ leasing.logo }}</div>
                        <div>
                            <div class="font-medium text-sm">{{ leasing.name }}</div>
                        </div>
                    </div>
                    <div class="text-right">
                        <div 
                            class="text-2xl font-bold"
                            :style="{ color: leasing.color }"
                        >
                            {{ leasing.count }}
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
