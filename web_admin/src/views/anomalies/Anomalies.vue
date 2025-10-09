<template>
    <div class="anomalies-container">
        <div class="flex justify-between items-center mb-6">
            <div>
                <h1 class="text-3xl font-bold text-gray-800">Integration Anomalies</h1>
                <p class="text-gray-600 mt-1">Monitor WhatsApp and Google Scrape integration failures</p>
            </div>
            <div class="flex gap-2 items-center">
                <div class="flex items-center gap-2">
                    <label class="text-sm text-gray-600">Auto-refresh</label>
                    <InputSwitch v-model="autoRefresh" @change="toggleAutoRefresh" />
                </div>
                <Button
                    icon="pi pi-refresh"
                    label="Refresh"
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
            <!-- WhatsApp Anomalies Tab -->
            <TabPanel>
                <template #header>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-whatsapp"></i>
                        <span>WhatsApp Failures</span>
                        <Badge v-if="counts.whatsapp > 0" :value="counts.whatsapp" severity="danger" />
                    </div>
                </template>
                <WhatsAppAnomalies ref="whatsappRef" @loaded="onWhatsAppLoaded" />
            </TabPanel>

            <!-- Google Scrape Anomalies Tab -->
            <TabPanel>
                <template #header>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-google"></i>
                        <span>Google Scrape Failures</span>
                        <Badge v-if="counts.googleScrape > 0" :value="counts.googleScrape" severity="danger" />
                    </div>
                </template>
                <GoogleScrapeAnomalies ref="googleScrapeRef" @loaded="onGoogleScrapeLoaded" />
            </TabPanel>
        </TabView>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import { formatToIndonesiaTime } from '@/utils/dateFormatter';
import WhatsAppAnomalies from './WhatsAppAnomalies.vue';
import GoogleScrapeAnomalies from './GoogleScrapeAnomalies.vue';

const activeTab = ref(0);
const autoRefresh = ref(false);
const refreshing = ref(false);
const lastUpdated = ref(formatToIndonesiaTime(new Date()));
let refreshInterval = null;

const counts = reactive({
    whatsapp: 0,
    googleScrape: 0
});

const whatsappRef = ref(null);
const googleScrapeRef = ref(null);

const onWhatsAppLoaded = (count) => {
    counts.whatsapp = count;
};

const onGoogleScrapeLoaded = (count) => {
    counts.googleScrape = count;
};

const refreshAll = async () => {
    refreshing.value = true;
    try {
        // Refresh based on active tab
        if (activeTab.value === 0) {
            // WhatsApp Anomalies Tab
            await whatsappRef.value?.loadData();
        } else if (activeTab.value === 1) {
            // Google Scrape Anomalies Tab
            await googleScrapeRef.value?.loadData();
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
.anomalies-container {
    padding: 1.5rem;
}
</style>
