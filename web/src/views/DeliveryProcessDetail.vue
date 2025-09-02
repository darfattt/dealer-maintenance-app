<script setup>
import { ref, computed, watch } from 'vue';
import { useDealers } from '@/composables/useDealers';
import { useRouter } from 'vue-router';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import { useAuthStore } from '@/stores/auth';
import TopDriverWidget from '@/components/dashboard/TopDriverWidget.vue';
import DeliveryProcessWidget from '@/components/dashboard/DeliveryProcessWidget.vue';
import DeliveryLocationWidget from '@/components/dashboard/DeliveryLocationWidget.vue';
import DeliveryDataHistoryWidget from '@/components/dashboard/DeliveryDataHistoryWidget.vue';

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
    console.log('Refreshing Delivery Process data...');
};

// Watch for dealers to be loaded and set initial dealer for non-DEALER_USER
watch(dealerOptions, (newDealers) => {
    if (newDealers.length > 0 && !selectedDealer.value && authStore.userRole !== 'DEALER_USER') {
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
                    DELIVERY PROCESS
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
                <div v-if="showDealerDropdown" class="flex items-center space-x-2">
                    <label for="dealer-filter" class="text-sm font-medium text-surface-700">Dealer:</label>
                    <Dropdown
                        id="dealer-filter"
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

        <!-- First Row: 3 Widgets (3 columns) -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <!-- Widget 1: Top Driver (Left) -->
            <div class="lg:col-span-1">
                <TopDriverWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>

            <!-- Widget 2: Delivery Process (Center) -->
            <div class="lg:col-span-1">
                <DeliveryProcessWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                    :showTitle="true"
                />
            </div>

            <!-- Widget 3: Delivery Location (Right) -->
            <div class="lg:col-span-1">
                <DeliveryLocationWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>
        </div>

        <!-- Second Row: 1 Widget (Full width) -->
        <div class="grid grid-cols-1 gap-6">
            <!-- Widget 4: Data History Table -->
            <div class="lg:col-span-1">
                <DeliveryDataHistoryWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Custom spacing for the layout */
.space-y-6 > * + * {
    margin-top: 1.5rem;
}

/* Ensure proper responsive behavior */
@media (max-width: 1024px) {
    .grid.lg\:grid-cols-3 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
    }
}

@media (min-width: 768px) and (max-width: 1024px) {
    .grid.lg\:grid-cols-3 {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
</style>
