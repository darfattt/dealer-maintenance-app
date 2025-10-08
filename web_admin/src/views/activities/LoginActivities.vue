<template>
    <div class="activity-list">
        <ProgressSpinner v-if="loading" class="flex justify-center" />
        
        <div v-else-if="!activities.length" class="empty-state">
            <i class="pi pi-inbox text-6xl text-gray-300"></i>
            <p class="text-gray-500 mt-4">No login activities today</p>
        </div>

        <div v-else class="space-y-3">
            <Card v-for="activity in activities" :key="activity.id" class="activity-card">
                <template #content>
                    <div class="flex gap-4">
                        <div class="flex-shrink-0">
                            <div 
                                class="w-12 h-12 rounded-full flex items-center justify-center" 
                                :class="getActivityBgColor(activity.action, activity.success)"
                            >
                                <i 
                                    class="text-xl" 
                                    :class="[getActivityIcon(activity.action), getActivityColor(activity.action, activity.success)]"
                                ></i>
                            </div>
                        </div>
                        <div class="flex-1">
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <h4 class="font-semibold text-gray-800">{{ activity.email }}</h4>
                                    <div class="flex gap-2 items-center mt-1">
                                        <Tag 
                                            :value="formatAction(activity.action)" 
                                            :severity="getStatusSeverity(activity.action, activity.success)"
                                        />
                                        <span class="text-sm text-gray-500">{{ activity.ip_address || 'Unknown IP' }}</span>
                                    </div>
                                </div>
                                <span class="text-sm text-gray-500">{{ formatToIndonesiaTime(activity.created_at) }}</span>
                            </div>
                            
                            <div v-if="activity.failure_reason" class="mt-2 p-2 bg-red-50 rounded text-sm text-red-700">
                                <i class="pi pi-exclamation-circle mr-1"></i>
                                {{ activity.failure_reason }}
                            </div>
                            
                            <div v-if="activity.user_agent" class="mt-2 text-xs text-gray-500 truncate">
                                {{ activity.user_agent }}
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
import { getActivityIcon, getActivityColor, getActivityBgColor, getStatusSeverity } from '@/utils/activityHelpers';

const emit = defineEmits(['loaded']);
const toast = useToast();

const loading = ref(false);
const activities = ref([]);

const formatAction = (action) => {
    const labels = { 'LOGIN': 'Login', 'LOGOUT': 'Logout', 'LOGIN_FAILED': 'Login Failed' };
    return labels[action] || action;
};

const loadData = async () => {
    loading.value = true;
    try {
        const result = await ActivityService.getLoginActivities();
        if (result.success) {
            activities.value = result.data.activities || [];
            emit('loaded', activities.value.length);
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.message, life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load login activities', life: 3000 });
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
