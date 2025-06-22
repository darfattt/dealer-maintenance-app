<script setup>
import { ref, computed } from 'vue';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import UnitInboundStatusWidget from '@/components/dashboard/UnitInboundStatusWidget.vue';
import StatusSPKWidget from '@/components/dashboard/StatusSPKWidget.vue';
import PaymentTypeWidget from '@/components/dashboard/PaymentTypeWidget.vue';
import DocumentHandlingWidget from '@/components/dashboard/DocumentHandlingWidget.vue';
import StatusProspectWidget from '@/components/dashboard/StatusProspectWidget.vue';
import TopLeasingWidget from '@/components/dashboard/TopLeasingWidget.vue';
import DeliveryProcessWidget from '@/components/dashboard/DeliveryProcessWidget.vue';
// New prospect-related widgets
import StatusProspectBarWidget from '@/components/dashboard/StatusProspectBarWidget.vue';
import MetodeFollowUpWidget from '@/components/dashboard/MetodeFollowUpWidget.vue';
import SumberProspectWidget from '@/components/dashboard/SumberProspectWidget.vue';
import DataHistoryWidget from '@/components/dashboard/DataHistoryWidget.vue';
import SebaranDataWidget from '@/components/dashboard/SebaranDataMapWidget.vue';
import { useAuthStore } from '@/stores/auth';

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

        <!-- Dashboard Widgets Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- Row 1: Top 4 widgets -->
            <div class="lg:col-span-1">
                <UnitInboundStatusWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>

            <div class="lg:col-span-1">
                <StatusSPKWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>

            <div class="lg:col-span-1">
                <PaymentTypeWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>

            <div class="lg:col-span-1">
                <DocumentHandlingWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>
        </div>

        <!-- Row 2: Bottom 3 widgets -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div class="lg:col-span-1">
                <StatusProspectWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>

            <div class="lg:col-span-1">
                <TopLeasingWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
            </div>

            <div class="lg:col-span-1">
                <DeliveryProcessWidget
                    :dealerId="selectedDealer"
                    :dateFrom="formattedDateFrom"
                    :dateTo="formattedDateTo"
                />
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
