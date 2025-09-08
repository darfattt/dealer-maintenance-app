<script setup>
import { ref, computed, watch } from 'vue';
import { useDealers } from '@/composables/useDealers';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import { useAuthStore } from '@/stores/auth';

// Import H23 specific widgets
import TotalUnitEntryWidget from '@/components/dashboard/h23/TotalUnitEntryWidget.vue';
import WorkOrderRevenueWidget from '@/components/dashboard/h23/WorkOrderRevenueWidget.vue';
import WorkOrderStatusWidget from '@/components/dashboard/h23/WorkOrderStatusWidget.vue';
import NJBWidget from '@/components/dashboard/h23/NJBWidget.vue';
import NSCWidget from '@/components/dashboard/h23/NSCWidget.vue';
import HLOWidget from '@/components/dashboard/h23/HLOWidget.vue';

// Auth store
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

// Watch for dealers to be loaded and set initial dealer for non-DEALER_USER
watch(
    dealerOptions,
    (newDealers) => {
        if (newDealers.length > 0 && !selectedDealer.value && authStore.userRole !== 'DEALER_USER') {
            // Set first dealer as default for non-DEALER_USER roles
            selectedDealer.value = newDealers[0].value;
        }
    },
    { immediate: true }
);
</script>

<template>
    <div class="space-y-6">
        <!-- Filter Controls -->
        <div class="flex justify-end items-center space-x-4 mb-6">
            <!-- Dealer Selection (only for non-DEALER_USER) -->
            <div v-if="showDealerDropdown" class="flex items-center space-x-2">
                <label for="dealer-filter" class="text-sm font-medium">Dealer:</label>
                <Dropdown
                    id="dealer-filter"
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

            <!-- Date Range Filters -->
            <div class="flex items-center space-x-2">
                <Calendar v-model="selectedDateFrom" dateFormat="dd-mm-yy" placeholder="From Date" class="w-36" showIcon />
                <span class="text-sm text-muted-color">to</span>
                <Calendar v-model="selectedDateTo" dateFormat="dd-mm-yy" placeholder="To Date" class="w-36" showIcon />
            </div>
        </div>

        <!-- Dashboard Main Layout: 2 Columns -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- 1st Column: Work Order Section -->
            <div class="space-y-6">
                <!-- Work Order Section Header -->
                <div class="bg-surface-0 p-4 rounded-lg border border-surface-200 shadow-sm">
                    <h2 class="text-xl font-bold text-surface-900 uppercase tracking-wide">Work Order</h2>
                </div>

                <!-- Work Order Row 1: Total Unit Entry & Revenue (2 columns) -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <!-- Total Unit Entry Title -->
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">Total Unit Entry</h3>
                        </div>
                        <!-- Widget -->
                        <div class="widget-with-title">
                            <TotalUnitEntryWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                        </div>
                    </div>

                    <div>
                        <!-- Revenue Title -->
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">Revenue</h3>
                        </div>
                        <!-- Widget -->
                        <div class="widget-with-title">
                            <WorkOrderRevenueWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                        </div>
                    </div>
                </div>

                <!-- Work Order Row 2: Status Work Order (1 column) -->
                <div>
                    <!-- Status Work Order Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">Status Work Order</h3>
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <WorkOrderStatusWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                    </div>
                </div>
            </div>

            <!-- 2nd Column: Pembayaran Section -->
            <div class="space-y-6">
                <!-- Pembayaran Section Header -->
                <div class="bg-surface-0 p-4 rounded-lg border border-surface-200 shadow-sm">
                    <h2 class="text-xl font-bold text-surface-900 uppercase tracking-wide">Pembayaran</h2>
                </div>

                <!-- Pembayaran Section 1: NJB & NSC (2 columns) -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <!-- NJB Title -->
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">Nota Jasa Bengkel</h3>
                        </div>
                        <!-- Widget -->
                        <div class="widget-with-title">
                            <NJBWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                        </div>
                    </div>

                    <div>
                        <!-- NSC Title -->
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">Nota Suku Cadang</h3>
                        </div>
                        <!-- Widget -->
                        <div class="widget-with-title">
                            <NSCWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                        </div>
                    </div>
                </div>

                <!-- Pembayaran Section 2: HLO (1 column) -->
                <div>
                    <!-- HLO Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">Jumlah HLO</h3>
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <HLOWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Custom styles for the H23 dashboard */

/* Widget with title styling */
.widget-with-title :deep(.p-card) {
    border-top-left-radius: 0;
    border-top-right-radius: 0;
    border-top: none;
}

/* Section spacing */
.space-y-6 > * + * {
    margin-top: 1.5rem;
}

/* Responsive grid adjustments */
@media (max-width: 1024px) {
    .grid.lg\:grid-cols-2 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
    }
}

@media (max-width: 768px) {
    .grid.md\:grid-cols-2 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
    }
}

/* Section headers styling */
.bg-surface-0 {
    background-color: var(--surface-0);
}
</style>