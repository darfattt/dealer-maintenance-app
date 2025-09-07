<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useDealers } from '@/composables/useDealers';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';

// Import widgets
import TopLeasingWidget from '@/components/dashboard/TopLeasingWidget.vue';
import POCreationWidget from '@/components/dashboard/POCreationWidget.vue';
import PODocumentStatusWidget from '@/components/dashboard/PODocumentStatusWidget.vue';
import LeasingDataHistoryWidget from '@/components/dashboard/LeasingDataHistoryWidget.vue';

// Router and Auth store
const router = useRouter();
const authStore = useAuthStore();

// Use dealers composable for dynamic dealer loading
const { dealerOptions, isLoading: dealersLoading, hasError: dealersError } = useDealers();

// Filter controls - Use dealer from auth for DEALER_USER, fallback to first available dealer
const getInitialDealer = () => {
    if (authStore.userRole === 'DEALER_USER') {
        return authStore.userDealerId;
    }
    return '';
};

const selectedDealer = ref(getInitialDealer());
const selectedDateFrom = ref(new Date(new Date().getFullYear(), 0, 1)); // Start of current year
const selectedDateTo = ref(new Date()); // Today

// Computed properties
const isDealerUser = computed(() => {
    return authStore.userRole === 'DEALER_USER';
});

const showDealerDropdown = computed(() => {
    return !isDealerUser.value;
});

// Format dates for API calls
const formattedDateFrom = computed(() => {
    if (!selectedDateFrom.value) return '';
    return selectedDateFrom.value.toISOString().split('T')[0];
});

const formattedDateTo = computed(() => {
    if (!selectedDateTo.value) return '';
    return selectedDateTo.value.toISOString().split('T')[0];
});

// Navigation methods
const goBack = () => {
    router.push('/');
};

const refreshData = () => {
    // Refresh logic here
    console.log('Refreshing Handle Leasing data...');
};

// Lifecycle
onMounted(() => {
    // Initialize any required data
});

// Watch for dealers to be loaded and set initial dealer for non-DEALER_USER
watch(
    dealerOptions,
    (newDealers) => {
        if (newDealers.length > 0 && !selectedDealer.value && authStore.userRole !== 'DEALER_USER') {
            selectedDealer.value = newDealers[0].value;
        }
    },
    { immediate: true }
);
</script>

<template>
    <div class="p-6 bg-surface-50 min-h-screen">
        <!-- Header with Filter Controls -->
        <div class="space-y-6">
            <!-- Header with Back Button, Title, Refresh and Filter Controls in One Row -->
            <div class="flex items-center justify-between mb-8">
                <!-- Left Side: Back Button, Title, and Refresh -->
                <div class="flex items-center space-x-4">
                    <h1 class="text-2xl font-bold text-surface-900 uppercase tracking-wide">HANDLE LEASING</h1>
                </div>

                <!-- Right Side: Filter Controls -->
                <div class="flex items-center space-x-4">
                    <Button icon="pi pi-arrow-left" text @click="goBack" class="text-surface-600 hover:text-surface-900" v-tooltip.top="'Back to Dashboard'" />
                    <Button icon="pi pi-refresh" text @click="refreshData" class="text-surface-600 hover:text-surface-900" v-tooltip.top="'Refresh Data'" />
                    <!-- Dealer Dropdown (only for non-DEALER_USER roles) -->
                    <div v-if="showDealerDropdown" class="flex items-center space-x-2">
                        <label class="text-sm font-medium text-surface-700">Dealer:</label>
                        <Dropdown
                            v-model="selectedDealer"
                            :options="dealerOptions"
                            optionLabel="label"
                            optionValue="value"
                            :placeholder="dealersLoading ? 'Loading dealers...' : dealersError ? 'Error loading dealers' : 'Select Dealer'"
                            :loading="dealersLoading"
                            :disabled="dealersLoading || dealersError"
                            class="w-48"
                        />
                    </div>

                    <!-- Date Range -->
                    <div class="flex items-center space-x-2">
                        <Calendar v-model="selectedDateFrom" placeholder="From Date" dateFormat="dd-mm-yy" class="w-36" showIcon />
                        <span class="text-sm text-surface-500">to</span>
                        <Calendar v-model="selectedDateTo" placeholder="To Date" dateFormat="dd-mm-yy" class="w-36" showIcon />
                    </div>
                </div>
            </div>

            <!-- First Row - 2 Columns -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- First Column: Reused TopLeasingWidget -->
                <div>
                    <!-- Top 5 Leasing Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">Top 5 Leasing</h3>
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <TopLeasingWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                    </div>
                </div>

                <!-- Second Column: PO Creation Widget -->
                <div>
                    <!-- PO Creation Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">Pembuatan PO</h3>
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <POCreationWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                    </div>
                </div>
            </div>

            <!-- Second Row - 2 Columns -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- First Column: PO Document Status Widget -->
                <div>
                    <!-- PO Document Status Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">Status Dokumen PO</h3>
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <PODocumentStatusWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                    </div>
                </div>

                <!-- Second Column: Leasing Data History Widget -->
                <div>
                    <!-- Data History Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <!-- <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
                            Data History
                        </h3> -->
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <LeasingDataHistoryWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.widget-with-title {
    @apply bg-white rounded-b-lg border border-t-0 border-surface-200 shadow-sm;
}
</style>
