<script setup>
import { ref, computed, watch } from 'vue';
import { useDealers } from '@/composables/useDealers';
import { useRouter } from 'vue-router';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import { useAuthStore } from '@/stores/auth';
import UnitInboundStatusWidget from '@/components/dashboard/UnitInboundStatusWidget.vue';
import Top5PenerimaanUnitWidget from '@/components/dashboard/Top5PenerimaanUnitWidget.vue';
import UnitInboundDataHistoryWidget from '@/components/dashboard/UnitInboundDataHistoryWidget.vue';

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
    // For non-DEALER_USER, we'll set the dealer once dealers are loaded
    return '';
};

const selectedDealer = ref(getInitialDealer());
const selectedDateFrom = ref(new Date(new Date().getFullYear(), 0, 1)); // Start of current year
const selectedDateTo = ref(new Date()); // Today

// Check if user is DEALER_USER role
const isDealerUser = computed(() => {
    return authStore.userRole === 'DEALER_USER';
});

// Show dealer dropdown only for non-DEALER_USER roles
const showDealerDropdown = computed(() => {
    return !isDealerUser.value;
});

// Computed properties for formatted dates
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
    console.log('Refreshing Unit Inbound data...');
};

// Watch for dealers to be loaded and set initial dealer for non-DEALER_USER
watch(dealerOptions, (newDealers) => {
    if (newDealers.length > 0 && !selectedDealer.value && authStore.userRole !== 'DEALER_USER') {
        // Set first dealer as default for non-DEALER_USER roles
        selectedDealer.value = newDealers[0].value;
    }
}, { immediate: true });
</script>

<template>
    <div class="space-y-6">
        <!-- Header with Back Button, Title, Refresh and Filter Controls in One Row -->
        <div class="flex items-center justify-between mb-8">
            <!-- Left Side: Back Button, Title, and Refresh -->
            <div class="flex items-center space-x-4">
                
                <h1 class="text-2xl font-bold text-surface-900 uppercase tracking-wide">
                    UNIT INBOUND
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
                <!-- Dealer Dropdown (only for non-DEALER_USER roles) -->
                <div v-if="showDealerDropdown" class="flex items-center space-x-2">
                    <label class="text-sm font-medium text-surface-700">Dealer:</label>
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

                <!-- Date Range -->
                <div class="flex items-center space-x-2">
                    <Calendar
                        v-model="selectedDateFrom"
                        placeholder="From Date"
                        dateFormat="dd-mm-yy"
                        class="w-36"
                        showIcon
                    />
                    <span class="text-sm text-surface-500">to</span>
                    <Calendar
                        v-model="selectedDateTo"
                        placeholder="To Date"
                        dateFormat="dd-mm-yy"
                        class="w-36"
                        showIcon
                    />
                </div>
            </div>
        </div>

        <!-- Dashboard Content -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Left Column (2 rows) -->
            <div class="space-y-6">
                <!-- Row 1: Unit Inbound Status Widget -->
                <div>
                    <!-- Data Inbound Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
                            Data Inbound
                        </h3>
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <UnitInboundStatusWidget
                            :dealerId="selectedDealer"
                            :dateFrom="formattedDateFrom"
                            :dateTo="formattedDateTo"
                        />
                    </div>
                </div>

                <!-- Row 2: Top 5 Penerimaan Unit Widget -->
                <div>
                    <!-- Top 5 Penerimaan Unit Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
                            Top 5 Penerimaan Unit
                        </h3>
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <Top5PenerimaanUnitWidget
                            :dealerId="selectedDealer"
                            :dateFrom="formattedDateFrom"
                            :dateTo="formattedDateTo"
                        />
                    </div>
                </div>
            </div>

            <!-- Right Column (1 widget) -->
            <div class="h-full flex flex-col">
                <!-- Widget with integrated title and buttons -->
                <div class="flex-1">
                    <UnitInboundDataHistoryWidget
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
/* Component styles */
</style>
