<template>
    <div class="activity-list">
        <ProgressSpinner v-if="loading" class="flex justify-center" />
        
        <div v-else-if="!uploads.length" class="empty-state">
            <i class="pi pi-inbox text-6xl text-gray-300"></i>
            <p class="text-gray-500 mt-4">No uploads today</p>
        </div>

        <div v-else class="space-y-3">
            <Card v-for="upload in uploads" :key="upload.id" class="activity-card">
                <template #content>
                    <div class="flex gap-4">
                        <div class="flex-shrink-0">
                            <div 
                                class="w-12 h-12 rounded-full flex items-center justify-center" 
                                :class="getBgColor(upload.upload_status)"
                            >
                                <i class="pi pi-upload text-xl" :class="getColor(upload.upload_status)"></i>
                            </div>
                        </div>
                        <div class="flex-1">
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <h4 class="font-semibold text-gray-800">{{ upload.file_name }}</h4>
                                    <div class="flex gap-2 items-center mt-1">
                                        <Tag :value="upload.upload_status" :severity="getSeverity(upload.upload_status)" />
                                        <span v-if="upload.file_size" class="text-sm text-gray-500">
                                            {{ formatFileSize(upload.file_size) }}
                                        </span>
                                    </div>
                                </div>
                                <span class="text-sm text-gray-500">{{ formatToIndonesiaTime(upload.upload_date) }}</span>
                            </div>
                            
                            <div class="flex gap-4 mt-2 text-sm">
                                <span class="text-gray-600">📊 {{ upload.total_records }} total</span>
                                <span class="text-green-600">✓ {{ upload.successful_records }} success</span>
                                <span v-if="upload.failed_records > 0" class="text-red-600">
                                    ✗ {{ upload.failed_records }} failed
                                </span>
                            </div>
                            
                            <div v-if="upload.uploaded_by" class="mt-2 text-sm text-gray-600">
                                👤 Uploaded by: {{ upload.uploaded_by }}
                            </div>
                            
                            <div v-if="upload.error_message" class="mt-2 p-2 bg-red-50 rounded text-sm text-red-700">
                                <i class="pi pi-exclamation-circle mr-1"></i>
                                {{ upload.error_message }}
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
import { formatToIndonesiaTime, formatFileSize } from '@/utils/dateFormatter';

const emit = defineEmits(['loaded']);
const toast = useToast();

const loading = ref(false);
const uploads = ref([]);

const getSeverity = (status) => {
    if (status === 'COMPLETED') return 'success';
    if (status === 'FAILED') return 'danger';
    if (status === 'PROCESSING') return 'info';
    return 'secondary';
};

const getColor = (status) => {
    if (status === 'COMPLETED') return 'text-green-500';
    if (status === 'FAILED') return 'text-red-500';
    if (status === 'PROCESSING') return 'text-blue-500';
    return 'text-gray-500';
};

const getBgColor = (status) => {
    if (status === 'COMPLETED') return 'bg-green-50';
    if (status === 'FAILED') return 'bg-red-50';
    if (status === 'PROCESSING') return 'bg-blue-50';
    return 'bg-gray-50';
};

const loadData = async () => {
    loading.value = true;
    try {
        const result = await ActivityService.getCustomerSatisfactionUploads();
        if (result.success) {
            uploads.value = result.data.uploads || [];
            emit('loaded', uploads.value.length);
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.message, life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load uploads', life: 3000 });
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
