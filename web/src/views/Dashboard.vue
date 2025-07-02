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
import { useRouter } from 'vue-router';

const router = useRouter();

const navigateToProspectingActivity = () => {
    router.push('/prospecting-activity');
};

const navigateToDealingProcess = () => {
    router.push('/dealing-process');
};

const navigateToDeliveryProcessDetail = () => {
    router.push('/delivery-process-detail');
};

const navigateToUnitInboundDetail = () => {
    router.push('/unit-inbound-detail');
};

const navigateToPaymentTypeDetail = () => {
    router.push('/payment-type-detail');
};

const navigateToHandleLeasingDetail = () => {
    router.push('/handle-leasing-detail');
};

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

        <!-- Dashboard Main Layout: 2 Columns -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">

            <!-- 1st Column: Sales Section -->
            <div class="space-y-6">
                <!-- Sales Section Header -->
                <div class="bg-surface-0 p-4 rounded-lg border border-surface-200 shadow-sm">
                    <h2 class="text-xl font-bold text-surface-900 uppercase tracking-wide">Sales</h2>
                </div>

                <!-- Sales Row 1: Status Prospect & Status SPK (2 columns) -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <!-- Status Prospect Title -->
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3
                                class="text-sm font-bold text-surface-900 uppercase tracking-wide hover:text-primary-600 transition-colors cursor-pointer"
                                @click="navigateToProspectingActivity"
                            >
                                Status Prospect
                            </h3>
                        </div>
                        <!-- Widget -->
                        <div class="widget-with-title">
                            <StatusProspectWidget
                                :dealerId="selectedDealer"
                                :dateFrom="formattedDateFrom"
                                :dateTo="formattedDateTo"
                            />
                        </div>
                    </div>

                    <div>
                        <!-- Status SPK Title -->
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3
                                class="text-sm font-bold text-surface-900 uppercase tracking-wide hover:text-primary-600 transition-colors cursor-pointer"
                                @click="navigateToDealingProcess"
                            >
                                Status SPK
                            </h3>
                        </div>
                        <!-- Widget -->
                        <div class="widget-with-title">
                            <StatusSPKWidget
                                :dealerId="selectedDealer"
                                :dateFrom="formattedDateFrom"
                                :dateTo="formattedDateTo"
                            />
                        </div>
                    </div>
                </div>

                <!-- Sales Row 2: Payment Type, Top Leasing, Document Handling (3 columns) -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <!-- Payment Type Title -->
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200 cursor-pointer hover:bg-surface-50 transition-colors duration-200" @click="navigateToPaymentTypeDetail">
                            <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
                                Tipe Pembayaran
                            </h3>
                        </div>
                        <!-- Widget -->
                        <div class="widget-with-title">
                            <PaymentTypeWidget
                                :dealerId="selectedDealer"
                                :dateFrom="formattedDateFrom"
                                :dateTo="formattedDateTo"
                            />
                        </div>
                    </div>

                    <div>
                        <!-- Top Leasing Title -->
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200 cursor-pointer hover:bg-surface-50 transition-colors duration-200"
                             @click="navigateToHandleLeasingDetail">
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

                    <div>
                        <!-- Document Handling Title -->
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
                                Document Handling
                            </h3>
                        </div>
                        <!-- Widget -->
                        <div class="widget-with-title">
                            <DocumentHandlingWidget
                                :dealerId="selectedDealer"
                                :dateFrom="formattedDateFrom"
                                :dateTo="formattedDateTo"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2nd Column: Inventory Section -->
            <div class="space-y-6">
                <!-- Inventory Section Header -->
                <div class="bg-surface-0 p-4 rounded-lg border border-surface-200 shadow-sm">
                    <h2 class="text-xl font-bold text-surface-900 uppercase tracking-wide">Inventory</h2>
                </div>

                <!-- Inventory Row 1: Unit Inbound Status (1 column) -->
                <div>
                    <!-- Data Inbound Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200 cursor-pointer hover:bg-surface-50 transition-colors duration-200" @click="navigateToUnitInboundDetail">
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

                <!-- Inventory Row 2: Delivery Process (1 column) -->
                <div>
                    <!-- Delivery Process Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <h3
                            class="text-sm font-bold text-surface-900 uppercase tracking-wide hover:text-primary-600 transition-colors cursor-pointer"
                            @click="navigateToDeliveryProcessDetail"
                        >
                            Delivery Process
                        </h3>
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <DeliveryProcessWidget
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
/* Custom styles for the dashboard */

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

    .grid.md\:grid-cols-3 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
    }
}

/* Section headers styling */
.bg-surface-0 {
    background-color: var(--surface-0);
}
</style>
