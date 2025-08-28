<template>
    <div class="space-y-6">
        <!-- Filter Controls -->
        <div class="flex justify-end items-center space-x-4 mb-6">
            <!-- No AHASS Filter (Only for SUPER_ADMIN) -->
            <div v-if="showAhassFilter" class="flex items-center space-x-2">
                <label for="ahass-filter" class="text-sm font-medium">No AHASS:</label>
                <InputText 
                    id="ahass-filter"
                    v-model="filters.no_ahass"
                    placeholder="Enter No AHASS"
                    class="w-36"
                />
            </div>

            <!-- Date Type Selector -->
            <div class="flex items-center space-x-2">
                <label for="date-type" class="text-sm font-medium">Date Type:</label>
                <Dropdown 
                    id="date-type"
                    v-model="selectedDateType"
                    :options="dateTypeOptions"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Select date type"
                    class="w-40"
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

            <!-- Search and Clear Buttons -->
            <div class="flex items-center space-x-2">
                <Button 
                    @click="handleSearch"
                    icon="pi pi-search"
                    severity="primary"
                    size="small"
                    title="Search"
                />
                <Button 
                    @click="clearFilters"
                    icon="pi pi-times"
                    severity="secondary"
                    size="small"
                    title="Clear Filters"
                />
            </div>

            <!-- Upload Button (Only for SUPER_ADMIN) -->
            <Button 
                v-if="canUpload"
                @click="showUploadSidebar = true"
                label="Upload File"
                icon="pi pi-upload"
                severity="success"
                size="small"
            />
        </div>

        <!-- Overview Section -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <!-- Total Records Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="loading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px;" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 mb-2">Total Records</h3>
                        <div class="text-3xl font-bold text-blue-600 mb-1">
                            {{ statistics?.total_records || 0 }}
                        </div>
                        <p class="text-sm text-surface-500">Customer Satisfaction</p>
                    </div>
                </template>
            </Card>

            <!-- Average Rating Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="loading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px;" />
                    </div>
                    <div v-else>
                        <div class="flex items-center justify-center space-x-2 mb-2">
                            <!-- <i class="pi pi-star-fill text-yellow-400 text-lg"></i> -->
                            <h3 class="text-lg font-semibold text-surface-900">Average Rating</h3>
                        </div>
                        <div class="text-3xl font-bold text-green-600 mb-1">
                            {{ getAverageRating() }}
                        </div>
                        <p class="text-sm text-surface-500">Overall Score</p>
                    </div>
                </template>
            </Card>

            <!-- Top Rating Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="loading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px;" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 mb-2">Most Common</h3>
                        <div class="text-3xl font-bold text-orange-600 mb-1">
                            {{ getTopRating() }}
                        </div>
                        <p class="text-sm text-surface-500">Rating Score</p>
                    </div>
                </template>
            </Card>

            <!-- AHASS Count Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="loading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px;" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 mb-2">AHASS Count</h3>
                        <div class="text-3xl font-bold text-primary-600 mb-1">
                            {{ statistics?.top_ahass?.length || 0 }}
                        </div>
                        <p class="text-sm text-surface-500">Unique Dealers</p>
                    </div>
                </template>
            </Card>
        </div>

        <!-- Details Table -->
        <Card>
            <template #title>
                <h2 class="text-xl font-bold text-surface-900">Customer Satisfaction Data</h2>
            </template>
            <template #content>
                <DataTable 
                    :value="satisfactionData"
                    :loading="loading"
                    responsiveLayout="scroll"
                    :paginator="false"
                    dataKey="id"
                    class="p-datatable-customers"
                >
                    <Column field="no_tiket" header="No Tiket" style="min-width: 120px">
                        <template #body="{ data }">
                            <span class="font-medium">{{ data.no_tiket || '-' }}</span>
                        </template>
                    </Column>
                    
                    <Column field="nama_konsumen" header="Nama Konsumen" style="min-width: 200px">
                        <template #body="{ data }">
                            {{ data.nama_konsumen || '-' }}
                        </template>
                    </Column>
                    
                    <Column field="no_ahass" header="No AHASS" style="min-width: 100px">
                        <template #body="{ data }">
                            <Tag :value="data.no_ahass || 'N/A'" severity="info" />
                        </template>
                    </Column>
                    
                    <Column field="nama_ahass" header="Nama AHASS" style="min-width: 200px">
                        <template #body="{ data }">
                            {{ data.nama_ahass || '-' }}
                        </template>
                    </Column>
                    
                    <Column field="rating" header="Rating" style="min-width: 80px">
                        <template #body="{ data }">
                            <div v-if="data.rating" class="flex align-items-center gap-1">
                                <Tag 
                                    :value="data.rating"
                                    :severity="getRatingSeverity(data.rating)"
                                />
                                <div class="flex">
                                    <i 
                                        v-for="star in 5" 
                                        :key="star"
                                        class="pi pi-star-fill text-xs"
                                        :class="star <= parseInt(data.rating) ? 'text-yellow-400' : 'text-gray-300'"
                                    ></i>
                                </div>
                            </div>
                            <span v-else class="text-gray-400">-</span>
                        </template>
                    </Column>
                    
                    <Column field="periode_utk_suspend" header="Periode UTK Suspend" style="min-width: 180px">
                        <template #body="{ data }">
                            <span class="text-sm">{{ data.periode_utk_suspend || '-' }}</span>
                        </template>
                    </Column>
                    
                    <Column field="submit_review_date_first_fu_cs" header="Submit Review Date" style="min-width: 150px">
                        <template #body="{ data }">
                            <span class="text-sm">{{ data.submit_review_date_first_fu_cs || '-' }}</span>
                        </template>
                    </Column>
                    
                    <Column field="indikasi_keluhan" header="Indikasi Keluhan" style="min-width: 200px">
                        <template #body="{ data }">
                            <span class="text-sm">{{ data.indikasi_keluhan || '-' }}</span>
                        </template>
                    </Column>
                    
                    <Column field="departemen" header="Departemen" style="min-width: 150px">
                        <template #body="{ data }">
                            <Tag 
                                :value="data.departemen || 'N/A'"
                                severity="secondary"
                                class="text-xs"
                            />
                        </template>
                    </Column>
                </DataTable>

                <!-- Pagination -->
                <Paginator
                    v-if="pagination.total_count > pagination.page_size"
                    :rows="pagination.page_size"
                    :totalRecords="pagination.total_count"
                    :rowsPerPageOptions="[10, 20, 50]"
                    @page="onPageChange"
                    class="mt-4"
                />

                <!-- Last Upload Info -->
                <div v-if="lastUploadInfo" class="mt-4 p-3 bg-surface-50 rounded-lg border">
                    <div class="flex items-center justify-between text-sm">
                        <div class="flex items-center space-x-2">
                            <i class="pi pi-upload text-primary-500"></i>
                            <span class="font-medium">Last Upload:</span>
                            <span>{{ formatDate(lastUploadInfo.created_at) }}</span>
                        </div>
                        <div class="flex items-center space-x-4">
                            <div class="flex items-center space-x-1">
                                <span class="text-surface-600">Records:</span>
                                <Tag :value="lastUploadInfo.total_records || 0" severity="info" />
                            </div>
                            <div class="flex items-center space-x-1">
                                <span class="text-surface-600">Status:</span>
                                <Tag 
                                    :value="lastUploadInfo.status || 'Unknown'"
                                    :severity="getUploadStatusSeverity(lastUploadInfo.status)"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </Card>

        <!-- Upload Sidebar -->
        <CustomerSatisfactionUploadSidebar 
            v-model:visible="showUploadSidebar"
            @upload-success="onUploadSuccess"
        />
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useAuthStore } from '@/stores/auth';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import Tag from 'primevue/tag';
import Paginator from 'primevue/paginator';
import ProgressSpinner from 'primevue/progressspinner';
import CustomerSatisfactionUploadSidebar from '@/components/CustomerSatisfactionUploadSidebar.vue';
import CustomerService from '@/service/CustomerService';

const authStore = useAuthStore();
const toast = useToast();

// Data state
const satisfactionData = ref([]);
const statistics = ref(null);
const loading = ref(false);
const showUploadSidebar = ref(false);
const lastUploadInfo = ref(null);

// Filter state
const filters = reactive({
    no_ahass: '',
    periode_utk_suspend: '',
    submit_review_date: '',
    date_from: null,
    date_to: null
});

const selectedDateFrom = ref(null);
const selectedDateTo = ref(null);
const selectedDateType = ref('created');

// Date type options
const dateTypeOptions = ref([
    { label: 'Created Date', value: 'created' },
    { label: 'Periode UTK Suspend', value: 'periode_suspend' },
    { label: 'Submit Review Date', value: 'submit_review' }
]);

// Pagination state
const pagination = reactive({
    page: 1,
    page_size: 10,
    total_count: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
});

// Role-based computed properties
const showAhassFilter = computed(() => authStore.userRole === 'SUPER_ADMIN');
const canUpload = computed(() => authStore.userRole === 'SUPER_ADMIN');
const isDealerUser = computed(() => authStore.userRole === 'DEALER_USER');

const paginatorFirst = computed({
    get: () => (pagination.page - 1) * pagination.page_size,
    set: (value) => {
        pagination.page = Math.floor(value / pagination.page_size) + 1;
    }
});

// Load data
const loadData = async () => {
    loading.value = true;
    try {
        // Prepare date filters based on selected type
        let apiFilters = {
            no_ahass: filters.no_ahass || null,
            periode_utk_suspend: filters.periode_utk_suspend || null,
            submit_review_date: filters.submit_review_date || null,
            page: pagination.page,
            page_size: pagination.page_size
        };

        // Add date filters based on selected type
        if (selectedDateType.value === 'created') {
            apiFilters.date_from = selectedDateFrom.value ? formatDateForAPI(selectedDateFrom.value) : null;
            apiFilters.date_to = selectedDateTo.value ? formatDateForAPI(selectedDateTo.value) : null;
        }

        // Auto-apply dealer filter for DEALER_USER
        if (isDealerUser.value && authStore.userDealerId) {
            apiFilters.no_ahass = authStore.userDealerId;
        }

        // Load records
        const [recordsResult, statsResult] = await Promise.all([
            CustomerService.getCustomerSatisfactionRecords(apiFilters),
            CustomerService.getCustomerSatisfactionStatistics(apiFilters)
        ]);

        if (recordsResult.success) {
            satisfactionData.value = recordsResult.data?.records || [];
            const paginationData = recordsResult.data?.pagination || {};
            Object.assign(pagination, paginationData);
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: recordsResult.message,
                life: 5000
            });
        }

        if (statsResult.success) {
            statistics.value = statsResult.data;
        }

    } catch (error) {
        console.error('Error loading customer satisfaction data:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load customer satisfaction data',
            life: 5000
        });
    } finally {
        loading.value = false;
    }
};

// Manual search handler
const handleSearch = () => {
    pagination.page = 1; // Reset to first page when searching
    loadData();
};

// Pagination handler
const onPageChange = (event) => {
    pagination.page = event.page + 1;
    loadData();
};

// Filter actions
const clearFilters = () => {
    // Only clear AHASS filter for SUPER_ADMIN
    if (showAhassFilter.value) {
        filters.no_ahass = '';
    }
    filters.periode_utk_suspend = '';
    filters.submit_review_date = '';
    selectedDateFrom.value = null;
    selectedDateTo.value = null;
    selectedDateType.value = 'created';
    pagination.page = 1;
    loadData();
};

// Upload success handler
const onUploadSuccess = () => {
    toast.add({
        severity: 'success',
        summary: 'Upload Complete',
        detail: 'Customer satisfaction data uploaded successfully',
        life: 5000
    });
    loadData(); // Refresh data after upload
    loadLastUploadInfo(); // Refresh upload info
};

// Utilities
const formatDateForAPI = (date) => {
    if (!date) return null;
    const d = new Date(date);
    return d.getFullYear() + '-' + 
           String(d.getMonth() + 1).padStart(2, '0') + '-' + 
           String(d.getDate()).padStart(2, '0');
};

const getRatingSeverity = (rating) => {
    const ratingNum = parseInt(rating);
    if (ratingNum >= 4) return 'success';
    if (ratingNum >= 3) return 'warning';
    return 'danger';
};

const getAverageRating = () => {
    if (!statistics.value?.rating_distribution) return '-';
    let totalRating = 0;
    let totalCount = 0;
    
    statistics.value.rating_distribution.forEach(item => {
        const rating = parseInt(item.rating);
        if (!isNaN(rating)) {
            totalRating += rating * item.count;
            totalCount += item.count;
        }
    });
    
    return totalCount > 0 ? (totalRating / totalCount).toFixed(1) : '-';
};

const getTopRating = () => {
    if (!statistics.value?.rating_distribution) return '-';
    
    const maxItem = statistics.value.rating_distribution.reduce((max, item) => {
        return item.count > max.count ? item : max;
    }, { count: 0, rating: '-' });
    
    return maxItem.rating;
};

// Load last upload info
const loadLastUploadInfo = async () => {
    try {
        const result = await CustomerService.getCustomerSatisfactionUploadTrackers({
            page: 1,
            page_size: 1
        });
        if (result.success && result.data?.records?.length > 0) {
            lastUploadInfo.value = result.data.records[0];
        }
    } catch (error) {
        console.error('Error loading upload info:', error);
    }
};

// Utility functions
const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: '2-digit', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

const getUploadStatusSeverity = (status) => {
    switch (status?.toLowerCase()) {
        case 'completed':
        case 'success':
            return 'success';
        case 'processing':
        case 'pending':
            return 'warning';
        case 'failed':
        case 'error':
            return 'danger';
        default:
            return 'secondary';
    }
};

// Initialize
onMounted(() => {
    loadData();
    loadLastUploadInfo();
});
</script>

<style scoped>
/* Custom styles for the customer satisfaction page */

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