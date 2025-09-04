<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useDealers } from '@/composables/useDealers';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Paginator from 'primevue/paginator';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';
import CustomerService from '@/service/CustomerService';
import { formatIndonesiaDate, formatIndonesiaTime, formatDateForAPI, getCurrentMonthIndonesia } from '@/utils/dateFormatter';

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
// Use Indonesia timezone for date initialization
const { firstDay: currentYearFirstDay } = getCurrentMonthIndonesia();
const currentYearStart = new Date(currentYearFirstDay.getFullYear(), 0, 1);
const selectedDateFrom = ref(currentYearStart);
const selectedDateTo = ref(new Date());

// Check if user is DEALER_USER role
const isDealerUser = computed(() => {
    return authStore.userRole === 'DEALER_USER';
});

// Show dealer dropdown only for non-DEALER_USER roles
const showDealerDropdown = computed(() => {
    return !isDealerUser.value;
});

// Computed properties for formatted dates (using Indonesia timezone)
const formattedDateFrom = computed(() => {
    return formatDateForAPI(selectedDateFrom.value);
});

const formattedDateTo = computed(() => {
    return formatDateForAPI(selectedDateTo.value);
});

// Data states
const loading = ref(false);
const statsLoading = ref(false);
const stats = ref({
    total_requests: 0,
    delivered_count: 0,
    failed_count: 0,
    delivery_percentage: 0
});

// Table data
const requests = ref([]);
const totalRecords = ref(0);
const currentPage = ref(0);
const pageSize = ref(10);

// Load stats
const loadStats = async () => {
    if (!selectedDealer.value) return;

    statsLoading.value = true;
    try {
        const response = await CustomerService.getCustomerStats(selectedDealer.value, formattedDateFrom.value, formattedDateTo.value);

        if (response.success && response.data) {
            const data = response.data;
            stats.value = {
                total_requests: data.total_requests || 0,
                delivered_count: data.delivered_count || 0,
                failed_count: data.failed_count || 0,
                delivery_percentage: data.delivery_percentage || 0
            };
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
        // Reset stats on error
        stats.value = {
            total_requests: 0,
            delivered_count: 0,
            failed_count: 0,
            delivery_percentage: 0
        };
    } finally {
        statsLoading.value = false;
    }
};

// Load requests table data
const loadRequests = async (page = 0) => {
    if (!selectedDealer.value) return;

    loading.value = true;
    try {
        const response = await CustomerService.getCustomerRequests(selectedDealer.value, {
            page: page + 1, // Convert from 0-based to 1-based
            pageSize: pageSize.value,
            dateFrom: formattedDateFrom.value,
            dateTo: formattedDateTo.value
        });

        if (response.success && response.data) {
            requests.value = response.data.items || [];
            totalRecords.value = response.data.total || 0;
            currentPage.value = page;
        }
    } catch (error) {
        console.error('Failed to load requests:', error);
        requests.value = [];
        totalRecords.value = 0;
    } finally {
        loading.value = false;
    }
};

// Handle pagination
const onPageChange = (event) => {
    // Update page size if it changed
    if (event.rows && event.rows !== pageSize.value) {
        pageSize.value = event.rows;
        // Reset to first page when page size changes
        loadRequests(0);
    } else {
        loadRequests(event.page);
    }
};

// Get status severity for Tag component
const getStatusSeverity = (status) => {
    switch (status?.toLowerCase()) {
        case 'delivered':
            return 'success';
        case 'failed':
            return 'danger';
        case 'sent':
            return 'warning';
        case 'not_sent':
        default:
            return 'secondary';
    }
};

// Get status label for display
const getStatusLabel = (status) => {
    switch (status?.toLowerCase()) {
        case 'delivered':
            return 'Terkirim';
        case 'failed':
            return 'Gagal';
        case 'sent':
            return 'Dikirim';
        case 'not_sent':
        default:
            return 'Belum Dikirim';
    }
};

// Format date for display (using Indonesia timezone)
const formatDate = (date) => {
    return formatIndonesiaDate(date);
};

// Format time for display (using Indonesia timezone)
const formatTime = (time) => {
    return formatIndonesiaTime(time);
};

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

// Watch for filter changes
watch(
    [selectedDealer, formattedDateFrom, formattedDateTo],
    () => {
        loadStats();
        loadRequests(0);
    },
    { deep: true }
);

// Initial load
onMounted(() => {
    loadStats();
    loadRequests(0);
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

        <!-- Overview Section -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Terkirim Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="statsLoading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100 mb-2">Terkirim</h3>
                        <div class="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">{{ stats.delivered_count }}/{{ stats.total_requests }}</div>
                        <p class="text-sm text-surface-500 dark:text-surface-400">WhatsApp Messages</p>
                    </div>
                </template>
            </Card>

            <!-- Tidak Terkirim Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="statsLoading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100 mb-2">Tidak Terkirim</h3>
                        <div class="text-3xl font-bold text-red-600 dark:text-red-400 mb-1">{{ stats.failed_count }}/{{ stats.total_requests }}</div>
                        <p class="text-sm text-surface-500 dark:text-surface-400">WhatsApp Messages</p>
                    </div>
                </template>
            </Card>

            <!-- Summary Percentage Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="statsLoading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100 mb-2">Summary Data terkirim</h3>
                        <div class="text-3xl font-bold text-primary-600 dark:text-primary-400 mb-1">{{ stats.delivery_percentage }}%</div>
                        <p class="text-sm text-surface-500 dark:text-surface-400">Success Rate</p>
                    </div>
                </template>
            </Card>
        </div>

        <!-- Details Table -->
        <Card>
            <template #title>
                <h2 class="text-xl font-bold text-surface-900 dark:text-surface-100">Customer Validation Requests</h2>
            </template>
            <template #content>
                <DataTable :value="requests" :loading="loading" responsiveLayout="scroll" :paginator="false" class="p-datatable-customers">
                    <Column field="request_date" header="Request Date">
                        <template #body="slotProps">
                            {{ formatDate(slotProps.data.request_date) }}
                        </template>
                    </Column>
                    <Column field="request_time" header="Request Time">
                        <template #body="slotProps">
                            {{ formatTime(slotProps.data.request_time) }}
                        </template>
                    </Column>
                    <Column field="nama_pembawa" header="Nama Pembawa" />
                    <Column field="nomor_telepon_pembawa" header="No. Telepon" />
                    <Column field="nomor_polisi" header="No. Polisi" />
                    <Column v-if="!isDealerUser" field="kode_ahass" header="Kode AHASS" />
                    <Column v-if="!isDealerUser" field="nama_ahass" header="Nama AHASS" />
                    <Column v-if="!isDealerUser" field="alamat_ahass" header="Alamat AHASS" style="max-width: 200px">
                        <template #body="slotProps">
                            <div class="text-ellipsis overflow-hidden whitespace-nowrap" :title="slotProps.data.alamat_ahass">
                                {{ slotProps.data.alamat_ahass }}
                            </div>
                        </template>
                    </Column>
                    <Column field="nomor_mesin" header="Nomor Mesin" />
                    <Column field="whatsapp_status" header="Status WhatsApp">
                        <template #body="slotProps">
                            <Tag :value="getStatusLabel(slotProps.data.whatsapp_status)" :severity="getStatusSeverity(slotProps.data.whatsapp_status)" />
                        </template>
                    </Column>
                </DataTable>

                <!-- Pagination -->
                <Paginator v-if="totalRecords > pageSize" :first="currentPage * pageSize" :rows="pageSize" :totalRecords="totalRecords" :rowsPerPageOptions="[10, 20, 50]" @page="onPageChange" class="mt-4" />
            </template>
        </Card>
    </div>
</template>

<style scoped>
/* Custom styles for the customer validation page */

/* Section spacing */
.space-y-6 > * + * {
    margin-top: 1.5rem;
}

/* Card hover effects */
:deep(.p-card) {
    transition: box-shadow 0.2s ease;
}

:deep(.p-card:hover) {
    box-shadow: 0 4px 25px 0 rgba(0, 0, 0, 0.1);
}

/* Responsive grid adjustments */
@media (max-width: 768px) {
    .grid.md\\:grid-cols-3 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
    }
}

/* Table responsive styling */
:deep(.p-datatable-customers .p-datatable-tbody > tr > td) {
    padding: 0.75rem 1rem;
}

:deep(.p-datatable-customers .p-datatable-thead > tr > th) {
    background-color: var(--surface-50);
    font-weight: 600;
}

/* Responsive table for AHASS fields */
@media (max-width: 1024px) {
    :deep(.p-datatable-customers) {
        font-size: 0.875rem;
    }

    :deep(.p-datatable-customers .p-datatable-tbody > tr > td) {
        padding: 0.5rem 0.75rem;
    }
}

/* Status tag styling */
:deep(.p-tag) {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
}
</style>
