<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useAuthStore } from '@/stores/auth';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import DatePicker from 'primevue/datepicker';
import Tag from 'primevue/tag';
import Paginator from 'primevue/paginator';
import ProgressSpinner from 'primevue/progressspinner';
import ProgressBar from 'primevue/progressbar';
import Dialog from 'primevue/dialog';
import CustomerSatisfactionUploadSidebar from '@/components/CustomerSatisfactionUploadSidebar.vue';
import SentimentAnalysisChart from '@/components/dashboard/SentimentAnalysisChart.vue';
import SentimentThemesWordCloud from '@/components/dashboard/SentimentThemesWordCloud.vue';
import CustomerService from '@/service/CustomerService';
import { formatIndonesiaDateTime, formatRelativeTime, formatDateForAPI, getCurrentMonthIndonesia } from '@/utils/dateFormatter';

const authStore = useAuthStore();
const toast = useToast();

// Date utility functions for current month defaults (using Indonesia timezone)
const getCurrentMonthFirstDay = () => {
    const { firstDay } = getCurrentMonthIndonesia();
    return firstDay;
};

const getCurrentMonthLastDay = () => {
    const { lastDay } = getCurrentMonthIndonesia();
    return lastDay;
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
const sentimentStatistics = ref(null);
const sentimentThemesStatistics = ref(null);
const searchTrigger = ref(0);

// Dialog state for details popup
const showDetailsDialog = ref(false);
const selectedRecord = ref(null);

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

// Computed properties for formatted dates
const formattedDateFrom = computed(() => {
    return selectedDateFrom.value ? formatDateForAPI(selectedDateFrom.value) : null;
});

const formattedDateTo = computed(() => {
    return selectedDateTo.value ? formatDateForAPI(selectedDateTo.value) : null;
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

        // Load records, statistics, top complaints, overall rating, sentiment statistics, and themes statistics
        const [recordsResult, statsResult, complaintsResult, ratingResult, sentimentResult, themesResult] = await Promise.all([
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
            }),
            CustomerService.getSentimentStatistics({
                periode_utk_suspend: apiFilters.periode_utk_suspend,
                submit_review_date: apiFilters.submit_review_date,
                no_ahass: apiFilters.no_ahass,
                date_from: apiFilters.date_from,
                date_to: apiFilters.date_to
            }),
            CustomerService.getSentimentThemesStatistics({
                periode_utk_suspend: apiFilters.periode_utk_suspend,
                submit_review_date: apiFilters.submit_review_date,
                no_ahass: apiFilters.no_ahass,
                dateFrom: apiFilters.date_from,
                dateTo: apiFilters.date_to
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

        if (sentimentResult.success) {
            sentimentStatistics.value = sentimentResult.data || null;
        }

        if (themesResult.success) {
            sentimentThemesStatistics.value = themesResult.data || null;
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
    searchTrigger.value++; // Increment to trigger word cloud refresh
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

// Utilities (using Indonesia timezone-aware formatDateForAPI from utils)

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
        case 'increase':
            return 'text-green-600';
        case 'decrease':
            return 'text-red-600';
        case 'no_change':
            return 'text-gray-600';
        default:
            return 'text-gray-600';
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

// Date formatting utilities (using Indonesia timezone)
const formatDate = (dateString) => {
    return formatIndonesiaDateTime(dateString);
};

const formatUploadDate = (dateString) => {
    return formatRelativeTime(dateString);
};

// Show details dialog
const showDetails = (record) => {
    selectedRecord.value = record;
    showDetailsDialog.value = true;
};

// Sentiment utilities
const getSentimentSeverity = (sentiment) => {
    if (!sentiment) return 'secondary';
    switch (sentiment.toLowerCase()) {
        case 'positive':
            return 'success';
        case 'negative':
            return 'danger';
        case 'neutral':
            return 'warning';
        default:
            return 'secondary';
    }
};

const parseSentimentThemes = (themesString) => {
    if (!themesString) return [];
    try {
        // Try to parse as JSON array
        const themes = JSON.parse(themesString);
        return Array.isArray(themes) ? themes : [];
    } catch {
        // If not JSON, split by comma or return as single item
        return themesString.includes(',') ? themesString.split(',').map((theme) => theme.trim()) : [themesString.trim()];
    }
};

// Initialize
onMounted(() => {
    loadData();
    loadLastUploadInfo();
});
</script>

<template>
    <div class="space-y-6">
        <!-- Filter Controls -->
        <div class="flex justify-end items-center space-x-4 mb-6">
            <!-- No AHASS Filter (Only for SUPER_ADMIN) -->
            <div v-if="showAhassFilter" class="flex items-center space-x-2">
                <label for="ahass-filter" class="text-sm font-medium">No AHASS:</label>
                <InputText id="ahass-filter" v-model="filters.no_ahass" placeholder="Enter No AHASS" class="w-36" />
            </div>

            <!-- Date Range Filters -->
            <div class="flex items-center space-x-2">
                <DatePicker v-model="selectedDateFrom" dateFormat="dd-mm-yy" placeholder="From Date" class="w-36" showIcon />
                <span class="text-sm text-muted-color">to</span>
                <DatePicker v-model="selectedDateTo" dateFormat="dd-mm-yy" placeholder="To Date" class="w-36" showIcon />
            </div>

            <!-- Search and Clear Buttons -->
            <div class="flex items-center space-x-2">
                <Button @click="handleSearch" icon="pi pi-search" severity="primary" size="small" title="Search" />
                <Button @click="clearFilters" icon="pi pi-times" severity="secondary" size="small" title="Clear Filters" />
            </div>

            <!-- Upload Button (Only for SUPER_ADMIN) -->
            <Button v-if="canUpload" @click="showUploadSidebar = true" label="Upload File" icon="pi pi-upload" severity="success" size="small" />
        </div>

        <!-- Overview Section -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <!-- Sentiment Analysis Chart -->
            <SentimentAnalysisChart :stats="sentimentStatistics" :loading="loading" />

            <!-- Sentiment Themes Word Cloud -->
            <SentimentThemesWordCloud :themes="sentimentThemesStatistics" :loading="loading" />

            <!-- Top Complaints Card -->
            <!-- <Card class="text-center">
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
            </Card> -->

            <!-- Overall Rating Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="loading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px" />
                    </div>
                    <div v-else>
                        <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-3">Overall Rating</h3>

                        <div class="mb-4">
                            <!-- Main Rating Display -->
                            <div class="flex items-center justify-center space-x-3 mb-3">
                                <span class="text-6xl font-bold text-surface-900 dark:text-surface-0">
                                    {{ overallRating?.current_rating || '-' }}
                                </span>
                                <div class="flex items-center">
                                    <!-- Star Rating Display -->
                                    <div class="flex mr-2">
                                        <i v-for="star in 5" :key="star" class="pi pi-star-fill text-lg" :class="getStarColor(star, overallRating?.current_rating)"></i>
                                    </div>
                                    <span class="text-base text-surface-600 dark:text-surface-400 font-medium">/ 5.0</span>
                                </div>
                            </div>
                        </div>

                        <!-- Month-over-Month Comparison -->
                        <div v-if="overallRating?.change !== null && overallRating?.change_direction" class="text-base">
                            <span :class="getChangeColor(overallRating?.change_direction)" class="font-medium">
                                {{ formatChangeText(overallRating?.change, overallRating?.change_direction) }}
                            </span>
                        </div>
                        <div v-else class="text-base text-surface-500 dark:text-surface-400">Tidak ada perbandingan data dengan bulan lalu</div>
                    </div>
                </template>
            </Card>

            <!-- Total Reviews Card -->
            <Card class="text-center">
                <template #content>
                    <div v-if="loading" class="flex justify-center">
                        <ProgressSpinner style="width: 30px; height: 30px" />
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
                <DataTable :value="satisfactionData" :loading="loading" responsiveLayout="scroll" :paginator="false" dataKey="id" class="p-datatable-customers">
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
                    <!-- <Column field="alamat_email" header="Alamat Email" style="min-width: 150px">
                        <template #body="{ data }">
                            <span class="text-sm font-mono">{{ maskEmail(data.alamat_email) || '-' }}</span>
                        </template>
                    </Column> -->

                    <!-- Kota Column -->
                    <!-- <Column field="kota" header="Kota" style="min-width: 120px">
                        <template #body="{ data }">
                            <span class="text-sm">{{ data.kota || '-' }}</span>
                        </template>
                    </Column> -->

                    <!-- Inbox Column -->
                    <Column field="inbox" header="Inbox" style="min-width: 200px">
                        <template #body="{ data }">
                            <span class="text-sm cursor-help" v-tooltip.left="data.inbox || 'No inbox data'">
                                {{ data.inbox ? (data.inbox.length > 50 ? data.inbox.substring(0, 50) + '...' : data.inbox) : '-' }}
                            </span>
                        </template>
                    </Column>

                    <!-- Sentiment Column -->
                    <Column field="sentiment" header="Sentiment" style="min-width: 120px">
                        <template #body="{ data }">
                            <div v-if="data.sentiment" class="flex align-items-center gap-2">
                                <Tag :value="data.sentiment" :severity="getSentimentSeverity(data.sentiment)" class="text-xs" />
                            </div>
                            <span v-else class="text-gray-400 text-sm">-</span>
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
                                <Tag :value="data.rating" :severity="getRatingSeverity(data.rating)" class="text-xs" />
                                <div class="flex">
                                    <i v-for="star in 5" :key="star" class="pi pi-star-fill text-xs" :class="star <= parseInt(data.rating) ? 'text-yellow-400' : 'text-gray-300'"></i>
                                </div>
                            </div>
                            <span v-else class="text-gray-400">-</span>
                        </template>
                    </Column>

                    <!-- Action Column -->
                    <Column header="Action" style="min-width: 80px">
                        <template #body="{ data }">
                            <Button @click="showDetails(data)" icon="pi pi-eye" severity="info" size="small" outlined title="View Details" class="p-button-sm" />
                        </template>
                    </Column>
                </DataTable>

                <!-- Pagination -->
                <Paginator :rows="pagination.page_size" :totalRecords="pagination.total_count" :rowsPerPageOptions="[10, 20, 50]" @page="onPageChange" class="mt-4" />

                <!-- Simplified Latest Upload Info -->
                <div v-if="lastUploadInfo" class="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-surface-700 dark:to-surface-800 rounded-xl border border-blue-200 dark:border-surface-600 shadow-sm">
                    <div class="flex items-center space-x-3">
                        <div class="flex items-center justify-center w-10 h-10 bg-blue-500 dark:bg-blue-600 text-white rounded-full">
                            <i class="pi pi-calendar text-lg"></i>
                        </div>
                        <div class="flex-1">
                            <h4 class="text-lg font-semibold text-surface-800 dark:text-surface-200 mb-1">Latest Upload</h4>
                            <div class="text-sm text-surface-600 dark:text-surface-400">
                                <span>{{ formatUploadDate(lastUploadInfo.latest_upload_date) }}</span>
                            </div>

                            <!-- Sentiment Analysis Processing Indicator -->
                            <div v-if="lastUploadInfo.sentiment_analysis && lastUploadInfo.sentiment_analysis.is_processing" class="mt-3 space-y-2">
                                <div class="flex items-center space-x-2">
                                    <ProgressSpinner size="small" style="width: 16px; height: 16px" />
                                    <span class="text-sm font-medium text-surface-700 dark:text-surface-300"> Sentiment Analysis in Progress </span>
                                </div>
                                <div class="space-y-1">
                                    <div class="flex justify-between text-xs text-surface-600 dark:text-surface-400">
                                        <span>{{ lastUploadInfo.sentiment_analysis.processed_records }} / {{ lastUploadInfo.sentiment_analysis.total_records }} processed</span>
                                        <span>{{ lastUploadInfo.sentiment_analysis.processing_progress }}%</span>
                                    </div>
                                    <ProgressBar :value="lastUploadInfo.sentiment_analysis.processing_progress" :showValue="false" style="height: 6px" class="w-full" />
                                </div>
                                <div v-if="lastUploadInfo.sentiment_analysis.last_processed_at" class="text-xs text-surface-500 dark:text-surface-400">Last processed: {{ formatDate(lastUploadInfo.sentiment_analysis.last_processed_at) }}</div>
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

        <!-- Details Dialog -->
        <Dialog v-model:visible="showDetailsDialog" :header="`Customer Satisfaction Details - ${selectedRecord?.no_tiket || 'N/A'}`" :modal="true" :style="{ width: '80vw', maxWidth: '800px' }" class="customer-details-dialog">
            <div v-if="selectedRecord" class="space-y-4">
                <!-- Customer Info Section -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-4">
                        <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 border-b border-surface-200 dark:border-surface-700 pb-2">Customer Information</h4>

                        <div class="space-y-3">
                            <div class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">No Tiket:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right">{{ selectedRecord.no_tiket || '-' }}</span>
                            </div>
                            <div class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Nama Konsumen:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right">{{ selectedRecord.nama_konsumen || '-' }}</span>
                            </div>
                            <div class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">No HP:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right font-mono">{{ maskPhoneNumber(selectedRecord.no_hp) || '-' }}</span>
                            </div>
                            <div class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Alamat Email:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right font-mono break-all">{{ maskEmail(selectedRecord.alamat_email) || '-' }}</span>
                            </div>
                            <div class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Kota:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right">{{ selectedRecord.kota || '-' }}</span>
                            </div>
                            <div v-if="showAhassFilter" class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">No AHASS:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right">{{ selectedRecord.no_ahass || '-' }}</span>
                            </div>
                        </div>
                    </div>

                    <div class="space-y-4">
                        <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 border-b border-surface-200 dark:border-surface-700 pb-2">Rating & Review</h4>

                        <div class="space-y-3">
                            <div class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Tanggal Rating:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right">{{ selectedRecord.tanggal_rating || '-' }}</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Rating:</span>
                                <div class="flex items-center gap-2">
                                    <Tag v-if="selectedRecord.rating" :value="selectedRecord.rating" :severity="getRatingSeverity(selectedRecord.rating)" class="text-xs" />
                                    <div v-if="selectedRecord.rating" class="flex">
                                        <i v-for="star in 5" :key="star" class="pi pi-star-fill text-sm" :class="star <= parseInt(selectedRecord.rating) ? 'text-yellow-400' : 'text-gray-300'"></i>
                                    </div>
                                    <span v-if="!selectedRecord.rating" class="text-surface-500 dark:text-surface-400">-</span>
                                </div>
                            </div>
                            <div class="space-y-2">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Indikasi Keluhan:</span>
                                <p class="text-surface-900 dark:text-surface-100 text-sm bg-surface-50 dark:bg-surface-800 p-3 rounded-lg border border-surface-200 dark:border-surface-600">
                                    {{ selectedRecord.indikasi_keluhan || 'No complaint indication' }}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Sentiment Analysis Section -->
                <div v-if="selectedRecord && (selectedRecord.sentiment || selectedRecord.sentiment_score || selectedRecord.sentiment_reasons)" class="space-y-3">
                    <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 border-b border-surface-200 dark:border-surface-700 pb-2">Sentiment Analysis</h4>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- Sentiment & Score -->
                        <div class="space-y-3">
                            <div v-if="selectedRecord.sentiment" class="flex justify-between items-center">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Sentiment:</span>
                                <Tag :value="selectedRecord.sentiment" :severity="getSentimentSeverity(selectedRecord.sentiment)" class="text-sm font-medium" />
                            </div>
                            <div v-if="selectedRecord.sentiment_score !== null && selectedRecord.sentiment_score !== undefined" class="flex justify-between items-center">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Sentiment Score:</span>
                                <span class="text-surface-900 dark:text-surface-100 font-mono text-lg">
                                    {{ parseFloat(selectedRecord.sentiment_score).toFixed(2) }}
                                </span>
                            </div>
                            <div v-if="selectedRecord.sentiment_analyzed_at" class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Analyzed At:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right text-sm">
                                    {{ formatDate(selectedRecord.sentiment_analyzed_at) }}
                                </span>
                            </div>
                        </div>

                        <!-- Themes -->
                        <div v-if="selectedRecord.sentiment_themes" class="space-y-2">
                            <span class="font-medium text-surface-600 dark:text-surface-400">Themes:</span>
                            <div class="flex flex-wrap gap-1">
                                <Tag v-for="theme in parseSentimentThemes(selectedRecord.sentiment_themes)" :key="theme" :value="theme" severity="secondary" class="text-xs" />
                            </div>
                        </div>
                    </div>

                    <!-- Reasons -->
                    <div v-if="selectedRecord.sentiment_reasons" class="space-y-2">
                        <span class="font-medium text-surface-600 dark:text-surface-400">Analysis Reasons:</span>
                        <p class="text-surface-900 dark:text-surface-100 text-sm bg-surface-50 dark:bg-surface-800 p-3 rounded-lg border border-surface-200 dark:border-surface-600 leading-relaxed">
                            {{ selectedRecord.sentiment_reasons }}
                        </p>
                    </div>

                    <!-- Suggestions -->
                    <div v-if="selectedRecord.sentiment_suggestion" class="space-y-2">
                        <span class="font-medium text-surface-600 dark:text-surface-400">AI Suggestions:</span>
                        <p class="text-surface-900 dark:text-surface-100 text-sm bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg border border-blue-200 dark:border-blue-800 leading-relaxed">
                            {{ selectedRecord.sentiment_suggestion }}
                        </p>
                    </div>
                </div>

                <!-- Full Inbox/Review Section -->
                <div class="space-y-3">
                    <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 border-b border-surface-200 dark:border-surface-700 pb-2">Full Review</h4>
                    <div class="bg-surface-50 dark:bg-surface-800 p-4 rounded-lg border border-surface-200 dark:border-surface-600 max-h-64 overflow-y-auto">
                        <p class="text-sm text-surface-900 dark:text-surface-100 leading-relaxed whitespace-pre-wrap">
                            {{ selectedRecord.inbox || 'No review content available' }}
                        </p>
                    </div>
                </div>

                <!-- Additional Data Section (if any) -->
                <div v-if="selectedRecord.created_date || selectedRecord.updated_date" class="space-y-3">
                    <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 border-b border-surface-200 dark:border-surface-700 pb-2">System Information</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div v-if="selectedRecord.created_date" class="flex justify-between">
                            <span class="font-medium text-surface-600 dark:text-surface-400">Created:</span>
                            <span class="text-surface-900 dark:text-surface-100">{{ formatDate(selectedRecord.created_date) }}</span>
                        </div>
                        <div v-if="selectedRecord.updated_date" class="flex justify-between">
                            <span class="font-medium text-surface-600 dark:text-surface-400">Updated:</span>
                            <span class="text-surface-900 dark:text-surface-100">{{ formatDate(selectedRecord.updated_date) }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <template #footer>
                <div class="flex justify-end">
                    <Button @click="showDetailsDialog = false" label="Close" icon="pi pi-times" severity="secondary" autofocus />
                </div>
            </template>
        </Dialog>

        <!-- Upload Sidebar -->
        <CustomerSatisfactionUploadSidebar v-model:visible="showUploadSidebar" @upload-success="onUploadSuccess" />
    </div>
</template>

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
