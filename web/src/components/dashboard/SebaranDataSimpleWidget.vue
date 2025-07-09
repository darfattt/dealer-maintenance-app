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
const regionData = ref([]);

// West Java regions data
const westJavaRegions = [
    { name: 'Arcamanik', percentage: 30, color: '#10B981' },
    { name: 'Astanaanyar', percentage: 15, color: '#F59E0B' },
    { name: 'Bandung Kidul', percentage: 3, color: '#EF4444' },
    { name: 'Andir', percentage: 5, color: '#3B82F6' },
    { name: 'Others', percentage: 2, color: '#6B7280' }
];

// Methods
const fetchSebaranData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Use the West Java regions data
        regionData.value = westJavaRegions;
    } catch (err) {
        console.error('Error fetching sebaran data:', err);
        error.value = 'Failed to fetch distribution data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchSebaranData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchSebaranData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <span class="text-sm font-bold uppercase">SEBARAN DATA PROSPECT</span>
            </div>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Visual Map and Legend Container -->
            <div v-if="!error" class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <!-- Visual Map Representation -->
                <div class="lg:col-span-2">
                    <div class="h-64 w-full rounded-lg border border-surface-200 bg-surface-50 p-4 relative">
                        <!-- West Java Map Visual -->
                        <div class="text-center mb-4">
                            <h3 class="text-lg font-semibold text-muted-color">West Java Region</h3>
                            <p class="text-xs text-muted-color">Prospect Distribution</p>
                        </div>
                        
                        <!-- Visual Grid Representation -->
                        <div class="grid grid-cols-3 gap-4 h-40">
                            <!-- Region blocks positioned to roughly represent West Java -->
                            <div class="flex flex-col justify-center items-center">
                                <div
                                    class="w-12 h-12 rounded-lg flex items-center justify-center text-white text-xs font-bold shadow-md cursor-pointer hover:scale-110 transition-transform"
                                    :style="{ backgroundColor: regionData[1]?.color }"
                                    :title="`${regionData[1]?.name}: ${regionData[1]?.percentage}%`"
                                >
                                    {{ regionData[1]?.percentage }}%
                                </div>
                                <span class="text-xs mt-1">{{ regionData[1]?.name }}</span>
                            </div>
                            
                            <div class="flex flex-col justify-start items-center pt-4">
                                <div
                                    class="w-16 h-16 rounded-lg flex items-center justify-center text-white text-sm font-bold shadow-md cursor-pointer hover:scale-110 transition-transform"
                                    :style="{ backgroundColor: regionData[0]?.color }"
                                    :title="`${regionData[0]?.name}: ${regionData[0]?.percentage}%`"
                                >
                                    {{ regionData[0]?.percentage }}%
                                </div>
                                <span class="text-xs mt-1">{{ regionData[0]?.name }}</span>
                            </div>
                            
                            <div class="flex flex-col justify-end items-center pb-4">
                                <div
                                    class="w-10 h-10 rounded-lg flex items-center justify-center text-white text-xs font-bold shadow-md cursor-pointer hover:scale-110 transition-transform"
                                    :style="{ backgroundColor: regionData[3]?.color }"
                                    :title="`${regionData[3]?.name}: ${regionData[3]?.percentage}%`"
                                >
                                    {{ regionData[3]?.percentage }}%
                                </div>
                                <span class="text-xs mt-1">{{ regionData[3]?.name }}</span>
                            </div>
                        </div>
                        
                        <!-- Bottom regions -->
                        <div class="flex justify-center space-x-8 mt-4">
                            <div class="flex flex-col items-center">
                                <div
                                    class="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold shadow-md cursor-pointer hover:scale-110 transition-transform"
                                    :style="{ backgroundColor: regionData[2]?.color }"
                                    :title="`${regionData[2]?.name}: ${regionData[2]?.percentage}%`"
                                >
                                    {{ regionData[2]?.percentage }}%
                                </div>
                                <span class="text-xs mt-1">{{ regionData[2]?.name }}</span>
                            </div>
                            
                            <div class="flex flex-col items-center">
                                <div
                                    class="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold shadow-md cursor-pointer hover:scale-110 transition-transform"
                                    :style="{ backgroundColor: regionData[4]?.color }"
                                    :title="`${regionData[4]?.name}: ${regionData[4]?.percentage}%`"
                                >
                                    {{ regionData[4]?.percentage }}%
                                </div>
                                <span class="text-xs mt-1">{{ regionData[4]?.name }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Legend -->
                <div class="lg:col-span-1 flex flex-col justify-center">
                    <div class="space-y-3">
                        <div
                            v-for="(region, index) in regionData"
                            :key="index"
                            class="flex items-center justify-between p-2 rounded border border-surface-200 hover:bg-surface-50 transition-colors"
                        >
                            <div class="flex items-center space-x-2">
                                <div
                                    class="w-4 h-4 rounded-full border-2 border-white shadow-sm"
                                    :style="{ backgroundColor: region.color }"
                                ></div>
                                <span class="text-xs font-medium">{{ region.name }}</span>
                            </div>
                            <div class="text-right">
                                <div 
                                    class="font-bold text-sm px-2 py-1 rounded text-white"
                                    :style="{ backgroundColor: region.color }"
                                >
                                    {{ region.percentage }}%
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading distribution data...</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* Custom hover effects */
.region-block {
    transition: all 0.2s ease-in-out;
}

.region-block:hover {
    transform: scale(1.1);
    z-index: 10;
}
</style>
