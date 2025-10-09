<template>
    <div class="summary-container">
        <div class="flex justify-between items-center mb-6">
            <div>
                <h1 class="text-3xl font-bold text-gray-800">System Logs Summary</h1>
                <p class="text-gray-600 mt-1">Dealer activity overview and statistics</p>
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
            <!-- API Logs Tab -->
            <TabPanel>
                <template #header>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-cloud"></i>
                        <span>API Logs Summary</span>
                    </div>
                </template>

                <TabView v-model:activeIndex="apiLogsSubTab" :key="'api-logs-' + activeTab" class="mt-4">
                    <TabPanel>
                        <template #header>
                            <div class="flex items-center gap-2">
                                <i class="pi pi-calendar"></i>
                                <span>Today</span>
                            </div>
                        </template>
                        <ApiLogsSummary ref="apiLogsTodayRef" @loaded="onApiLogsTodayLoaded" />
                    </TabPanel>
                    <TabPanel>
                        <template #header>
                            <div class="flex items-center gap-2">
                                <i class="pi pi-chart-line"></i>
                                <span>This Week</span>
                            </div>
                        </template>
                        <ApiLogsWeeklySummary ref="apiLogsWeeklyRef" @loaded="onApiLogsWeeklyLoaded" />
                    </TabPanel>
                </TabView>
            </TabPanel>

            <!-- Google Reviews Tab -->
            <TabPanel>
                <template #header>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-star"></i>
                        <span>Google Reviews Summary</span>
                    </div>
                </template>

                <TabView v-model:activeIndex="googleReviewsSubTab" :key="'google-reviews-' + activeTab" class="mt-4">
                    <TabPanel>
                        <template #header>
                            <div class="flex items-center gap-2">
                                <i class="pi pi-calendar"></i>
                                <span>Today</span>
                            </div>
                        </template>
                        <GoogleReviewsSummary ref="googleReviewsTodayRef" @loaded="onGoogleReviewsTodayLoaded" />
                    </TabPanel>
                    <TabPanel>
                        <template #header>
                            <div class="flex items-center gap-2">
                                <i class="pi pi-chart-line"></i>
                                <span>This Week</span>
                            </div>
                        </template>
                        <GoogleReviewsWeeklySummary ref="googleReviewsWeeklyRef" @loaded="onGoogleReviewsWeeklyLoaded" />
                    </TabPanel>
                </TabView>
            </TabPanel>
        </TabView>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { formatToIndonesiaTime } from '@/utils/dateFormatter';
import ApiLogsSummary from './ApiLogsSummary.vue';
import ApiLogsWeeklySummary from './ApiLogsWeeklySummary.vue';
import GoogleReviewsSummary from './GoogleReviewsSummary.vue';
import GoogleReviewsWeeklySummary from './GoogleReviewsWeeklySummary.vue';

const activeTab = ref(0);
const apiLogsSubTab = ref(0);
const googleReviewsSubTab = ref(0);
const autoRefresh = ref(false);
const refreshing = ref(false);
const lastUpdated = ref(formatToIndonesiaTime(new Date()));
let refreshInterval = null;

const apiLogsTodayRef = ref(null);
const apiLogsWeeklyRef = ref(null);
const googleReviewsTodayRef = ref(null);
const googleReviewsWeeklyRef = ref(null);

const onApiLogsTodayLoaded = () => {
    // Can track loading state if needed
};

const onApiLogsWeeklyLoaded = () => {
    // Can track loading state if needed
};

const onGoogleReviewsTodayLoaded = () => {
    // Can track loading state if needed
};

const onGoogleReviewsWeeklyLoaded = () => {
    // Can track loading state if needed
};

const refreshAll = async () => {
    refreshing.value = true;
    try {
        // Refresh based on active tab and sub-tab
        if (activeTab.value === 0) {
            // API Logs Tab - refresh based on active sub-tab
            if (apiLogsSubTab.value === 0) {
                await apiLogsTodayRef.value?.loadData();
            } else {
                await apiLogsWeeklyRef.value?.loadData();
            }
        } else if (activeTab.value === 1) {
            // Google Reviews Tab - refresh based on active sub-tab
            if (googleReviewsSubTab.value === 0) {
                await googleReviewsTodayRef.value?.loadData();
            } else {
                await googleReviewsWeeklyRef.value?.loadData();
            }
        }
        lastUpdated.value = formatToIndonesiaTime(new Date());
    } finally {
        refreshing.value = false;
    }
};

const toggleAutoRefresh = () => {
    if (autoRefresh.value) {
        // Auto-refresh every 60 seconds
        refreshInterval = setInterval(refreshAll, 60000);
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
.summary-container {
    padding: 1.5rem;
}
</style>
