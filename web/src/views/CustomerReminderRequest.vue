<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
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
import Button from 'primevue/button';
import Tooltip from 'primevue/tooltip';
import Dialog from 'primevue/dialog';
import CustomerService from '@/service/CustomerService';
import DeliveryStatusChart from '@/components/dashboard/DeliveryStatusChart.vue';
import ReminderTargetChart from '@/components/dashboard/ReminderTargetChart.vue';
import ReminderTypeStatusChart from '@/components/dashboard/ReminderTypeStatusChart.vue';
import Top5TipeUnitWidget from '@/components/dashboard/Top5TipeUnitWidget.vue';
import { formatIndonesiaDate, formatDateForAPI, getCurrentMonthIndonesia, formatIndonesiaTime } from '@/utils/dateFormatter';

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
const selectedReminderTarget = ref('');

// Reminder target options (matching backend reminder_target field values)
const reminderTargetOptions = ref([
    { label: 'All Targets', value: '' },
    { label: 'KPB 1', value: 'KPB-1' },
    { label: 'KPB 2', value: 'KPB-2' },
    { label: 'KPB 3', value: 'KPB-3' },
    { label: 'KPB 4', value: 'KPB-4' },
    { label: 'Non KPB', value: 'Non KPB' },
    { label: 'Booking Service', value: 'Booking Service' },
    { label: 'Ultah Konsumen', value: 'Ultah Konsumen' }
]);

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
    pending_count: 0,
    delivery_percentage: 0,
    reminder_type_breakdown: {},
    reminder_target_breakdown: {}
});

// Table data
const reminders = ref([]);

// Pagination state (matching CustomerSatisfaction.vue pattern)
const pagination = reactive({
    page: 1,
    page_size: 10,
    total_count: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
});

// Dialog state
const showDetailsDialog = ref(false);
const selectedReminder = ref(null);

// Load stats
const loadStats = async () => {
    statsLoading.value = true;
    try {
        const response = await CustomerService.getReminderStats(formattedDateFrom.value, formattedDateTo.value, selectedDealer.value, selectedReminderTarget.value);

        if (response.success && response.data) {
            const data = response.data;
            stats.value = {
                total_requests: data.total_requests || 0,
                delivered_count: data.delivered_count || 0,
                failed_count: data.failed_count || 0,
                pending_count: data.pending_count || 0,
                delivery_percentage: data.delivery_percentage || 0,
                reminder_type_breakdown: data.reminder_type_breakdown || {},
                reminder_target_breakdown: data.reminder_target_breakdown || {}
            };
        }
    } catch (error) {
        console.error('Failed to load reminder stats:', error);
        // Reset stats on error
        stats.value = {
            total_requests: 0,
            delivered_count: 0,
            failed_count: 0,
            pending_count: 0,
            delivery_percentage: 0,
            reminder_type_breakdown: {},
            reminder_target_breakdown: {}
        };
    } finally {
        statsLoading.value = false;
    }
};

// Load reminders table data
const loadReminders = async () => {
    loading.value = true;
    try {
        const response = await CustomerService.getReminderRequests({
            page: pagination.page,
            pageSize: pagination.page_size,
            dateFrom: formattedDateFrom.value,
            dateTo: formattedDateTo.value,
            reminderTarget: selectedReminderTarget.value || null,
            dealerId: selectedDealer.value
        });

        if (response.success && response.data) {
            reminders.value = response.data.items || [];
            // Update pagination state with response data
            const paginationData = response.data;
            pagination.total_count = paginationData.total || 0;
            pagination.total_pages = paginationData.total_pages || 0;
            pagination.has_next = paginationData.has_next || false;
            pagination.has_prev = paginationData.has_prev || false;
        }
    } catch (error) {
        console.error('Failed to load reminders:', error);
        reminders.value = [];
        pagination.total_count = 0;
    } finally {
        loading.value = false;
    }
};

// Handle pagination (both page and page size changes)
const onPageChange = (event) => {
    pagination.page = event.page + 1; // Convert from 0-based to 1-based
    pagination.page_size = event.rows;
    loadReminders();
};

// Get reminder target severity for Tag component (based on reminder_target field)
const getReminderTargetSeverity = (target) => {
    switch (target) {
        case 'KPB 1':
        case 'KPB-1':
            return 'info';
        case 'KPB 2':
        case 'KPB-2':
            return 'success';
        case 'KPB 3':
        case 'KPB-3':
            return 'warning';
        case 'KPB 4':
        case 'KPB-4':
            return 'help';
        case 'Non KPB':
            return 'secondary';
        case 'Booking Service':
            return 'contrast';
        case 'Ultah Konsumen':
            return 'danger';
        default:
            return 'info';
    }
};

// Get reminder target label for display (based on reminder_target field)
const getReminderTargetLabel = (target) => {
    switch (target) {
        case 'KPB 1':
        case 'KPB-1':
            return 'KPB 1';
        case 'KPB 2':
        case 'KPB-2':
            return 'KPB 2';
        case 'KPB 3':
        case 'KPB-3':
            return 'KPB 3';
        case 'KPB 4':
        case 'KPB-4':
            return 'KPB 4';
        case 'Non KPB':
            return 'Non KPB';
        case 'Booking Service':
            return 'Booking Service';
        case 'Ultah Konsumen':
            return 'Ultah Konsumen';
        default:
            return target || 'Unknown';
    }
};

// Get status severity for Tag component
const getStatusSeverity = (status) => {
    switch (status?.toLowerCase()) {
        case 'sent':
            return 'success';
        case 'failed':
        case 'error':
            return 'danger';
        case 'not_sent':
        default:
            return 'secondary';
    }
};

// Get status label for display
const getStatusLabel = (status) => {
    switch (status?.toLowerCase()) {
        case 'sent':
            return 'Terkirim';
        case 'failed':
            return 'Gagal';
        case 'error':
            return 'Error';
        case 'not_sent':
        default:
            return 'Belum Dikirim';
    }
};

// Format date for display (using Indonesia timezone)
const formatDate = (date) => {
    return formatIndonesiaDate(date);
};

// Format time for display
const formatTime = (time) => {
    if (!time) return '';
    return formatIndonesiaTime(time);
};

// Get most common reminder targets for display
/*
const getTopReminderTargets = computed(() => {
    const breakdown = stats.value.reminder_type_breakdown;
    return Object.entries(breakdown)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 3)
        .map(([target, count]) => ({
            type: getReminderTargetLabel(target),
            count
        }));
});
*/

// Handle details dialog
const showReminderDetails = (reminder) => {
    selectedReminder.value = reminder;
    showDetailsDialog.value = true;
};

const closeDetailsDialog = () => {
    showDetailsDialog.value = false;
    selectedReminder.value = null;
};

// Watch for filter changes - includes selectedDealer for SUPER_ADMIN dealer switching
watch(
    [formattedDateFrom, formattedDateTo, selectedReminderTarget, selectedDealer],
    () => {
        pagination.page = 1; // Reset to first page when filters change
        loadStats();
        loadReminders();
    },
    { deep: true }
);

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

// Initial load
onMounted(() => {
    loadStats();
    loadReminders();
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

            <!-- Reminder Target Filter -->
            <div class="flex items-center space-x-2">
                <label for="target-filter" class="text-sm font-medium">Target:</label>
                <Dropdown id="target-filter" v-model="selectedReminderTarget" :options="reminderTargetOptions" optionLabel="label" optionValue="value" placeholder="All Targets" class="w-44" />
            </div>

            <!-- Date Range Filters -->
            <div class="flex items-center space-x-2">
                <Calendar v-model="selectedDateFrom" dateFormat="dd-mm-yy" placeholder="From Date" class="w-36" showIcon />
                <span class="text-sm text-muted-color">to</span>
                <Calendar v-model="selectedDateTo" dateFormat="dd-mm-yy" placeholder="To Date" class="w-36" showIcon />
            </div>
        </div>

        <!-- Overview Section -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Delivery Status Chart -->
            <!-- <DeliveryStatusChart 
                :stats="stats" 
                :loading="statsLoading"
            /> -->

            <!-- Reminder Target Chart -->
            <!-- <ReminderTargetChart 
                :stats="stats" 
                :loading="statsLoading"
            /> -->

            <!-- Reminder Type Status Chart -->
            <ReminderTypeStatusChart :date-from="formattedDateFrom" :date-to="formattedDateTo" :dealer-id="selectedDealer" :reminder-target="selectedReminderTarget" :loading="statsLoading" />

            <!-- Top 5 Vehicle Types Widget -->
            <Top5TipeUnitWidget :date-from="formattedDateFrom" :date-to="formattedDateTo" :dealer-id="selectedDealer" :reminder-target="selectedReminderTarget" />
        </div>

        <!-- Reminder Target Breakdown
        <div v-if="!statsLoading && getTopReminderTargets.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card class="text-center" v-for="item in getTopReminderTargets" :key="item.type">
                <template #content>
                    <h3 class="text-lg font-semibold text-surface-900 mb-2">{{ item.type }}</h3>
                    <div class="text-2xl font-bold text-indigo-600 mb-1">
                        {{ item.count }}
                    </div>
                    <p class="text-sm text-surface-500">Reminders</p>
                </template>
            </Card>
        </div>
         -->

        <!-- Details Table -->
        <Card>
            <template #title>
                <h2 class="text-xl font-bold text-surface-900">Customer Reminder Requests</h2>
            </template>
            <template #content>
                <DataTable :value="reminders" :loading="loading" responsiveLayout="scroll" :paginator="false" class="p-datatable-customers">
                    <Column field="request_date" header="Tanggal Reminder">
                        <template #body="slotProps">
                            {{ formatDate(slotProps.data.request_date) }}
                        </template>
                    </Column>
                    <Column field="request_time" header="Waktu">
                        <template #body="slotProps">
                            {{ formatTime(slotProps.data.request_time) }}
                        </template>
                    </Column>
                    <Column field="nama_pelanggan" header="Nama" />
                    <Column field="nomor_telepon_pelanggan" header="No. Telepon" />
                    <Column field="nomor_polisi" header="No. Polisi" />
                    <!-- <Column field="tipe_unit" header="Unit Type" /> -->
                    <Column field="whatsapp_status" header="Status WhatsApp">
                        <template #body="slotProps">
                            <Tag :value="getStatusLabel(slotProps.data.whatsapp_status)" :severity="getStatusSeverity(slotProps.data.whatsapp_status)" />
                        </template>
                    </Column>
                    <Column field="reminder_target" header="Reminder Target">
                        <template #body="slotProps">
                            <Tag :value="getReminderTargetLabel(slotProps.data.reminder_target)" :severity="getReminderTargetSeverity(slotProps.data.reminder_target)" />
                        </template>
                    </Column>
                    <!-- <Column field="reminder_type" header="Reminder Type" /> -->

                    <Column header="Actions" :exportable="false" class="action-column">
                        <template #body="slotProps">
                            <div class="flex gap-2">
                                <!-- WhatsApp Message Icon with Tooltip -->
                                <Button
                                    v-if="slotProps.data.whatsapp_message"
                                    v-tooltip.top="{ value: slotProps.data.whatsapp_message, fitContent: false }"
                                    icon="pi pi-comment"
                                    class="p-button-rounded p-button-text p-button-sm"
                                    severity="info"
                                    @click.stop
                                />

                                <!-- Details Icon -->
                                <Button icon="pi pi-info-circle" class="p-button-rounded p-button-text p-button-sm" severity="secondary" @click="showReminderDetails(slotProps.data)" />
                            </div>
                        </template>
                    </Column>
                </DataTable>

                <!-- Pagination -->
                <Paginator
                    v-if="pagination.total_count > pagination.page_size"
                    :rows="pagination.page_size"
                    :totalRecords="pagination.total_count"
                    :first="(pagination.page - 1) * pagination.page_size"
                    :rowsPerPageOptions="[10, 20, 50]"
                    @page="onPageChange"
                    class="mt-4"
                />
            </template>
        </Card>

        <!-- Details Dialog -->
        <Dialog v-model:visible="showDetailsDialog" :header="'Reminder Details'" modal :style="{ width: '50vw' }" :breakpoints="{ '960px': '75vw', '641px': '90vw' }">
            <div v-if="selectedReminder" class="space-y-4">
                <!-- Basic Information -->
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="font-medium text-surface-700 dark:text-surface-300">Customer Name:</label>
                        <p class="text-surface-900 dark:text-surface-100">{{ selectedReminder.nama_pelanggan || 'N/A' }}</p>
                    </div>
                    <div>
                        <label class="font-medium text-surface-700 dark:text-surface-300">Phone Number:</label>
                        <p class="text-surface-900 dark:text-surface-100">{{ selectedReminder.nomor_telepon_pelanggan || 'N/A' }}</p>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="font-medium text-surface-700 dark:text-surface-300">Request Date:</label>
                        <p class="text-surface-900 dark:text-surface-100">{{ formatDate(selectedReminder.request_date) }}</p>
                    </div>
                    <div>
                        <label class="font-medium text-surface-700 dark:text-surface-300">Request Time:</label>
                        <p class="text-surface-900 dark:text-surface-100">{{ formatTime(selectedReminder.request_time) }}</p>
                    </div>
                </div>

                <!-- Reminder Information -->
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="font-medium text-surface-700 dark:text-surface-300">Reminder Target:</label>
                        <p class="text-surface-900 dark:text-surface-100">
                            <Tag :value="getReminderTargetLabel(selectedReminder.reminder_target)" :severity="getReminderTargetSeverity(selectedReminder.reminder_target)" />
                        </p>
                    </div>
                    <div>
                        <label class="font-medium text-surface-700 dark:text-surface-300">Reminder Type:</label>
                        <p class="text-surface-900 dark:text-surface-100">{{ selectedReminder.reminder_type || 'N/A' }}</p>
                    </div>
                </div>

                <!-- WhatsApp Status -->
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="font-medium text-surface-700 dark:text-surface-300">WhatsApp Status:</label>
                        <p class="text-surface-900 dark:text-surface-100">
                            <Tag :value="getStatusLabel(selectedReminder.whatsapp_status)" :severity="getStatusSeverity(selectedReminder.whatsapp_status)" />
                        </p>
                    </div>
                    <div>
                        <label class="font-medium text-surface-700 dark:text-surface-300">Request Status:</label>
                        <p class="text-surface-900 dark:text-surface-100">{{ selectedReminder.request_status || 'N/A' }}</p>
                    </div>
                </div>

                <!-- Additional Fields -->
                <div v-if="selectedReminder.nomor_mesin" class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="font-medium text-surface-700 dark:text-surface-300">Engine Number:</label>
                        <p class="text-surface-900 dark:text-surface-100">{{ selectedReminder.nomor_mesin }}</p>
                    </div>
                    <div v-if="selectedReminder.nomor_polisi">
                        <label class="font-medium text-surface-700 dark:text-surface-300">License Plate:</label>
                        <p class="text-surface-900 dark:text-surface-100">{{ selectedReminder.nomor_polisi }}</p>
                    </div>
                </div>

                <div v-if="selectedReminder.tipe_unit" class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="font-medium text-surface-700 dark:text-surface-300">Unit Type:</label>
                        <p class="text-surface-900 dark:text-surface-100">{{ selectedReminder.tipe_unit }}</p>
                    </div>
                    <div v-if="selectedReminder.dealer_id">
                        <label class="font-medium text-surface-700 dark:text-surface-300">Dealer ID:</label>
                        <p class="text-surface-900 dark:text-surface-100">{{ selectedReminder.dealer_id }}</p>
                    </div>
                </div>

                <!-- WhatsApp Message -->
                <div v-if="selectedReminder.whatsapp_message">
                    <label class="font-medium text-surface-700 dark:text-surface-300">WhatsApp Message:</label>
                    <div class="mt-2 p-3 bg-surface-50 dark:bg-surface-800 rounded border border-surface-200 dark:border-surface-600">
                        <p class="text-surface-900 dark:text-surface-100 whitespace-pre-wrap">{{ selectedReminder.whatsapp_message }}</p>
                    </div>
                </div>

                <!-- Timestamps -->
                <div class="grid grid-cols-2 gap-4 pt-4 border-t border-surface-200 dark:border-surface-600">
                    <div>
                        <label class="font-medium text-surface-700 dark:text-surface-300">Created By:</label>
                        <p class="text-surface-900 dark:text-surface-100">{{ selectedReminder.created_by || 'N/A' }}</p>
                        <p class="text-sm text-surface-500 dark:text-surface-400">{{ formatDate(selectedReminder.created_date) }}</p>
                    </div>
                    <div>
                        <label class="font-medium text-surface-700 dark:text-surface-300">Last Modified:</label>
                        <p class="text-surface-900 dark:text-surface-100">{{ selectedReminder.last_modified_by || 'N/A' }}</p>
                        <p class="text-sm text-surface-500 dark:text-surface-400">{{ formatDate(selectedReminder.last_modified_date) }}</p>
                    </div>
                </div>
            </div>

            <template #footer>
                <Button label="Close" @click="closeDetailsDialog" />
            </template>
        </Dialog>
    </div>
</template>

<style scoped>
/* Custom styles for the customer reminder page */

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
    .grid.md\:grid-cols-4 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
    }

    .grid.md\:grid-cols-3 {
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

/* Status tag styling */
:deep(.p-tag) {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
}

/* Action column styling */
:deep(.action-column) {
    width: 120px;
    text-align: center;
}

:deep(.action-column .p-button) {
    margin: 0 0.25rem;
}

/* Dialog styling */
:deep(.p-dialog .p-dialog-content) {
    padding: 1.5rem;
}

:deep(.p-dialog .space-y-4 > * + *) {
    margin-top: 1rem;
}

/* WhatsApp message display */
.whitespace-pre-wrap {
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* Tooltip styling for long messages */
:deep(.p-tooltip .p-tooltip-text) {
    max-width: 300px;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* Filter controls responsive */
@media (max-width: 1024px) {
    .flex.justify-end {
        flex-wrap: wrap;
        gap: 0.5rem;
    }
}
</style>
