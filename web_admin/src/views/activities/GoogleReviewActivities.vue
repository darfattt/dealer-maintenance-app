<template>
    <div class="activity-list">
        <ProgressSpinner v-if="loading" class="flex justify-center" />
        
        <div v-else-if="!activities.length" class="empty-state">
            <i class="pi pi-inbox text-6xl text-gray-300"></i>
            <p class="text-gray-500 mt-4">No Google Review scrapes today</p>
        </div>

        <div v-else class="space-y-3">
            <Card v-for="activity in activities" :key="activity.id" class="activity-card">
                <template #content>
                    <div class="flex gap-4">
                        <div class="flex-shrink-0">
                            <div 
                                class="w-12 h-12 rounded-full flex items-center justify-center" 
                                :class="getBgColor(activity.scrape_status)"
                            >
                                <i class="pi pi-star text-xl" :class="getColor(activity.scrape_status)"></i>
                            </div>
                        </div>
                        <div class="flex-1">
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <h4 class="font-semibold text-gray-800">
                                        {{ activity.dealer_name || `Dealer ${activity.dealer_id}` }}
                                    </h4>
                                    <div class="flex gap-2 items-center mt-1">
                                        <Tag :value="activity.scrape_status" :severity="getSeverity(activity.scrape_status)" />
                                        <span class="text-sm text-gray-500">{{ activity.business_name }}</span>
                                    </div>
                                </div>
                                <span class="text-sm text-gray-500">{{ formatToIndonesiaTime(activity.scrape_date) }}</span>
                            </div>
                            
                            <div class="flex gap-4 mt-2 text-sm text-gray-600">
                                <span>⭐ {{ activity.scraped_reviews }} reviews</span>
                                <span class="text-green-600">✓ {{ activity.new_reviews }} new</span>
                                <span class="text-gray-500">↻ {{ activity.duplicate_reviews }} duplicate</span>
                                <span v-if="activity.scrape_duration_seconds">⏱️ {{ activity.scrape_duration_seconds }}s</span>
                            </div>
                            
                            <div v-if="activity.analyze_sentiment_enabled" class="mt-2 text-sm">
                                <Tag value="Sentiment Analysis" severity="info" size="small" />
                                <span class="ml-2 text-gray-600">{{ activity.sentiment_analysis_status || 'Pending' }}</span>
                            </div>
                            
                            <div v-if="activity.error_message" class="mt-2 p-2 bg-red-50 rounded text-sm text-red-700">
                                <i class="pi pi-exclamation-circle mr-1"></i>
                                {{ activity.error_message }}
                            </div>
                        </div>
                    </div>
                </template>
            </Card>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import ActivityService from '@/service/ActivityService';
import { formatToIndonesiaTime } from '@/utils/dateFormatter';

const emit = defineEmits(['loaded']);
const toast = useToast();

const loading = ref(false);
const activities = ref([]);

const getSeverity = (status) => {
    if (status === 'COMPLETED') return 'success';
    if (status === 'FAILED') return 'danger';
    if (status === 'PROCESSING') return 'info';
    if (status === 'PARTIAL') return 'warning';
    return 'secondary';
};

const getColor = (status) => {
    if (status === 'COMPLETED') return 'text-green-500';
    if (status === 'FAILED') return 'text-red-500';
    if (status === 'PROCESSING') return 'text-blue-500';
    if (status === 'PARTIAL') return 'text-orange-500';
    return 'text-gray-500';
};

const getBgColor = (status) => {
    if (status === 'COMPLETED') return 'bg-green-50';
    if (status === 'FAILED') return 'bg-red-50';
    if (status === 'PROCESSING') return 'bg-blue-50';
    if (status === 'PARTIAL') return 'bg-orange-50';
    return 'bg-gray-50';
};

const loadData = async () => {
    loading.value = true;
    try {
        const result = await ActivityService.getGoogleReviewActivities();
        if (result.success) {
            activities.value = result.data.activities || [];
            emit('loaded', activities.value.length);
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.message, life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load Google Review activities', life: 3000 });
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    loadData();
});

defineExpose({ loadData });
</script>

<style scoped>
.activity-list { padding: 1rem; }
.empty-state { text-align: center; padding: 4rem 0; }
.activity-card { margin-bottom: 0.75rem; }
</style>
