<script setup>
import { ref, computed } from 'vue';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import { useAuthStore } from '@/stores/auth';
import TopDriverWidget from '@/components/dashboard/TopDriverWidget.vue';
import DeliveryProcessWidget from '@/components/dashboard/DeliveryProcessWidget.vue';
import DeliveryLocationWidget from '@/components/dashboard/DeliveryLocationWidget.vue';
import DeliveryDataHistoryWidget from '@/components/dashboard/DeliveryDataHistoryWidget.vue';

// Auth store
const authStore = useAuthStore();

// Filter controls
const selectedDealer = ref('12284'); // Default dealer
const selectedDateFrom = ref(new Date(new Date().getFullYear(), 0, 1)); // Start of current year
const selectedDateTo = ref(new Date()); // Today

// Dealer options
const dealerOptions = ref([
    { label: 'Sample Dealer (12284)', value: '12284' },
    { label: 'Test Dealer (00999)', value: '00999' }
]);

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
                    placeholder="Select Dealer"
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
                <span class="text-sm text-muted-color">to</span>
                <Calendar
                    v-model="selectedDateTo"
                    dateFormat="dd-mm-yy"
                    placeholder="To Date"
                    class="w-36"
                    showIcon
                />
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
