<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Paginator from 'primevue/paginator';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';
import CustomerService from '@/service/CustomerService';

const authStore = useAuthStore();

// Filter controls - Use dealer from auth for DEALER_USER
const selectedDealer = ref(authStore.userRole === 'DEALER_USER' ? authStore.userDealerId : '12284');
const selectedDateFrom = ref(new Date(new Date().getFullYear(), 0, 1));
const selectedDateTo = ref(new Date());
const selectedReminderType = ref('');

// Dealer options
const dealerOptions = ref([
    { label: 'Sample Dealer (12284)', value: '12284' },
    { label: 'Test Dealer (00999)', value: '00999' }
]);

// Reminder type options
const reminderTypeOptions = ref([
    { label: 'All Types', value: '' },
    { label: 'Service Reminder', value: 'SERVICE_REMINDER' },
    { label: 'Payment Reminder', value: 'PAYMENT_REMINDER' },
    { label: 'Appointment Reminder', value: 'APPOINTMENT_REMINDER' },
    { label: 'Maintenance Reminder', value: 'MAINTENANCE_REMINDER' },
    { label: 'Follow Up Reminder', value: 'FOLLOW_UP_REMINDER' },
    { label: 'Custom Reminder', value: 'CUSTOM_REMINDER' }
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

// Data states
const loading = ref(false);
const statsLoading = ref(false);
const stats = ref({
    total_requests: 0,
    delivered_count: 0,
    failed_count: 0,
    pending_count: 0,
    delivery_percentage: 0,
    reminder_type_breakdown: {}
});

// Table data
const reminders = ref([]);
const totalRecords = ref(0);
const currentPage = ref(0);
const pageSize = ref(10);

// Load stats
const loadStats = async () => {
    statsLoading.value = true;
    try {
        const response = await CustomerService.getReminderStats(
            formattedDateFrom.value,
            formattedDateTo.value
        );
        
        if (response.success && response.data) {
            const data = response.data;
            stats.value = {
                total_requests: data.total_requests || 0,
                delivered_count: data.delivered_count || 0,
                failed_count: data.failed_count || 0,
                pending_count: data.pending_count || 0,
                delivery_percentage: data.delivery_percentage || 0,
                reminder_type_breakdown: data.reminder_type_breakdown || {}
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
            reminder_type_breakdown: {}
        };
    } finally {
        statsLoading.value = false;
    }
};

// Load reminders table data
const loadReminders = async (page = 0) => {
    loading.value = true;
    try {
        const response = await CustomerService.getReminderRequests({
            page: page + 1, // Convert from 0-based to 1-based
            pageSize: pageSize.value,
            dateFrom: formattedDateFrom.value,
            dateTo: formattedDateTo.value,
            reminderType: selectedReminderType.value || null
        });
        
        if (response.success && response.data) {
            reminders.value = response.data.items || [];
            totalRecords.value = response.data.total || 0;
            currentPage.value = page;
        }
    } catch (error) {
        console.error('Failed to load reminders:', error);
        reminders.value = [];
        totalRecords.value = 0;
    } finally {
        loading.value = false;
    }
};

// Handle pagination
const onPageChange = (event) => {
    loadReminders(event.page);
};

// Get reminder type severity for Tag component
const getReminderTypeSeverity = (type) => {
    switch (type) {
        case 'SERVICE_REMINDER':
            return 'info';
        case 'PAYMENT_REMINDER':
            return 'warning';
        case 'APPOINTMENT_REMINDER':
            return 'secondary';
        case 'MAINTENANCE_REMINDER':
            return 'success';
        case 'FOLLOW_UP_REMINDER':
            return 'help';
        case 'CUSTOM_REMINDER':
        default:
            return 'contrast';
    }
};

// Get reminder type label for display
const getReminderTypeLabel = (type) => {
    switch (type) {
        case 'SERVICE_REMINDER':
            return 'Service';
        case 'PAYMENT_REMINDER':
            return 'Payment';
        case 'APPOINTMENT_REMINDER':
            return 'Appointment';
        case 'MAINTENANCE_REMINDER':
            return 'Maintenance';
        case 'FOLLOW_UP_REMINDER':
            return 'Follow Up';
        case 'CUSTOM_REMINDER':
            return 'Custom';
        default:
            return 'Unknown';
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

// Format date for display
const formatDate = (date) => {
    if (!date) return '';
    return new Date(date).toLocaleDateString('id-ID');
};

// Format time for display
const formatTime = (time) => {
    if (!time) return '';
    return time;
};

// Get most common reminder types for display
const getTopReminderTypes = computed(() => {
    const breakdown = stats.value.reminder_type_breakdown;
    return Object.entries(breakdown)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 3)
        .map(([type, count]) => ({
            type: getReminderTypeLabel(type),
            count
        }));
});

// Watch for filter changes - removed selectedDealer since we use authenticated dealer
watch([formattedDateFrom, formattedDateTo, selectedReminderType], () => {
    loadStats();
    loadReminders(0);
}, { deep: true });

// Initial load
onMounted(() => {
    loadStats();
    loadReminders(0);
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

            <!-- Reminder Type Filter -->
            <div class="flex items-center space-x-2">
                <label for="type-filter" class="text-sm font-medium">Type:</label>
                <Dropdown
                    id="type-filter"
                    v-model="selectedReminderType"
                    :options="reminderTypeOptions"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="All Types"
                    class="w-44"
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

        <!-- Overview Section -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <!-- Total Reminders Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="statsLoading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px;" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 mb-2">Total Reminders</h3>
                        <div class="text-3xl font-bold text-blue-600 mb-1">
                            {{ stats.total_requests }}
                        </div>
                        <p class="text-sm text-surface-500">All Reminders</p>
                    </div>
                </template>
            </Card>

            <!-- Terkirim Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="statsLoading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px;" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 mb-2">Terkirim</h3>
                        <div class="text-3xl font-bold text-green-600 mb-1">
                            {{ stats.delivered_count }}
                        </div>
                        <p class="text-sm text-surface-500">Successfully Sent</p>
                    </div>
                </template>
            </Card>

            <!-- Tidak Terkirim Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="statsLoading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px;" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 mb-2">Tidak Terkirim</h3>
                        <div class="text-3xl font-bold text-red-600 mb-1">
                            {{ stats.failed_count }}
                        </div>
                        <p class="text-sm text-surface-500">Failed to Send</p>
                    </div>
                </template>
            </Card>

            <!-- Success Rate Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="statsLoading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px;" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 mb-2">Success Rate</h3>
                        <div class="text-3xl font-bold text-primary-600 mb-1">
                            {{ stats.delivery_percentage }}%
                        </div>
                        <p class="text-sm text-surface-500">Delivery Rate</p>
                    </div>
                </template>
            </Card>
        </div>

        <!-- Reminder Type Breakdown -->
        <div v-if="!statsLoading && getTopReminderTypes.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card class="text-center" v-for="item in getTopReminderTypes" :key="item.type">
                <template #content>
                    <h3 class="text-lg font-semibold text-surface-900 mb-2">{{ item.type }}</h3>
                    <div class="text-2xl font-bold text-indigo-600 mb-1">
                        {{ item.count }}
                    </div>
                    <p class="text-sm text-surface-500">Reminders</p>
                </template>
            </Card>
        </div>

        <!-- Details Table -->
        <Card>
            <template #title>
                <h2 class="text-xl font-bold text-surface-900">Customer Reminder Requests</h2>
            </template>
            <template #content>
                <DataTable
                    :value="reminders"
                    :loading="loading"
                    responsiveLayout="scroll"
                    :paginator="false"
                    class="p-datatable-customers"
                >
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
                    <Column field="customer_name" header="Customer Name" />
                    <Column field="no_telp" header="No. Telepon" />
                    <Column field="reminder_type" header="Reminder Type">
                        <template #body="slotProps">
                            <Tag 
                                :value="getReminderTypeLabel(slotProps.data.reminder_type)" 
                                :severity="getReminderTypeSeverity(slotProps.data.reminder_type)"
                            />
                        </template>
                    </Column>
                    <Column field="whatsapp_status" header="Status WhatsApp">
                        <template #body="slotProps">
                            <Tag 
                                :value="getStatusLabel(slotProps.data.whatsapp_status)" 
                                :severity="getStatusSeverity(slotProps.data.whatsapp_status)"
                            />
                        </template>
                    </Column>
                    <Column field="created_date" header="Created Date">
                        <template #body="slotProps">
                            {{ formatDate(slotProps.data.created_date) }}
                        </template>
                    </Column>
                </DataTable>

                <!-- Pagination -->
                <Paginator
                    v-if="totalRecords > pageSize"
                    :rows="pageSize"
                    :totalRecords="totalRecords"
                    :rowsPerPageOptions="[10, 20, 50]"
                    @page="onPageChange"
                    class="mt-4"
                />
            </template>
        </Card>
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

/* Filter controls responsive */
@media (max-width: 1024px) {
    .flex.justify-end {
        flex-wrap: wrap;
        gap: 0.5rem;
    }
}
</style>