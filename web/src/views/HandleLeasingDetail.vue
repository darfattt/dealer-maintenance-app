<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';

// Import widgets
import TopLeasingWidget from '@/components/dashboard/TopLeasingWidget.vue';
import POCreationWidget from '@/components/dashboard/POCreationWidget.vue';
import PODocumentStatusWidget from '@/components/dashboard/PODocumentStatusWidget.vue';
import LeasingDataHistoryWidget from '@/components/dashboard/LeasingDataHistoryWidget.vue';

// Auth store
const authStore = useAuthStore();

// Filter controls
const selectedDealer = ref('12284'); // Default dealer
const selectedDateFrom = ref(new Date(new Date().getFullYear(), 0, 1)); // Start of current year
const selectedDateTo = ref(new Date()); // Today

// Dealer options (mock data - replace with real API call)
const dealerOptions = ref([
    { label: 'All Dealers', value: '' },
    { label: 'Dealer A', value: '12284' },
    { label: 'Dealer B', value: '12285' },
    { label: 'Dealer C', value: '12286' }
]);

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

// Lifecycle
onMounted(() => {
    // Initialize any required data
});
</script>

<template>
    <div class="p-6 bg-surface-50 min-h-screen">
        <!-- Header with Filter Controls -->
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex justify-between items-center">
                <h1 class="text-2xl font-bold text-surface-900 uppercase tracking-wide">Handle Leasing</h1>
                
                <!-- Filter Controls -->
                <div class="flex items-center space-x-4">
                    <!-- Dealer Dropdown (only for non-DEALER_USER roles) -->
                    <div v-if="showDealerDropdown" class="flex items-center space-x-2">
                        <label class="text-sm font-medium text-surface-700">Dealer:</label>
                        <Dropdown
                            v-model="selectedDealer"
                            :options="dealerOptions"
                            optionLabel="label"
                            optionValue="value"
                            placeholder="Select Dealer"
                            class="w-40"
                        />
                    </div>

                    <!-- Date Range -->
                    <div class="flex items-center space-x-2">
                        <Calendar
                            v-model="selectedDateFrom"
                            placeholder="From Date"
                            dateFormat="dd-mm-yy"
                            class="w-32"
                            :showIcon="true"
                        />
                        <span class="text-surface-600">s/d</span>
                        <Calendar
                            v-model="selectedDateTo"
                            placeholder="To Date"
                            dateFormat="dd-mm-yy"
                            class="w-32"
                            :showIcon="true"
                        />
                    </div>
                </div>
            </div>

            <!-- First Row - 2 Columns -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- First Column: Reused TopLeasingWidget -->
                <div>
                    <!-- Top 5 Leasing Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
                            Top 5 Leasing
                        </h3>
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <TopLeasingWidget
                            :dealerId="selectedDealer"
                            :dateFrom="formattedDateFrom"
                            :dateTo="formattedDateTo"
                        />
                    </div>
                </div>

                <!-- Second Column: PO Creation Widget -->
                <div>
                    <!-- PO Creation Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
                            Pembuatan PO
                        </h3>
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <POCreationWidget
                            :dealerId="selectedDealer"
                            :dateFrom="formattedDateFrom"
                            :dateTo="formattedDateTo"
                        />
                    </div>
                </div>
            </div>

            <!-- Second Row - 2 Columns -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- First Column: PO Document Status Widget -->
                <div>
                    <!-- PO Document Status Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
                            Status Dokumen PO
                        </h3>
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <PODocumentStatusWidget
                            :dealerId="selectedDealer"
                            :dateFrom="formattedDateFrom"
                            :dateTo="formattedDateTo"
                        />
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
                        <LeasingDataHistoryWidget
                            :dealerId="selectedDealer"
                            :dateFrom="formattedDateFrom"
                            :dateTo="formattedDateTo"
                        />
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
