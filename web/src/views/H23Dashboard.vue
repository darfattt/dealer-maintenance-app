<script setup>
import { ref, computed, watch } from 'vue';
import { useDealers } from '@/composables/useDealers';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import Button from 'primevue/button';
import { useAuthStore } from '@/stores/auth';
import { useToast } from 'primevue/usetoast';
import api from '@/service/ApiService';

// Import H23 specific widgets
import TotalUnitEntryWidget from '@/components/dashboard/h23/TotalUnitEntryWidget.vue';
import WorkOrderRevenueWidget from '@/components/dashboard/h23/WorkOrderRevenueWidget.vue';
import WorkOrderStatusWidget from '@/components/dashboard/h23/WorkOrderStatusWidget.vue';
import NJBWidget from '@/components/dashboard/h23/NJBWidget.vue';
import NSCWidget from '@/components/dashboard/h23/NSCWidget.vue';
import HLOWidget from '@/components/dashboard/h23/HLOWidget.vue';

// Auth store and toast
const authStore = useAuthStore();
const toast = useToast();

// Export loading states
const isExportingWorkOrder = ref(false);
const isExportingNJB = ref(false);
const isExportingHLO = ref(false);

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

// Helper function to format date as YYYY-MM-DD without timezone conversion
const formatDateToLocal = (date) => {
    if (!date) return '';
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
};

// Computed properties for formatted dates
const formattedDateFrom = computed(() => {
    return formatDateToLocal(selectedDateFrom.value);
});

const formattedDateTo = computed(() => {
    return formatDateToLocal(selectedDateTo.value);
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

// Excel export functionality
const exportWorkOrderExcel = async () => {
    if (!selectedDealer.value) {
        toast.add({
            severity: 'warn',
            summary: 'Warning',
            detail: 'Please select a dealer first',
            life: 3000
        });
        return;
    }

    if (!formattedDateFrom.value || !formattedDateTo.value) {
        toast.add({
            severity: 'warn',
            summary: 'Warning',
            detail: 'Please select date range first',
            life: 3000
        });
        return;
    }

    isExportingWorkOrder.value = true;

    try {
        const response = await api.get('/v1/h23-dashboard/exports/work-order-excel', {
            params: {
                dealer_id: selectedDealer.value,
                date_from: formattedDateFrom.value,
                date_to: formattedDateTo.value
            },
            responseType: 'blob'
        });

        // Extract filename from Content-Disposition header
        const contentDisposition = response.headers['content-disposition'];
        let filename = 'work-order-export.xlsx';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }

        // Create blob and download
        const blob = new Blob([response.data], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        });

        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Work Order data exported successfully',
            life: 3000
        });
    } catch (error) {
        console.error('Excel export error:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'Failed to export Work Order data',
            life: 5000
        });
    } finally {
        isExportingWorkOrder.value = false;
    }
};

// NJB Excel export functionality
const exportNJBExcel = async () => {
    if (!selectedDealer.value) {
        toast.add({
            severity: 'warn',
            summary: 'Warning',
            detail: 'Please select a dealer first',
            life: 3000
        });
        return;
    }

    if (!formattedDateFrom.value || !formattedDateTo.value) {
        toast.add({
            severity: 'warn',
            summary: 'Warning',
            detail: 'Please select date range first',
            life: 3000
        });
        return;
    }

    isExportingNJB.value = true;

    try {
        const response = await api.get('/v1/h23-dashboard/exports/njb-nsc-excel', {
            params: {
                dealer_id: selectedDealer.value,
                date_from: formattedDateFrom.value,
                date_to: formattedDateTo.value
            },
            responseType: 'blob'
        });

        // Extract filename from Content-Disposition header
        const contentDisposition = response.headers['content-disposition'];
        let filename = 'njb-nsc-export.xlsx';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }

        // Create blob and download
        const blob = new Blob([response.data], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        });

        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'NJB/NSC data exported successfully',
            life: 3000
        });
    } catch (error) {
        console.error('NJB Excel export error:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'Failed to export NJB/NSC data',
            life: 5000
        });
    } finally {
        isExportingNJB.value = false;
    }
};

// HLO Excel export functionality
const exportHLOExcel = async () => {
    if (!selectedDealer.value) {
        toast.add({
            severity: 'warn',
            summary: 'Warning',
            detail: 'Please select a dealer first',
            life: 3000
        });
        return;
    }

    if (!formattedDateFrom.value || !formattedDateTo.value) {
        toast.add({
            severity: 'warn',
            summary: 'Warning',
            detail: 'Please select date range first',
            life: 3000
        });
        return;
    }

    isExportingHLO.value = true;

    try {
        const response = await api.get('/v1/h23-dashboard/exports/hlo-excel', {
            params: {
                dealer_id: selectedDealer.value,
                date_from: formattedDateFrom.value,
                date_to: formattedDateTo.value
            },
            responseType: 'blob'
        });

        // Extract filename from Content-Disposition header
        const contentDisposition = response.headers['content-disposition'];
        let filename = 'hlo-export.xlsx';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }

        // Create blob and download
        const blob = new Blob([response.data], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        });

        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'HLO data exported successfully',
            life: 3000
        });
    } catch (error) {
        console.error('HLO Excel export error:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'Failed to export HLO data',
            life: 5000
        });
    } finally {
        isExportingHLO.value = false;
    }
};
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
                <div class="bg-surface-0 p-4 rounded-lg border border-surface-200 shadow-sm flex justify-between items-center">
                    <h2 class="text-xl font-bold text-surface-900 dark:text-surface-0 uppercase tracking-wide">Work Order</h2>
                    <Button icon="pi pi-file-excel" severity="success" size="small" :loading="isExportingWorkOrder" @click="exportWorkOrderExcel" v-tooltip="'Export to Excel'" class="p-button-outlined" />
                </div>

                <!-- Work Order Row 1: Total Unit Entry & Revenue (2 columns) -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 work-order-row-1">
                    <div>
                        <!-- Total Unit Entry Title -->
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3 class="text-sm font-bold text-surface-900 dark:text-surface-0 uppercase tracking-wide">Total Unit Entry</h3>
                        </div>
                        <!-- Widget -->
                        <div class="widget-with-title">
                            <TotalUnitEntryWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                        </div>
                    </div>

                    <div>
                        <!-- Revenue Title -->
                        <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                            <h3 class="text-sm font-bold text-surface-900 dark:text-surface-0 uppercase tracking-wide">Revenue</h3>
                        </div>
                        <!-- Widget -->
                        <div class="widget-with-title">
                            <WorkOrderRevenueWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                        </div>
                    </div>
                </div>

                <!-- Work Order Row 2: Status Work Order (1 column) -->
                <div class="work-order-row-2">
                    <!-- Status Work Order Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <h3 class="text-sm font-bold text-surface-900 dark:text-surface-0 uppercase tracking-wide">Status Work Order</h3>
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
                    <h2 class="text-xl font-bold text-surface-900 dark:text-surface-0 uppercase tracking-wide">Pembayaran</h2>
                </div>

                <!-- Pembayaran Section 1: NJB (1 row) -->
                <div>
                    <!-- NJB Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200 flex justify-between items-center">
                        <h3 class="text-sm font-bold text-surface-900 dark:text-surface-0 uppercase tracking-wide">Nota Jasa Bengkel</h3>
                        <Button icon="pi pi-file-excel" severity="success" size="small" :loading="isExportingNJB" @click="exportNJBExcel" v-tooltip="'Export to Excel'" class="p-button-outlined" />
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <NJBWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                    </div>
                </div>

                <!-- Pembayaran Section 2: NSC (1 row) -->
                <div>
                    <!-- NSC Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
                        <h3 class="text-sm font-bold text-surface-900 dark:text-surface-0 uppercase tracking-wide">Nota Suku Cadang</h3>
                    </div>
                    <!-- Widget -->
                    <div class="widget-with-title">
                        <NSCWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
                    </div>
                </div>

                <!-- Pembayaran Section 3: HLO (1 row) -->
                <div>
                    <!-- HLO Title -->
                    <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200 flex justify-between items-center">
                        <h3 class="text-sm font-bold text-surface-900 dark:text-surface-0 uppercase tracking-wide">Jumlah HLO</h3>
                        <Button icon="pi pi-file-excel" severity="success" size="small" :loading="isExportingHLO" @click="exportHLOExcel" v-tooltip="'Export to Excel'" class="p-button-outlined" />
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

    /* Reduce minimum heights on mobile for better space usage */
    .work-order-row-1 .widget-with-title :deep(.p-card) {
        min-height: 220px;
    }

    .work-order-row-2 .widget-with-title :deep(.p-card) {
        min-height: 300px;
    }
}

/* Section headers styling */
.bg-surface-0 {
    background-color: var(--surface-0);
}

/* Widget height consistency */
/* Force equal heights for Total Unit Entry & Revenue widgets */
.work-order-row-1 .widget-with-title :deep(.p-card) {
    min-height: 280px;
    display: flex;
    flex-direction: column;
}

.work-order-row-1 .widget-with-title :deep(.p-card-content) {
    display: flex;
    flex-direction: column;
    justify-content: center;
    flex: 1;
}

/* Status Work Order section - accommodate larger chart */
.work-order-row-2 .widget-with-title :deep(.p-card) {
    min-height: 380px;
}

.work-order-row-2 .widget-with-title :deep(.p-card-content) {
    display: flex;
    flex-direction: column;
    flex: 1;
}
</style>
