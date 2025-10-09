<template>
    <div class="google-scrape-anomalies">
        <ProgressSpinner v-if="loadingSummary" class="flex justify-center my-8" />

        <!-- Summary Charts Grid -->
        <div v-else-if="summaryData" class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
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
            <!-- <Card>
                <template #title>
                    <span class="text-sm font-semibold">By Type</span>
                </template>
                <template #content>
                    <div class="space-y-2">
                        <div class="flex justify-between items-center">
                            <span class="text-sm text-gray-600">Manual:</span>
                            <Badge :value="summaryData.breakdown_by_type.MANUAL || 0" severity="info" />
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-sm text-gray-600">Scheduled:</span>
                            <Badge :value="summaryData.breakdown_by_type.SCHEDULED || 0" severity="warning" />
                        </div>
                    </div>
                </template>
            </Card> -->
        </div>

        <!-- Common Errors Summary -->
        <Card v-if="summaryData && summaryData.common_errors.length > 0" class="mb-4">
            <template #title>
                <span class="text-lg font-semibold">Top Errors</span>
            </template>
            <template #content>
                <div class="space-y-2">
                    <div
                        v-for="(error, index) in summaryData.common_errors.slice(0, 5)"
                        :key="index"
                        class="flex justify-between items-center p-2 bg-gray-50 rounded"
                    >
                        <span class="text-sm text-gray-700 flex-1">{{ error.error }}</span>
                        <Badge :value="error.count" severity="danger" />
                    </div>
                </div>
            </template>
        </Card>

        <!-- Filters -->
        <Card class="mb-4">
            <template #title>
                <span class="text-lg font-semibold">Filters</span>
            </template>
            <template #content>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                            v-model="filters.scrape_status"
                            :options="statusOptions"
                            optionLabel="label"
                            optionValue="value"
                            placeholder="All Statuses"
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
            <p class="text-gray-500 mt-4">No Google scrape failures found</p>
        </div>

        <div v-else class="space-y-3 mb-4">
            <Card v-for="anomaly in anomalies" :key="anomaly.id" class="anomaly-card hover:shadow-lg transition-shadow">
                <template #content>
                    <div class="flex gap-4">
                        <!-- Icon -->
                        <div class="flex-shrink-0">
                            <div :class="['w-12 h-12 rounded-full flex items-center justify-center', getStatusColorClass(anomaly.scrape_status)]">
                                <i :class="['text-xl', getStatusIcon(anomaly.scrape_status)]"></i>
                            </div>
                        </div>

                        <!-- Content -->
                        <div class="flex-1">
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <h4 class="font-semibold text-gray-800">{{ anomaly.dealer_name || anomaly.dealer_id }}</h4>
                                    <div class="flex gap-2 items-center mt-1">
                                        <Tag :value="anomaly.scrape_status" :severity="getStatusSeverity(anomaly.scrape_status)" />
                                        <Tag :value="anomaly.scrape_type" severity="secondary" />
                                        <span class="text-sm text-gray-500">{{ anomaly.dealer_id }}</span>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <span class="text-sm text-gray-500">{{ formatDate(anomaly.scrape_date) }}</span>
                                </div>
                            </div>

                            <!-- Scrape Statistics -->
                            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 bg-gray-50 p-3 rounded mb-2">
                                <div class="text-center">
                                    <p class="text-xs text-gray-500">Requested</p>
                                    <p class="text-lg font-semibold text-blue-600">{{ anomaly.max_reviews_requested }}</p>
                                </div>
                                <div class="text-center">
                                    <p class="text-xs text-gray-500">Scraped</p>
                                    <p class="text-lg font-semibold text-green-600">{{ anomaly.scraped_reviews }}</p>
                                </div>
                                <div class="text-center">
                                    <p class="text-xs text-gray-500">Failed</p>
                                    <p class="text-lg font-semibold text-red-600">{{ anomaly.failed_reviews }}</p>
                                </div>
                                <div class="text-center">
                                    <p class="text-xs text-gray-500">Success Rate</p>
                                    <p class="text-lg font-semibold text-purple-600">{{ anomaly.success_rate }}%</p>
                                </div>
                            </div>

                            <!-- Additional Info -->
                            <div class="flex flex-wrap gap-4 text-sm text-gray-600 mb-2">
                                <span v-if="anomaly.scrape_duration_seconds">
                                    <i class="pi pi-clock mr-1"></i>
                                    {{ anomaly.scrape_duration_seconds }}s
                                </span>
                                <span v-if="anomaly.new_reviews">
                                    <i class="pi pi-plus mr-1"></i>
                                    {{ anomaly.new_reviews }} new
                                </span>
                                <span v-if="anomaly.duplicate_reviews">
                                    <i class="pi pi-copy mr-1"></i>
                                    {{ anomaly.duplicate_reviews }} duplicates
                                </span>
                                <span v-if="anomaly.api_response_id">
                                    <i class="pi pi-id-card mr-1"></i>
                                    {{ anomaly.api_response_id }}
                                </span>
                            </div>

                            <!-- Error Message -->
                            <div v-if="anomaly.error_message" class="flex items-start gap-2 p-2 bg-red-50 rounded text-sm text-red-700 mb-2">
                                <i class="pi pi-exclamation-circle mt-0.5"></i>
                                <span>{{ anomaly.error_message }}</span>
                            </div>

                            <!-- Warning Message -->
                            <div v-if="anomaly.warning_message" class="flex items-start gap-2 p-2 bg-yellow-50 rounded text-sm text-yellow-700 mb-2">
                                <i class="pi pi-exclamation-triangle mt-0.5"></i>
                                <span>{{ anomaly.warning_message }}</span>
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
        <Dialog v-model:visible="detailsDialog" header="Scrape Anomaly Full Details" :style="{ width: '50vw' }" modal>
            <div v-if="selectedAnomaly" class="space-y-4">
                <div>
                    <h4 class="font-semibold text-gray-700 mb-2">Scrape Information</h4>
                    <div class="grid grid-cols-2 gap-3 text-sm">
                        <div><strong>ID:</strong> {{ selectedAnomaly.id }}</div>
                        <div><strong>Dealer ID:</strong> {{ selectedAnomaly.dealer_id }}</div>
                        <div><strong>Dealer Name:</strong> {{ selectedAnomaly.dealer_name }}</div>
                        <div><strong>Scrape Date:</strong> {{ selectedAnomaly.scrape_date }}</div>
                        <div><strong>Status:</strong> {{ selectedAnomaly.scrape_status }}</div>
                        <div><strong>Type:</strong> {{ selectedAnomaly.scrape_type }}</div>
                        <div><strong>Duration:</strong> {{ selectedAnomaly.scrape_duration_seconds }}s</div>
                        <div><strong>Scraped By:</strong> {{ selectedAnomaly.scraped_by || 'System' }}</div>
                    </div>
                </div>

                <Divider />

                <div>
                    <h4 class="font-semibold text-gray-700 mb-2">Scrape Results</h4>
                    <div class="grid grid-cols-2 gap-3 text-sm">
                        <div><strong>Max Reviews Requested:</strong> {{ selectedAnomaly.max_reviews_requested }}</div>
                        <div><strong>Reviews Scraped:</strong> {{ selectedAnomaly.scraped_reviews }}</div>
                        <div><strong>Failed Reviews:</strong> {{ selectedAnomaly.failed_reviews }}</div>
                        <div><strong>New Reviews:</strong> {{ selectedAnomaly.new_reviews }}</div>
                        <div><strong>Duplicate Reviews:</strong> {{ selectedAnomaly.duplicate_reviews }}</div>
                        <div><strong>Success Rate:</strong> {{ selectedAnomaly.success_rate }}%</div>
                    </div>
                </div>

                <Divider />

                <div v-if="selectedAnomaly.business_name">
                    <h4 class="font-semibold text-gray-700 mb-2">Business Information</h4>
                    <div class="grid grid-cols-2 gap-3 text-sm">
                        <div><strong>Business Name:</strong> {{ selectedAnomaly.business_name }}</div>
                        <div><strong>Google Business ID:</strong> {{ selectedAnomaly.google_business_id }}</div>
                        <div><strong>API Response ID:</strong> {{ selectedAnomaly.api_response_id }}</div>
                    </div>
                </div>

                <Divider />

                <div v-if="selectedAnomaly.error_message">
                    <h4 class="font-semibold text-gray-700 mb-2">Error Message</h4>
                    <div class="bg-red-50 p-3 rounded text-sm text-red-700">
                        {{ selectedAnomaly.error_message }}
                    </div>
                </div>

                <div v-if="selectedAnomaly.warning_message">
                    <h4 class="font-semibold text-gray-700 mb-2">Warning Message</h4>
                    <div class="bg-yellow-50 p-3 rounded text-sm text-yellow-700">
                        {{ selectedAnomaly.warning_message }}
                    </div>
                </div>

                <Divider />

                <div v-if="selectedAnomaly.sentiment_analysis_status">
                    <h4 class="font-semibold text-gray-700 mb-2">Sentiment Analysis</h4>
                    <div class="text-sm">
                        <strong>Status:</strong> {{ selectedAnomaly.sentiment_analysis_status }}
                    </div>
                </div>
            </div>
        </Dialog>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
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
    scrape_status: null
});

const statusOptions = [
    { label: 'Failed', value: 'FAILED' },
    { label: 'Partial', value: 'PARTIAL' }
];

const getStatusIcon = (status) => {
    return status === 'FAILED' ? 'pi pi-times-circle' : 'pi pi-exclamation-triangle';
};

const getStatusColorClass = (status) => {
    return status === 'FAILED' ? 'bg-red-50 text-red-500' : 'bg-orange-50 text-orange-500';
};

const getStatusSeverity = (status) => {
    return status === 'FAILED' ? 'danger' : 'warning';
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

        const result = await AnomalyService.getGoogleScrapeAnomalySummary(filterParams);
        if (result.success && result.data.success) {
            summaryData.value = result.data.data;
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.message || 'Failed to load summary', life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load Google scrape anomaly summary', life: 3000 });
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
            scrape_status: filters.scrape_status
        };

        const result = await AnomalyService.getGoogleScrapeAnomalies(page, perPage.value, filterParams);
        if (result.success && result.data.success) {
            anomalies.value = result.data.data || [];
            totalRecords.value = result.data.pagination.total_records;
            currentPage.value = result.data.pagination.page;
            emit('loaded', totalRecords.value);
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.message || 'Failed to load anomalies', life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load Google scrape anomalies', life: 3000 });
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
.google-scrape-anomalies {
    padding: 0.5rem;
}

.empty-state {
    text-align: center;
    padding: 4rem 0;
}

.anomaly-card {
    border-left: 4px solid #F59E0B;
}
</style>
