<template>
    <div class="activities-container">
        <div class="flex justify-between items-center mb-6">
            <div>
                <h1 class="text-3xl font-bold text-gray-800">System Activities</h1>
                <p class="text-gray-600 mt-1">Today's system activity logs</p>
            </div>
            <div class="flex gap-2 items-center">
                <div class="flex items-center gap-2">
                    <label class="text-sm text-gray-600">Auto-refresh</label>
                    <InputSwitch v-model="autoRefresh" @change="toggleAutoRefresh" />
                </div>
                <Button 
                    icon="pi pi-refresh" 
                    label="Refresh All" 
                    @click="refreshAll" 
                    :loading="refreshing"
                    severity="secondary"
                />
            </div>
        </div>

        <div class="text-sm text-gray-500 mb-4">
            Last updated: {{ lastUpdated }}
        </div>

        <TabView v-model:activeIndex="activeTab">
            <TabPanel>
                <template #header>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-sign-in"></i>
                        <span>Login Activities</span>
                        <Badge v-if="counts.login > 0" :value="counts.login" severity="info" />
                    </div>
                </template>
                <LoginActivities ref="loginActivitiesRef" @loaded="onLoginLoaded" />
            </TabPanel>

            <TabPanel>
                <template #header>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-cloud"></i>
                        <span>API Logs</span>
                        <Badge v-if="counts.apiLogs > 0" :value="counts.apiLogs" severity="info" />
                    </div>
                </template>
                <ApiLogActivities ref="apiLogsRef" @loaded="onApiLogsLoaded" />
            </TabPanel>

            <TabPanel>
                <template #header>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-star"></i>
                        <span>Google Reviews</span>
                        <Badge v-if="counts.googleReviews > 0" :value="counts.googleReviews" severity="info" />
                    </div>
                </template>
                <GoogleReviewActivities ref="googleReviewsRef" @loaded="onGoogleReviewsLoaded" />
            </TabPanel>

            <TabPanel>
                <template #header>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-upload"></i>
                        <span>Customer Satisfaction</span>
                        <Badge v-if="counts.satisfaction > 0" :value="counts.satisfaction" severity="info" />
                    </div>
                </template>
                <CustomerSatisfactionActivities ref="satisfactionRef" @loaded="onSatisfactionLoaded" />
            </TabPanel>
        </TabView>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import { formatToIndonesiaTime } from '@/utils/dateFormatter';
import LoginActivities from './LoginActivities.vue';
import ApiLogActivities from './ApiLogActivities.vue';
import GoogleReviewActivities from './GoogleReviewActivities.vue';
import CustomerSatisfactionActivities from './CustomerSatisfactionActivities.vue';

const activeTab = ref(0);
const autoRefresh = ref(false);
const refreshing = ref(false);
const lastUpdated = ref(formatToIndonesiaTime(new Date()));
let refreshInterval = null;

const counts = reactive({
    login: 0,
    apiLogs: 0,
    googleReviews: 0,
    satisfaction: 0
});

const loginActivitiesRef = ref(null);
const apiLogsRef = ref(null);
const googleReviewsRef = ref(null);
const satisfactionRef = ref(null);

const onLoginLoaded = (count) => {
    counts.login = count;
};

const onApiLogsLoaded = (count) => {
    counts.apiLogs = count;
};

const onGoogleReviewsLoaded = (count) => {
    counts.googleReviews = count;
};

const onSatisfactionLoaded = (count) => {
    counts.satisfaction = count;
};

const refreshAll = async () => {
    refreshing.value = true;
    try {
        await Promise.all([
            loginActivitiesRef.value?.loadData(),
            apiLogsRef.value?.loadData(),
            googleReviewsRef.value?.loadData(),
            satisfactionRef.value?.loadData()
        ]);
        lastUpdated.value = formatToIndonesiaTime(new Date());
    } finally {
        refreshing.value = false;
    }
};

const toggleAutoRefresh = () => {
    if (autoRefresh.value) {
        refreshInterval = setInterval(refreshAll, 30000);
    } else {
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
    }
};

onMounted(() => {
    // Initial load handled by child components
});

onUnmounted(() => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
</script>

<style scoped>
.activities-container {
    padding: 1.5rem;
}
</style>
