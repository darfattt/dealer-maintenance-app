<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import PaymentTypeWidget from '@/components/dashboard/PaymentTypeWidget.vue';
import PaymentMethodWidget from '@/components/dashboard/PaymentMethodWidget.vue';
import PaymentStatusWidget from '@/components/dashboard/PaymentStatusWidget.vue';
import PaymentRevenueWidget from '@/components/dashboard/PaymentRevenueWidget.vue';
import TrenRevenueWidget from '@/components/dashboard/TrenRevenueWidget.vue';
import PaymentDataHistoryWidget from '@/components/dashboard/PaymentDataHistoryWidget.vue';

// Auth store
const authStore = useAuthStore();

// Filter controls
const selectedDealer = ref('12284'); // Default dealer
const selectedDateFrom = ref(new Date(new Date().getFullYear(), 0, 1)); // Start of current year
const selectedDateTo = ref(new Date()); // Today

// Dealer options
const dealerOptions = ref([
    { label: 'All Dealers', value: '' },
    { label: 'Dealer 12284', value: '12284' },
    { label: 'Dealer 12285', value: '12285' },
    { label: 'Dealer 12286', value: '12286' }
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
    <div class="p-6 bg-surface-50 min-h-screen">
        <!-- Header with Filter Controls -->
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex justify-between items-center">
                <h1 class="text-2xl font-bold text-surface-900 uppercase tracking-wide">Payment Type Detail</h1>

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

            <!-- Dashboard Content -->
            <div class="space-y-6">
                <!-- First Row: 4 Columns -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <!-- Column 1: Tipe Pembayaran (Reused Widget) -->
                    <div>
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
                                Tipe Pembayaran
                            </h3>
                        </div>
                        <div class="widget-with-title">
                            <PaymentTypeWidget
                                :dealerId="selectedDealer"
                                :dateFrom="formattedDateFrom"
                                :dateTo="formattedDateTo"
                            />
                        </div>
                    </div>

                    <!-- Column 2: Cara Pembayaran -->
                    <div>
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
                                Cara Pembayaran
                            </h3>
                        </div>
                        <div class="widget-with-title">
                            <PaymentMethodWidget
                                :dealerId="selectedDealer"
                                :dateFrom="formattedDateFrom"
                                :dateTo="formattedDateTo"
                            />
                        </div>
                    </div>

                    <!-- Column 3: Status Pembayaran -->
                    <div>
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
                                Status Pembayaran
                            </h3>
                        </div>
                        <div class="widget-with-title">
                            <PaymentStatusWidget
                                :dealerId="selectedDealer"
                                :dateFrom="formattedDateFrom"
                                :dateTo="formattedDateTo"
                            />
                        </div>
                    </div>

                    <!-- Column 4: Revenue -->
                    <div>
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
                                Revenue
                            </h3>
                        </div>
                        <div class="widget-with-title">
                            <PaymentRevenueWidget
                                :dealerId="selectedDealer"
                                :dateFrom="formattedDateFrom"
                                :dateTo="formattedDateTo"
                            />
                        </div>
                    </div>
                </div>

                <!-- Second Row: 2 Columns -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Column 1: Tren Revenue -->
                    <div>
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
                                Tren Revenue
                            </h3>
                        </div>
                        <div class="widget-with-title">
                            <TrenRevenueWidget
                                :dealerId="selectedDealer"
                                :dateFrom="formattedDateFrom"
                                :dateTo="formattedDateTo"
                            />
                        </div>
                    </div>

                    <!-- Column 2: Data History -->
                    <div class="h-full flex flex-col">
                        <div class="flex-1">
                            <PaymentDataHistoryWidget
                                :dealerId="selectedDealer"
                                :dateFrom="formattedDateFrom"
                                :dateTo="formattedDateTo"
                            />
                        </div>
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
