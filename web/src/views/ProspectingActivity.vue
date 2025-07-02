<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import { useAuthStore } from '@/stores/auth';

// Imported widgets for ProspectingActivity
import StatusProspectBarWidget from '@/components/dashboard/StatusProspectBarWidget.vue';
import MetodeFollowUpWidget from '@/components/dashboard/MetodeFollowUpWidget.vue';
import SumberProspectWidget from '@/components/dashboard/SumberProspectWidget.vue';
import DataHistoryWidget from '@/components/dashboard/DataHistoryWidget.vue';
import SebaranDataWidget from '@/components/dashboard/SebaranDataMapWidget.vue';

// Router and Auth store
const router = useRouter();
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

// Navigation methods
const goBack = () => {
    router.push('/dashboard');
};

const refreshData = () => {
    // Refresh logic here
    console.log('Refreshing Prospecting Activity data...');
};
</script>

<template>
    <div class="space-y-6">
        <!-- Header with Back Button, Title, Refresh and Filter Controls in One Row -->
        <div class="flex items-center justify-between mb-8">
            <!-- Left Side: Back Button, Title, and Refresh -->
            <div class="flex items-center space-x-4">
                <Button
                    icon="pi pi-arrow-left"
                    text
                    @click="goBack"
                    class="text-surface-600 hover:text-surface-900"
                    v-tooltip.top="'Back to Dashboard'"
                />
                <h1 class="text-2xl font-bold text-surface-900 uppercase tracking-wide">
                    PROSPECTING ACTIVITY
                </h1>
                <Button
                    icon="pi pi-refresh"
                    text
                    @click="refreshData"
                    class="text-surface-600 hover:text-surface-900"
                    v-tooltip.top="'Refresh Data'"
                />
            </div>

            <!-- Right Side: Filter Controls -->
            <div class="flex items-center space-x-4">
                <!-- Dealer Selection (only for non-DEALER_USER) -->
                <div v-if="showDealerDropdown" class="flex items-center space-x-2">
                    <label for="dealer-filter" class="text-sm font-medium text-surface-700">Dealer:</label>
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

        <!-- Row 3: New Prospect Analysis Widgets -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div class="lg:col-span-1">
                <StatusProspectBarWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>

            <div class="lg:col-span-1">
                <MetodeFollowUpWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>

            <div class="lg:col-span-1">
                <SumberProspectWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>
        </div>

        <!-- Row 4: Data History and Map -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="lg:col-span-1">
                <DataHistoryWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>

            <div class="lg:col-span-1">
                <SebaranDataWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>
        </div>
    </div>
</template>
