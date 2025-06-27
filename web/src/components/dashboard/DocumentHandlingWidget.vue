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
const documentData = ref({});

// Methods
const fetchDocumentHandlingData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Dummy data for now
        documentData.value = {
            title: 'PENGAJUAN FAKTUR',
            count: 153,
            trend: 'up', // 'up', 'down', 'stable'
            color: '#1E40AF'
        };
    } catch (err) {
        console.error('Error fetching document handling data:', err);
        error.value = 'Failed to fetch document handling data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchDocumentHandlingData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchDocumentHandlingData();
});
</script>

<template>
    <Card class="h-full">
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Document Data -->
            <div v-if="!error && Object.keys(documentData).length > 0" class="text-center py-6">
                <div class="mb-4">
                    <h3 class="text-sm font-medium text-muted-color mb-2">
                        {{ documentData.title }}
                    </h3>
                    <div class="relative inline-block">
                        <div 
                            class="text-6xl font-bold rounded-full w-32 h-32 flex items-center justify-center mx-auto"
                            :style="{ 
                                backgroundColor: documentData.color + '20',
                                color: documentData.color 
                            }"
                        >
                            {{ documentData.count }}
                        </div>
                        <div 
                            v-if="documentData.trend === 'up'"
                            class="absolute -top-2 -right-2 bg-green-500 text-white rounded-full p-1"
                        >
                            <i class="pi pi-arrow-up text-xs"></i>
                        </div>
                        <div 
                            v-else-if="documentData.trend === 'down'"
                            class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1"
                        >
                            <i class="pi pi-arrow-down text-xs"></i>
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
