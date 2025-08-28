<template>
    <div class="grid">
        <div class="col-12">
            <div class="card">
                <div class="flex justify-content-between align-items-center mb-3">
                    <h5>Customer Satisfaction Data</h5>
                    <Button 
                        @click="showUploadSidebar = true"
                        label="Upload File"
                        icon="pi pi-upload"
                        severity="success"
                        class="p-button-sm"
                    />
                </div>

                <!-- Filters Section -->
                <Card class="mb-4">
                    <template #content>
                        <div class="grid">
                            <!-- Dealer Filter (No AHASS) -->
                            <div class="col-12 md:col-4">
                                <label for="dealerFilter" class="block text-sm font-medium text-900 mb-2">
                                    No AHASS
                                </label>
                                <InputText 
                                    id="dealerFilter"
                                    v-model="filters.no_ahass"
                                    placeholder="Enter No AHASS"
                                    class="w-full"
                                    @input="debouncedSearch"
                                />
                            </div>
                            
                            <!-- Date Type Selector -->
                            <div class="col-12 md:col-4">
                                <label for="dateType" class="block text-sm font-medium text-900 mb-2">
                                    Filter by Date
                                </label>
                                <Dropdown 
                                    id="dateType"
                                    v-model="selectedDateType"
                                    :options="dateTypeOptions"
                                    optionLabel="label"
                                    optionValue="value"
                                    placeholder="Select date type"
                                    class="w-full"
                                    @change="loadData"
                                />
                            </div>
                            
                            <!-- Date Range -->
                            <div class="col-12 md:col-4">
                                <label class="block text-sm font-medium text-900 mb-2">
                                    Date Range
                                </label>
                                <div class="flex gap-2">
                                    <Calendar 
                                        v-model="selectedDateFrom"
                                        placeholder="From"
                                        dateFormat="yy-mm-dd"
                                        class="flex-1"
                                        @date-select="loadData"
                                        showIcon
                                    />
                                    <Calendar 
                                        v-model="selectedDateTo"
                                        placeholder="To"
                                        dateFormat="yy-mm-dd"
                                        class="flex-1"
                                        @date-select="loadData"
                                        showIcon
                                    />
                                </div>
                            </div>
                            
                            
                            
                            <!-- Filter Actions -->
                            <div class="col-12">
                                <div class="flex gap-2 justify-content-end">
                                    <Button 
                                        @click="clearFilters"
                                        label="Clear"
                                        icon="pi pi-times"
                                        severity="secondary"
                                        outlined
                                        size="small"
                                    />
                                    <Button 
                                        @click="loadData"
                                        label="Search"
                                        icon="pi pi-search"
                                        size="small"
                                    />
                                </div>
                            </div>
                        </div>
                    </template>
                </Card>

                <!-- Statistics Summary -->
                <Card v-if="statistics" class="mb-4">
                    <template #content>
                        <div class="grid">
                            <div class="col-6 md:col-3">
                                <div class="text-center">
                                    <div class="text-2xl font-bold text-primary">{{ statistics.total_records || 0 }}</div>
                                    <div class="text-sm text-600">Total Records</div>
                                </div>
                            </div>
                            <div class="col-6 md:col-3">
                                <div class="text-center">
                                    <div class="text-2xl font-bold text-green-500">{{ getAverageRating() }}</div>
                                    <div class="text-sm text-600">Avg Rating</div>
                                </div>
                            </div>
                            <div class="col-6 md:col-3">
                                <div class="text-center">
                                    <div class="text-2xl font-bold text-orange-500">{{ getTopRating() }}</div>
                                    <div class="text-sm text-600">Top Rating</div>
                                </div>
                            </div>
                            <div class="col-6 md:col-3">
                                <div class="text-center">
                                    <div class="text-2xl font-bold text-blue-500">{{ statistics.top_ahass?.length || 0 }}</div>
                                    <div class="text-sm text-600">AHASS Count</div>
                                </div>
                            </div>
                        </div>
                    </template>
                </Card>

                <!-- Data Table -->
                <DataTable 
                    :value="satisfactionData"
                    :loading="loading"
                    responsiveLayout="scroll"
                    :paginator="false"
                    dataKey="id"
                    class="p-datatable-sm"
                    :scrollable="true"
                    scrollHeight="500px"
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
                <div class="flex justify-content-between align-items-center mt-3">
                    <div class="text-sm text-600">
                        Showing {{ ((pagination.page - 1) * pagination.page_size) + 1 }} 
                        to {{ Math.min(pagination.page * pagination.page_size, pagination.total_count) }} 
                        of {{ pagination.total_count }} entries
                    </div>
                    <Paginator
                        v-model:first="paginatorFirst"
                        :rows="pagination.page_size"
                        :totalRecords="pagination.total_count"
                        @page="onPageChange"
                        :template="{
                            '640px': 'PrevPageLink CurrentPageReport NextPageLink',
                            default: 'FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink'
                        }"
                        class="justify-content-end"
                    />
                </div>
            </div>
        </div>

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
import CustomerSatisfactionUploadSidebar from '@/components/CustomerSatisfactionUploadSidebar.vue';
import CustomerService from '@/service/CustomerService';

const authStore = useAuthStore();
const toast = useToast();

// Data state
const satisfactionData = ref([]);
const statistics = ref(null);
const loading = ref(false);
const showUploadSidebar = ref(false);

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

// Search debouncing
let searchTimeout = null;
const debouncedSearch = () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        pagination.page = 1; // Reset to first page when searching
        loadData();
    }, 500);
};

// Pagination handler
const onPageChange = (event) => {
    pagination.page = event.page + 1;
    loadData();
};

// Filter actions
const clearFilters = () => {
    filters.no_ahass = '';
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

// Initialize
onMounted(() => {
    loadData();
});
</script>

<style scoped>
.p-datatable .p-column-header {
    background-color: var(--p-primary-50);
}

.text-primary {
    color: var(--p-primary-500);
}
</style>