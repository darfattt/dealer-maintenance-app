<template>
    <div class="whatsapp-anomalies">
        <ProgressSpinner v-if="loadingSummary" class="flex justify-center my-8" />

        <!-- Summary Charts Grid -->
        <div v-else-if="summaryData" class="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
            <!-- Total Failed Breakdown -->
            <Card>
                <template #title>
                    <span class="text-sm font-semibold">Total Failed</span>
                </template>
                <template #content>
                    <div class="flex flex-col items-center">
                        <span class="text-3xl font-bold text-red-600">{{ summaryData.total_failed }}</span>
                        <span class="text-xs text-gray-500 mt-1">Failure Rate: {{ summaryData.failure_rate }}%</span>
                    </div>
                </template>
            </Card>

            <!-- Daily Failed -->
            <Card>
                <template #title>
                    <span class="text-sm font-semibold">Today's Failures</span>
                </template>
                <template #content>
                    <div class="flex flex-col items-center">
                        <span class="text-3xl font-bold text-orange-600">{{ summaryData.daily_failed }}</span>
                        <span class="text-xs text-gray-500 mt-1">Rate: {{ summaryData.daily_failure_rate }}%</span>
                    </div>
                </template>
            </Card>

            <!-- Weekly Failed -->
            <Card>
                <template #title>
                    <span class="text-sm font-semibold">Weekly Failures</span>
                </template>
                <template #content>
                    <div class="flex flex-col items-center">
                        <span class="text-3xl font-bold text-purple-600">{{ summaryData.weekly_failed }}</span>
                        <span class="text-xs text-gray-500 mt-1">Rate: {{ summaryData.weekly_failure_rate }}%</span>
                    </div>
                </template>
            </Card>

            <!-- Breakdown by Type -->
            <Card>
                <template #title>
                    <span class="text-sm font-semibold">By Type</span>
                </template>
                <template #content>
                    <div class="space-y-2">
                        <div class="flex justify-between items-center">
                            <span class="text-sm text-gray-600">Validation:</span>
                            <Badge :value="summaryData.breakdown_by_type.VALIDATION || 0" severity="info" />
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-sm text-gray-600">Reminder:</span>
                            <Badge :value="summaryData.breakdown_by_type.REMINDER || 0" severity="warning" />
                        </div>
                    </div>
                </template>
            </Card>
        </div>

        <!-- Filters -->
        <Card class="mb-4">
            <template #title>
                <span class="text-lg font-semibold">Filters</span>
            </template>
            <template #content>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="flex flex-col gap-2">
                        <label class="text-sm text-gray-600">From Date</label>
                        <Calendar
                            v-model="filters.date_from"
                            placeholder="From Date"
                            dateFormat="yy-mm-dd"
                            @date-select="applyFilters"
                            showIcon
                        />
                    </div>
                    <div class="flex flex-col gap-2">
                        <label class="text-sm text-gray-600">To Date</label>
                        <Calendar
                            v-model="filters.date_to"
                            placeholder="To Date"
                            dateFormat="yy-mm-dd"
                            @date-select="applyFilters"
                            showIcon
                        />
                    </div>
                    <div class="flex flex-col gap-2">
                        <label class="text-sm text-gray-600">Status</label>
                        <Dropdown
                            v-model="filters.whatsapp_status"
                            :options="statusOptions"
                            optionLabel="label"
                            optionValue="value"
                            placeholder="All Statuses"
                            @change="applyFilters"
                            showClear
                        />
                    </div>
                    <div class="flex flex-col gap-2">
                        <label class="text-sm text-gray-600">Request Type</label>
                        <Dropdown
                            v-model="filters.request_type"
                            :options="requestTypeOptions"
                            optionLabel="label"
                            optionValue="value"
                            placeholder="All Types"
                            @change="applyFilters"
                            showClear
                        />
                    </div>
                </div>
            </template>
        </Card>

        <!-- Thread List -->
        <ProgressSpinner v-if="loading" class="flex justify-center my-8" />

        <div v-else-if="!anomalies.length" class="empty-state">
            <i class="pi pi-inbox text-6xl text-gray-300"></i>
            <p class="text-gray-500 mt-4">No WhatsApp failures found</p>
        </div>

        <div v-else class="space-y-3 mb-4">
            <Card v-for="anomaly in anomalies" :key="anomaly.id" class="anomaly-card hover:shadow-lg transition-shadow">
                <template #content>
                    <div class="flex gap-4">
                        <!-- Icon -->
                        <div class="flex-shrink-0">
                            <div :class="['w-12 h-12 rounded-full flex items-center justify-center', getTypeColorClass(anomaly.request_type)]">
                                <i :class="['text-xl', getTypeIcon(anomaly.request_type)]"></i>
                            </div>
                        </div>

                        <!-- Content -->
                        <div class="flex-1">
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <h4 class="font-semibold text-gray-800">{{ anomaly.request_type }} - {{ anomaly.customer_name }}</h4>
                                    <div class="flex gap-2 items-center mt-1">
                                        <Tag :value="anomaly.whatsapp_status" :severity="getStatusSeverity(anomaly.whatsapp_status)" />
                                        <span class="text-sm text-gray-500">Phone: {{ anomaly.phone_number }}</span>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <span class="text-sm text-gray-500">{{ formatDate(anomaly.request_date) }}</span>
                                    <br>
                                    <span class="text-xs text-gray-400">{{ anomaly.request_time }}</span>
                                </div>
                            </div>

                            <!-- Message Preview -->
                            <div v-if="anomaly.whatsapp_message" class="text-sm text-gray-600 bg-gray-50 p-2 rounded mb-2">
                                <p class="line-clamp-2">{{ anomaly.whatsapp_message }}</p>
                            </div>

                            <!-- Error Details -->
                            <div v-if="anomaly.error_details" class="flex items-start gap-2 p-2 bg-red-50 rounded text-sm text-red-700">
                                <i class="pi pi-exclamation-circle mt-0.5"></i>
                                <span>{{ anomaly.error_details }}</span>
                            </div>

                            <!-- Actions -->
                            <div class="flex gap-2 mt-2">
                                <Button
                                    @click="showDetails(anomaly)"
                                    label="View Details"
                                    size="small"
                                    text
                                    severity="secondary"
                                />
                            </div>
                        </div>
                    </div>
                </template>
            </Card>
        </div>

        <!-- Pagination -->
        <Paginator
            v-if="totalRecords > 0"
            :rows="perPage"
            :totalRecords="totalRecords"
            :first="(currentPage - 1) * perPage"
            @page="onPageChange"
            template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport"
            currentPageReportTemplate="Showing {first} to {last} of {totalRecords} anomalies"
        />

        <!-- Details Dialog -->
        <Dialog v-model:visible="detailsDialog" header="Anomaly Full Details" :style="{ width: '50vw' }" modal>
            <div v-if="selectedAnomaly" class="space-y-4">
                <div>
                    <h4 class="font-semibold text-gray-700 mb-2">Basic Information</h4>
                    <div class="grid grid-cols-2 gap-3 text-sm">
                        <div><strong>ID:</strong> {{ selectedAnomaly.id }}</div>
                        <div><strong>Dealer ID:</strong> {{ selectedAnomaly.dealer_id }}</div>
                        <div><strong>Request Type:</strong> {{ selectedAnomaly.request_type }}</div>
                        <div><strong>Date:</strong> {{ selectedAnomaly.request_date }}</div>
                        <div><strong>Time:</strong> {{ selectedAnomaly.request_time }}</div>
                        <div><strong>Status:</strong> {{ selectedAnomaly.whatsapp_status }}</div>
                    </div>
                </div>

                <Divider />

                <div>
                    <h4 class="font-semibold text-gray-700 mb-2">Customer Information</h4>
                    <div class="grid grid-cols-2 gap-3 text-sm">
                        <div><strong>Name:</strong> {{ selectedAnomaly.customer_name }}</div>
                        <div><strong>Phone:</strong> {{ selectedAnomaly.phone_number }}</div>
                    </div>
                </div>

                <Divider />

                <div>
                    <h4 class="font-semibold text-gray-700 mb-2">WhatsApp Message</h4>
                    <div class="bg-gray-50 p-3 rounded text-sm">
                        {{ selectedAnomaly.whatsapp_message || 'No message' }}
                    </div>
                </div>

                <Divider />

                <div>
                    <h4 class="font-semibold text-gray-700 mb-2">Fonnte API Response</h4>
                    <pre class="bg-gray-50 p-3 rounded text-xs overflow-auto max-h-64">{{ JSON.stringify(selectedAnomaly.fonnte_response, null, 2) }}</pre>
                </div>

                <Divider />

                <div>
                    <h4 class="font-semibold text-gray-700 mb-2">Error Details</h4>
                    <div class="bg-red-50 p-3 rounded text-sm text-red-700">
                        {{ selectedAnomaly.error_details || 'No error details' }}
                    </div>
                </div>
            </div>
        </Dialog>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import AnomalyService from '@/service/AnomalyService';
import { formatToIndonesiaTime } from '@/utils/dateFormatter';

const emit = defineEmits(['loaded']);
const toast = useToast();

const loading = ref(false);
const loadingSummary = ref(false);
const anomalies = ref([]);
const summaryData = ref(null);
const currentPage = ref(1);
const perPage = ref(50);
const totalRecords = ref(0);
const detailsDialog = ref(false);
const selectedAnomaly = ref(null);

const filters = reactive({
    date_from: null,
    date_to: null,
    whatsapp_status: null,
    request_type: null
});

const statusOptions = [
    { label: 'Failed', value: 'FAILED' },
    { label: 'Error', value: 'ERROR' },
    { label: 'Rejected', value: 'REJECTED' },
    { label: 'Not Sent', value: 'NOT_SENT' }
];

const requestTypeOptions = [
    { label: 'All Types', value: 'ALL' },
    { label: 'Validation', value: 'VALIDATION' },
    { label: 'Reminder', value: 'REMINDER' }
];

const getTypeIcon = (type) => {
    return type === 'VALIDATION' ? 'pi pi-check-circle' : 'pi pi-bell';
};

const getTypeColorClass = (type) => {
    return type === 'VALIDATION' ? 'bg-blue-50 text-blue-500' : 'bg-purple-50 text-purple-500';
};

const getStatusSeverity = (status) => {
    const severityMap = {
        'FAILED': 'danger',
        'ERROR': 'danger',
        'REJECTED': 'warning',
        'NOT_SENT': 'secondary'
    };
    return severityMap[status] || 'info';
};

const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
        const date = new Date(dateStr);
        return formatToIndonesiaTime(date);
    } catch {
        return dateStr;
    }
};

const loadSummary = async () => {
    loadingSummary.value = true;
    try {
        const filterParams = {
            date_from: filters.date_from ? formatDateForAPI(filters.date_from) : null,
            date_to: filters.date_to ? formatDateForAPI(filters.date_to) : null
        };

        const result = await AnomalyService.getWhatsAppAnomalySummary(filterParams);
        if (result.success && result.data.success) {
            summaryData.value = result.data.data;
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.message || 'Failed to load summary', life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load WhatsApp anomaly summary', life: 3000 });
    } finally {
        loadingSummary.value = false;
    }
};

const loadAnomalies = async (page = 1) => {
    loading.value = true;
    try {
        const filterParams = {
            date_from: filters.date_from ? formatDateForAPI(filters.date_from) : null,
            date_to: filters.date_to ? formatDateForAPI(filters.date_to) : null,
            whatsapp_status: filters.whatsapp_status,
            request_type: filters.request_type
        };

        const result = await AnomalyService.getWhatsAppAnomalies(page, perPage.value, filterParams);
        if (result.success && result.data.success) {
            anomalies.value = result.data.data || [];
            totalRecords.value = result.data.pagination.total_records;
            currentPage.value = result.data.pagination.page;
            emit('loaded', totalRecords.value);
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.message || 'Failed to load anomalies', life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load WhatsApp anomalies', life: 3000 });
    } finally {
        loading.value = false;
    }
};

const formatDateForAPI = (date) => {
    if (!date) return null;
    const d = new Date(date);
    return d.toISOString().split('T')[0]; // YYYY-MM-DD format
};

const applyFilters = () => {
    currentPage.value = 1;
    loadAnomalies(1);
    loadSummary();
};

const onPageChange = (event) => {
    const page = event.page + 1; // PrimeVue uses 0-based index
    loadAnomalies(page);
};

const showDetails = (anomaly) => {
    selectedAnomaly.value = anomaly;
    detailsDialog.value = true;
};

const loadData = async () => {
    await Promise.all([
        loadSummary(),
        loadAnomalies(currentPage.value)
    ]);
};

onMounted(() => {
    loadData();
});

defineExpose({ loadData });
</script>

<style scoped>
.whatsapp-anomalies {
    padding: 0.5rem;
}

.empty-state {
    text-align: center;
    padding: 4rem 0;
}

.anomaly-card {
    border-left: 4px solid #EF4444;
}

.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>
