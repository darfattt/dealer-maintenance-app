<template>
    <div class="activity-list">
        <ProgressSpinner v-if="loading" class="flex justify-center" />
        
        <div v-else-if="!logs.length" class="empty-state">
            <i class="pi pi-inbox text-6xl text-gray-300"></i>
            <p class="text-gray-500 mt-4">No API logs today</p>
        </div>

        <div v-else class="space-y-3">
            <Card v-for="log in logs" :key="log.id" class="activity-card">
                <template #content>
                    <div class="flex gap-4">
                        <div class="flex-shrink-0">
                            <div class="w-12 h-12 rounded-full flex items-center justify-center bg-blue-50">
                                <i class="pi pi-cloud text-xl text-blue-500"></i>
                            </div>
                        </div>
                        <div class="flex-1">
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <h4 class="font-semibold text-gray-800">{{ log.request_name }}</h4>
                                    <div class="flex gap-2 items-center mt-1">
                                        <Tag :value="log.request_method" :class="getHttpMethodColor(log.request_method)" />
                                        <Tag :value="log.response_code" :severity="getCodeSeverity(log.response_code)" />
                                        <span class="text-sm text-gray-500">{{ log.dealer_id || 'No Dealer' }}</span>
                                    </div>
                                </div>
                                <span class="text-sm text-gray-500">{{ formatToIndonesiaTime(log.request_timestamp) }}</span>
                            </div>
                            
                            <div class="text-sm text-gray-600 mt-2">
                                <code class="bg-gray-100 px-2 py-1 rounded">{{ log.endpoint }}</code>
                            </div>
                            
                            <div class="flex gap-4 mt-2 text-sm text-gray-600">
                                <span v-if="log.processing_time_ms">⏱️ {{ log.processing_time_ms }}ms</span>
                                <span v-if="log.user_email">👤 {{ log.user_email }}</span>
                                <span v-if="log.request_ip">📍 {{ log.request_ip }}</span>
                            </div>
                            
                            <div v-if="log.error_message" class="mt-2 p-2 bg-red-50 rounded text-sm text-red-700">
                                <i class="pi pi-exclamation-circle mr-1"></i>
                                {{ log.error_message }}
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
import { getHttpMethodColor } from '@/utils/activityHelpers';

const emit = defineEmits(['loaded']);
const toast = useToast();

const loading = ref(false);
const logs = ref([]);

const getCodeSeverity = (code) => {
    if (code >= 200 && code < 300) return 'success';
    if (code >= 400 && code < 500) return 'warning';
    if (code >= 500) return 'danger';
    return 'info';
};

const loadData = async () => {
    loading.value = true;
    try {
        const result = await ActivityService.getApiLogs();
        if (result.success) {
            logs.value = result.data.logs || [];
            emit('loaded', logs.value.length);
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.message, life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load API logs', life: 3000 });
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
