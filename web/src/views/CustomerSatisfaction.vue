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
            
            <!-- AHASS Count Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="loading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px;" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-2">SENTIMENT RECORD</h3>
                       
                        <p class="text-sm text-surface-500 dark:text-surface-400"><i>Work in progress</i></p>
                    </div>
                </template>
            </Card>

            

            <!-- Top Complaints Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="loading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px;" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-3">TOP 3 INDIKASI KELUHAN</h3>
                        <div v-if="topComplaints && topComplaints.length > 0" class="space-y-2">
                            <div 
                                v-for="(complaint, index) in topComplaints" 
                                :key="index"
                                class="flex items-start gap-3 p-2 bg-surface-50 dark:bg-surface-800 rounded-lg"
                            >
                                <div class="flex-1 min-w-0">
                                    <div class="text-xs font-medium text-surface-800 dark:text-surface-200 break-words" :title="complaint.indikasi_keluhan">
                                        {{ complaint.indikasi_keluhan || 'N/A' }}
                                    </div>
                                    <div class="text-xs text-surface-500 dark:text-surface-400 mt-1">{{ complaint.count }} cases</div>
                                </div>
                                <div class="text-sm font-bold text-surface-900 dark:text-surface-0 flex-shrink-0">
                                    {{ complaint.percentage }}%
                                </div>
                            </div>
                        </div>
                        <div v-else class="text-sm text-surface-500 dark:text-surface-400">
                            No complaint data
                        </div>
                    </div>
                </template>
            </Card>
            

            <!-- Overall Rating Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="loading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px;" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-3">OVERALL RATING</h3>
                        
                        <div class="mb-4">
                            <!-- Main Rating Display -->
                            <div class="flex items-center justify-center space-x-3 mb-3">
                                <span class="text-6xl font-bold text-surface-900 dark:text-surface-0">
                                    {{ overallRating?.current_rating || '-' }}
                                </span>
                                <div class="flex items-center">
                                    <!-- Star Rating Display -->
                                    <div class="flex mr-2">
                                        <i 
                                            v-for="star in 5" 
                                            :key="star"
                                            class="pi pi-star-fill text-lg"
                                            :class="getStarColor(star, overallRating?.current_rating)"
                                        ></i>
                                    </div>
                                    <span class="text-base text-surface-600 dark:text-surface-400 font-medium">/ 5.0</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Month-over-Month Comparison -->
                        <div v-if="overallRating?.change !== null && overallRating?.change_direction" class="text-base">
                            <span 
                                :class="getChangeColor(overallRating?.change_direction)"
                                class="font-medium"
                            >
                                {{ formatChangeText(overallRating?.change, overallRating?.change_direction) }}
                            </span>
                        </div>
                        <div v-else class="text-base text-surface-500 dark:text-surface-400">
                            No comparison data
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Total Reviews Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="loading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px;" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-3">Total Review</h3>
                        <div class="text-6xl font-bold text-blue-600 mb-2">
                            {{ statistics?.total_records || 0 }}
                        </div>
                        <p class="text-base text-surface-500 font-medium">Reviews</p>
                    </div>
                </template>
            </Card>
            
        </div>

        <!-- Details Table -->
        <Card>
            <template #title>
                <h2 class="text-xl font-bold text-surface-900 dark:text-surface-0">Customer Satisfaction Data</h2>
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
                    <!-- No (Index) Column -->
                    <Column header="No" style="min-width: 60px">
                        <template #body="{ index }">
                            <span class="font-medium text-sm">
                                {{ (pagination.page - 1) * pagination.page_size + index + 1 }}
                            </span>
                        </template>
                    </Column>
                    
                    <!-- No Tiket Column -->
                    <Column field="no_tiket" header="No Tiket" style="min-width: 120px">
                        <template #body="{ data }">
                            <span class="font-medium text-sm">{{ data.no_tiket || '-' }}</span>
                        </template>
                    </Column>
                    
                    <!-- No AHASS Column (Only for SUPER_ADMIN) -->
                    <Column v-if="showAhassFilter" field="no_ahass" header="No AHASS" style="min-width: 100px">
                        <template #body="{ data }">
                            <span class="font-medium text-sm">{{ data.no_ahass || '-' }}</span>
                        </template>
                    </Column>
                    
                    <!-- Tanggal Rating Column -->
                    <Column field="tanggal_rating" header="Tanggal Rating" style="min-width: 120px">
                        <template #body="{ data }">
                            <span class="text-sm">{{ data.tanggal_rating || '-' }}</span>
                        </template>
                    </Column>
                    
                    <!-- Nama Konsumen Column -->
                    <Column field="nama_konsumen" header="Nama Konsumen" style="min-width: 180px">
                        <template #body="{ data }">
                            <span class="text-sm">{{ data.nama_konsumen || '-' }}</span>
                        </template>
                    </Column>
                    
                    <!-- No HP Column (with masking) -->
                    <Column field="no_hp" header="No HP" style="min-width: 120px">
                        <template #body="{ data }">
                            <span class="text-sm font-mono">{{ maskPhoneNumber(data.no_hp) || '-' }}</span>
                        </template>
                    </Column>
                    
                    <!-- Alamat Email Column (with masking) -->
                    <Column field="alamat_email" header="Alamat Email" style="min-width: 150px">
                        <template #body="{ data }">
                            <span class="text-sm font-mono">{{ maskEmail(data.alamat_email) || '-' }}</span>
                        </template>
                    </Column>
                    
                    <!-- Kota Column -->
                    <Column field="kota" header="Kota" style="min-width: 120px">
                        <template #body="{ data }">
                            <span class="text-sm">{{ data.kota || '-' }}</span>
                        </template>
                    </Column>
                    
                    <!-- Inbox Column -->
                    <Column field="inbox" header="Inbox" style="min-width: 200px">
                        <template #body="{ data }">
                            <span 
                                class="text-sm cursor-help" 
                                v-tooltip.left="data.inbox || 'No inbox data'"
                            >
                                {{ data.inbox ? (data.inbox.length > 50 ? data.inbox.substring(0, 50) + '...' : data.inbox) : '-' }}
                            </span>
                        </template>
                    </Column>
                    
                    <!-- Indikasi Keluhan Column -->
                    <Column field="indikasi_keluhan" header="Indikasi Keluhan" style="min-width: 180px">
                        <template #body="{ data }">
                            <span class="text-sm">{{ data.indikasi_keluhan || '-' }}</span>
                        </template>
                    </Column>
                    
                    <!-- Rating Column -->
                    <Column field="rating" header="Rating" style="min-width: 100px">
                        <template #body="{ data }">
                            <div v-if="data.rating" class="flex align-items-center gap-2">
                                <Tag 
                                    :value="data.rating"
                                    :severity="getRatingSeverity(data.rating)"
                                    class="text-xs"
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

                <!-- Simplified Latest Upload Info -->
                <div v-if="lastUploadInfo" class="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-surface-700 dark:to-surface-800 rounded-xl border border-blue-200 dark:border-surface-600 shadow-sm">
                    <div class="flex items-center space-x-3">
                        <div class="flex items-center justify-center w-10 h-10 bg-blue-500 dark:bg-blue-600 text-white rounded-full">
                            <i class="pi pi-calendar text-lg"></i>
                        </div>
                        <div>
                            <h4 class="text-lg font-semibold text-surface-800 dark:text-surface-200 mb-1">Latest Upload</h4>
                            <div class="text-sm text-surface-600 dark:text-surface-400">
                                <span>{{ formatUploadDate(lastUploadInfo.latest_upload_date) }}</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- No Upload Info State -->
                <div v-else-if="!loadingUploadInfo" class="mt-6 p-4 bg-surface-50 dark:bg-surface-800 rounded-lg border border-dashed border-surface-300 dark:border-surface-600 text-center">
                    <div class="flex flex-col items-center space-y-2">
                        <i class="pi pi-info-circle text-3xl text-surface-400 dark:text-surface-500"></i>
                        <p class="text-sm text-surface-500 dark:text-surface-400">No upload information available</p>
                        <p class="text-xs text-surface-400 dark:text-surface-500">Upload a file to see the latest upload details here</p>
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
import Calendar from 'primevue/calendar';
import Tag from 'primevue/tag';
import Paginator from 'primevue/paginator';
import ProgressSpinner from 'primevue/progressspinner';
import CustomerSatisfactionUploadSidebar from '@/components/CustomerSatisfactionUploadSidebar.vue';
import CustomerService from '@/service/CustomerService';

const authStore = useAuthStore();
const toast = useToast();

// Date utility functions for current month defaults
const getCurrentMonthFirstDay = () => {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), 1);
};

const getCurrentMonthLastDay = () => {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth() + 1, 0);
};

// Data state
const satisfactionData = ref([]);
const statistics = ref(null);
const loading = ref(false);
const showUploadSidebar = ref(false);
const lastUploadInfo = ref(null);
const loadingUploadInfo = ref(false);
const topComplaints = ref([]);
const overallRating = ref(null);

// Filter state
const filters = reactive({
    no_ahass: '',
    periode_utk_suspend: '',
    submit_review_date: '',
    date_from: null,
    date_to: null
});

const selectedDateFrom = ref(getCurrentMonthFirstDay());
const selectedDateTo = ref(getCurrentMonthLastDay());
// Always use tanggal_rating for filtering
const selectedDateType = 'tanggal_rating';


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

        // Always use tanggal_rating for date filtering
        apiFilters.date_from = selectedDateFrom.value ? formatDateForAPI(selectedDateFrom.value) : null;
        apiFilters.date_to = selectedDateTo.value ? formatDateForAPI(selectedDateTo.value) : null;

        // Auto-apply dealer filter for DEALER_USER
        if (isDealerUser.value && authStore.userDealerId) {
            apiFilters.no_ahass = authStore.userDealerId;
        }

        // Load records, statistics, top complaints, and overall rating
        const [recordsResult, statsResult, complaintsResult, ratingResult] = await Promise.all([
            CustomerService.getCustomerSatisfactionRecords(apiFilters),
            CustomerService.getCustomerSatisfactionStatistics(apiFilters),
            CustomerService.getTopIndikasiKeluhan({
                periode_utk_suspend: apiFilters.periode_utk_suspend,
                submit_review_date: apiFilters.submit_review_date,
                no_ahass: apiFilters.no_ahass,
                date_from: apiFilters.date_from,
                date_to: apiFilters.date_to,
                limit: 3
            }),
            CustomerService.getOverallRating({
                periode_utk_suspend: apiFilters.periode_utk_suspend,
                submit_review_date: apiFilters.submit_review_date,
                no_ahass: apiFilters.no_ahass,
                date_from: apiFilters.date_from,
                date_to: apiFilters.date_to,
                compare_previous_period: true
            })
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

        if (complaintsResult.success) {
            topComplaints.value = complaintsResult.data || [];
        }

        if (ratingResult.success) {
            overallRating.value = ratingResult.data || null;
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
    // Reset to current month defaults instead of null
    selectedDateFrom.value = getCurrentMonthFirstDay();
    selectedDateTo.value = getCurrentMonthLastDay();
    // Reset to appropriate default based on user role
    selectedDateType.value = isDealerUser.value ? 'tanggal_rating' : 'created';
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

// Masking utilities
const maskPhoneNumber = (phoneNumber) => {
    if (!phoneNumber || typeof phoneNumber !== 'string') {
        return phoneNumber || '';
    }
    
    // Remove any non-digit characters
    const digitsOnly = phoneNumber.replace(/\D/g, '');
    
    // If phone number is too short (less than 6 digits), return as-is
    if (digitsOnly.length < 6) {
        return phoneNumber;
    }
    
    // Show first 3 digits, mask middle with 5 asterisks, show last 2 digits
    const prefix = digitsOnly.slice(0, 3);
    const suffix = digitsOnly.slice(-2);
    return `${prefix}*****${suffix}`;
};

const maskEmail = (email) => {
    if (!email || typeof email !== 'string' || !email.includes('@')) {
        return email || '';
    }
    
    const [localPart, domain] = email.split('@');
    
    // If local part is too short, return as-is
    if (localPart.length <= 3) {
        return email;
    }
    
    // Show first 3 characters of local part, mask the rest
    const maskedLocal = localPart.slice(0, 3) + '***';
    
    // Mask domain but keep the extension
    const domainParts = domain.split('.');
    let maskedDomain;
    
    if (domainParts.length >= 2) {
        const mainDomain = domainParts[0];
        const extension = domainParts.slice(1).join('.');
        maskedDomain = '***' + extension;
    } else {
        maskedDomain = '***' + domain;
    }
    
    return `${maskedLocal}@${maskedDomain}`;
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

const getComplaintSeverityColor = (percentage) => {
    if (percentage >= 30) return 'text-red-600';
    if (percentage >= 15) return 'text-orange-600';
    return 'text-green-600';
};

// Overall rating card helper functions
const getStarColor = (starPosition, rating) => {
    if (!rating) return 'text-gray-300';
    
    const ratingNum = parseFloat(rating);
    if (starPosition <= Math.floor(ratingNum)) {
        return 'text-yellow-400'; // Full star
    } else if (starPosition === Math.ceil(ratingNum) && ratingNum % 1 !== 0) {
        return 'text-yellow-400'; // Half star (for now, treating as full)
    } else {
        return 'text-gray-300'; // Empty star
    }
};

const getChangeColor = (direction) => {
    if (!direction) return 'text-gray-600';
    
    switch (direction) {
        case 'increase': return 'text-green-600';
        case 'decrease': return 'text-red-600';
        case 'no_change': return 'text-gray-600';
        default: return 'text-gray-600';
    }
};

const formatChangeText = (change, direction) => {
    if (!change || !direction || direction === 'no_change') {
        return 'No change from last period';
    }
    
    const changeAbs = Math.abs(change);
    const prefix = direction === 'increase' ? '+' : '';
    return `${prefix}${changeAbs} point from last period`;
};

// Load last upload info using simplified API
const loadLastUploadInfo = async () => {
    loadingUploadInfo.value = true;
    try {
        const result = await CustomerService.getLatestUploadInfoSimple();
        if (result.success && result.data) {
            lastUploadInfo.value = result.data;
        } else {
            lastUploadInfo.value = null;
        }
    } catch (error) {
        console.error('Error loading latest upload info:', error);
        lastUploadInfo.value = null;
    } finally {
        loadingUploadInfo.value = false;
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

const formatUploadDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffHours < 1) {
        return 'Just now';
    } else if (diffHours < 24) {
        return `${diffHours} hours ago`;
    } else if (diffDays === 1) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else {
        return date.toLocaleDateString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
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