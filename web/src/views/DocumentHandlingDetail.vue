<script setup>
import { ref, computed, watch } from 'vue';
import { useDealers } from '@/composables/useDealers';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import Button from 'primevue/button';

// Import widgets
import PermohonanFakturWidget from '@/components/dashboard/PermohonanFakturWidget.vue';
import STNKDiterimaKonsumenWidget from '@/components/dashboard/STNKDiterimaKonsumenWidget.vue';
import BPKBDiterimaKonsumenWidget from '@/components/dashboard/BPKBDiterimaKonsumenWidget.vue';
import DocumentHandlingDataHistoryWidget from '@/components/dashboard/DocumentHandlingDataHistoryWidget.vue';

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


// Computed properties for formatted dates
const formattedDateFrom = computed(() => {
    if (!selectedDateFrom.value) return '';
    return selectedDateFrom.value.toISOString().split('T')[0];
});

const formattedDateTo = computed(() => {
    if (!selectedDateTo.value) return '';
    return selectedDateTo.value.toISOString().split('T')[0];
});

// Methods
const goBack = () => {
    router.push('/');
};

const refreshData = () => {
    // Force refresh by updating a reactive property
    const currentDateFrom = selectedDateFrom.value;
    selectedDateFrom.value = null;
    setTimeout(() => {
        selectedDateFrom.value = currentDateFrom;
    }, 10);
};

// Lifecycle
onMounted(() => {
    // Set default dealer if user is DEALER_USER
    if (authStore.userRole === 'DEALER_USER' && authStore.dealerId) {
        selectedDealer.value = authStore.dealerId;
    }
});

// Watch for dealers to be loaded and set initial dealer for non-DEALER_USER
watch(dealerOptions, (newDealers) => {
    if (newDealers.length > 0 && !selectedDealer.value && authStore.userRole !== 'DEALER_USER') {
        selectedDealer.value = newDealers[0].value;
    }
}, { immediate: true });
</script>

<template>
    <div class="p-6 bg-surface-50 min-h-screen">
        <!-- Header with Back Button, Title, Refresh and Filter Controls in One Row -->
        <div class="flex items-center justify-between mb-8">
            <!-- Left Side: Back Button, Title, and Refresh -->
            <div class="flex items-center space-x-4">
               
                <h1 class="text-2xl font-bold text-surface-900 uppercase tracking-wide">
                    DOCUMENT HANDLING
                </h1>
                
            </div>

            <!-- Right Side: Filter Controls -->
            <div class="flex items-center space-x-4">
                 <Button
                    icon="pi pi-arrow-left"
                    text
                    @click="goBack"
                    class="text-surface-600 hover:text-surface-900"
                    v-tooltip.top="'Back to Dashboard'"
                />
                 <Button
                    icon="pi pi-refresh"
                    text
                    @click="refreshData"
                    class="text-surface-600 hover:text-surface-900"
                    v-tooltip.top="'Refresh Data'"
                />
                <!-- Dealer Selection (only for non-DEALER_USER) -->
                <div v-if="authStore.userRole !== 'DEALER_USER'" class="flex items-center space-x-2">
                    <label for="dealer-filter" class="text-sm font-medium text-surface-700">Dealer:</label>
                    <Dropdown
                        v-model="selectedDealer"
                        :options="dealerOptions"
                        optionLabel="label"
                        optionValue="value"
                            :placeholder="dealersLoading ? 'Loading dealers...' : (dealersError ? 'Error loading dealers' : 'Select Dealer')"
                            :loading="dealersLoading"
                            :disabled="dealersLoading || dealersError"
                        class="w-48"
                    />
                </div>

                <!-- Date Range Filters -->
                <div class="flex items-center space-x-2">
                    <Calendar
                        v-model="selectedDateFrom"
                        dateFormat="dd-mm-yy"
                        placeholder="From Date"
                        class="w-36"
                        showIcon
                    />
                    <span class="text-sm text-surface-500">to</span>
                    <Calendar
                        v-model="selectedDateTo"
                        dateFormat="dd-mm-yy"
                        placeholder="To Date"
                        class="w-36"
                        showIcon
                    />
                </div>
               
            </div>
        </div>

        <div class="space-y-6">

        <!-- First Row: 3 Columns for Status Widgets -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <!-- Permohonan Faktur Widget -->
            <div class="md:col-span-1">
                <PermohonanFakturWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>

            <!-- STNK Diterima Konsumen Widget -->
            <div class="md:col-span-1">
                <STNKDiterimaKonsumenWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>

            <!-- BPKB Diterima Konsumen Widget -->
            <div class="md:col-span-1">
                <BPKBDiterimaKonsumenWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>
        </div>

        <!-- Second Row: 1 Column for Data History -->
        <div class="grid grid-cols-1 gap-6">
            <div class="col-span-1">
                <DocumentHandlingDataHistoryWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>
        </div>
        </div>
    </div>
</template>

<style scoped>
/* Custom styles for the detail view */
.widget-with-title {
    border-top: none;
    border-top-left-radius: 0;
    border-top-right-radius: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .grid {
        grid-template-columns: 1fr;
    }
    
    .flex-wrap {
        flex-direction: column;
        align-items: stretch;
    }
    
    .flex-wrap > div {
        width: 100%;
    }
}
</style>
