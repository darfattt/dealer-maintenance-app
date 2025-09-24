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
import DatePicker from 'primevue/datepicker';
import Tag from 'primevue/tag';
import Paginator from 'primevue/paginator';
import ProgressSpinner from 'primevue/progressspinner';
import Dialog from 'primevue/dialog';
import Textarea from 'primevue/textarea';
import SentimentAnalysisGAChart from '@/components/dashboard/SentimentAnalysisGAChart.vue';
import SentimentAnalysisGATotalReview from '@/components/dashboard/SentimentAnalysisGATotalReview.vue';
import GAProfile from '@/components/GAProfile.vue';
import GoogleReviewScrapingSidebar from '@/components/GoogleReviewScrapingSidebar.vue';
import GoogleReviewService from '@/service/GoogleReviewService';
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
const reviewsData = ref([]);
const statistics = ref(null);
const sentimentStatistics = ref(null);
const monthlyData = ref(null);
const loading = ref(false);
const loadingActions = ref({
    scraping: false,
    analyzing: false
});

// Dialog state for details popup
const showDetailsDialog = ref(false);
const selectedReview = ref(null);

// Sidebar state
const showScrapingSidebar = ref(false);

// Dealer selection state (for SUPER_ADMIN)
const selectedDealerId = ref(null);
const dealerOptions = ref([]);
const loadingDealers = ref(false);

// Filter state
const filters = reactive({
    no_ahass: '', // AHASS selection for SUPER_ADMIN
    reviewer_name: '',
    text_search: '',
    stars: null,
    date_from: null,
    date_to: null
});

const selectedDateFrom = ref(getCurrentMonthFirstDay());
const selectedDateTo = ref(getCurrentMonthLastDay());

// Pagination state
const pagination = reactive({
    page: 1,
    per_page: 10,
    total_items: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
});

// Role-based computed properties
const showAhassFilter = computed(() => authStore.userRole === 'SUPER_ADMIN');
const canManageReviews = computed(() => authStore.userRole === 'SUPER_ADMIN');
const isDealerUser = computed(() => authStore.userRole === 'DEALER_USER');

// Get current dealer ID (non-reactive for SUPER_ADMIN)
const currentDealerId = computed(() => {
    if (isDealerUser.value && authStore.userDealerId) {
        return authStore.userDealerId;
    }
    return selectedDealerId.value;
});

// Load dealer options for SUPER_ADMIN
const loadDealerOptions = async () => {
    if (!showAhassFilter.value) return; // Only for SUPER_ADMIN

    loadingDealers.value = true;
    try {
        const result = await CustomerService.getActiveDealers();
        if (result.success) {
            dealerOptions.value = result.data.map(dealer => ({
                label: dealer.dealer_name || dealer.dealer_id,
                value: dealer.dealer_id,
                dealer_id: dealer.dealer_id,
                dealer_name: dealer.dealer_name
            }));
        }
    } catch (error) {
        console.error('Error loading dealer options:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load dealer options',
            life: 3000
        });
    } finally {
        loadingDealers.value = false;
    }
};

// Computed properties for formatted dates
const formattedDateFrom = computed(() => {
    return selectedDateFrom.value ? formatDateForAPI(selectedDateFrom.value) : null;
});

const formattedDateTo = computed(() => {
    return selectedDateTo.value ? formatDateForAPI(selectedDateTo.value) : null;
});

// Load only reviews data (for search/pagination)
const loadReviewsOnly = async () => {
    if (!currentDealerId.value) {
        toast.add({
            severity: 'warn',
            summary: 'Warning',
            detail: 'Please select a dealer to view Google Reviews',
            life: 5000
        });
        return;
    }

    loading.value = true;
    try {
        // Prepare filters for API
        let apiFilters = {
            page: pagination.page,
            per_page: pagination.per_page,
            published_from: formattedDateFrom.value,
            published_to: formattedDateTo.value,
            sort_by: 'published_date',
            sort_order: 'desc'
        };

        if (filters.reviewer_name) {
            apiFilters.reviewer_name = filters.reviewer_name;
        }
        if (filters.text_search) {
            apiFilters.text_search = filters.text_search;
        }
        if (filters.stars) {
            apiFilters.stars = filters.stars;
        }

        // Load only reviews data
        const reviewsResult = await GoogleReviewService.getReviewsForDealer(currentDealerId.value, apiFilters);

        if (reviewsResult.success) {
            reviewsData.value = reviewsResult.reviews || [];
            const paginationData = reviewsResult.pagination || {};
            Object.assign(pagination, paginationData);
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: reviewsResult.message,
                life: 5000
            });
        }
    } catch (error) {
        console.error('Error loading Google Reviews data:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load Google Reviews data',
            life: 5000
        });
    } finally {
        loading.value = false;
    }
};

// Load only statistics data (for initial load/dealer change)
const loadStatisticsData = async () => {
    if (!currentDealerId.value) {
        console.warn('Cannot load statistics: no dealer selected');
        return;
    }

    console.log('Loading statistics for dealer:', currentDealerId.value);

    try {
        // Load statistics, sentiment statistics, and monthly data
        const [statsResult, sentimentResult, monthlyResult] = await Promise.all([
            GoogleReviewService.getReviewStatistics(currentDealerId.value),
            GoogleReviewService.getSentimentStatistics(currentDealerId.value),
            GoogleReviewService.getMonthlyReviewTotals(currentDealerId.value)
        ]);

        console.log('Statistics results:', { statsResult, sentimentResult, monthlyResult });

        if (statsResult.success) {
            statistics.value = statsResult.data;
            console.log('Statistics loaded:', statistics.value);
        } else {
            console.warn('Statistics failed:', statsResult);
        }

        if (sentimentResult.success) {
            sentimentStatistics.value = sentimentResult;
            console.log('Sentiment statistics loaded:', sentimentStatistics.value);
        } else {
            console.warn('Sentiment statistics failed:', sentimentResult);
        }

        if (monthlyResult.success) {
            monthlyData.value = monthlyResult;
            console.log('Monthly data loaded:', monthlyData.value);
        } else {
            console.warn('Monthly data failed:', monthlyResult);
        }
    } catch (error) {
        console.error('Error loading statistics data:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load statistics data',
            life: 5000
        });
    }
};

// Load all data (combination of reviews and statistics)
const loadAllData = async () => {
    if (!currentDealerId.value) {
        toast.add({
            severity: 'warn',
            summary: 'Warning',
            detail: 'Please select a dealer to view Google Reviews',
            life: 5000
        });
        return;
    }

    loading.value = true;
    try {
        // Prepare filters for API
        let apiFilters = {
            page: pagination.page,
            per_page: pagination.per_page,
            published_from: formattedDateFrom.value,
            published_to: formattedDateTo.value,
            sort_by: 'published_date',
            sort_order: 'desc'
        };

        if (filters.reviewer_name) {
            apiFilters.reviewer_name = filters.reviewer_name;
        }
        if (filters.text_search) {
            apiFilters.text_search = filters.text_search;
        }
        if (filters.stars) {
            apiFilters.stars = filters.stars;
        }

        // Load all data concurrently
        const [reviewsResult, statsResult, sentimentResult, monthlyResult] = await Promise.all([
            GoogleReviewService.getReviewsForDealer(currentDealerId.value, apiFilters),
            GoogleReviewService.getReviewStatistics(currentDealerId.value),
            GoogleReviewService.getSentimentStatistics(currentDealerId.value),
            GoogleReviewService.getMonthlyReviewTotals(currentDealerId.value)
        ]);

        // Process reviews result
        if (reviewsResult.success) {
            reviewsData.value = reviewsResult.reviews || [];
            const paginationData = reviewsResult.pagination || {};
            Object.assign(pagination, paginationData);
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: reviewsResult.message,
                life: 5000
            });
        }

        // Process statistics results
        if (statsResult.success) {
            statistics.value = statsResult.data;
        }

        if (sentimentResult.success) {
            sentimentStatistics.value = sentimentResult;
        }

        if (monthlyResult.success) {
            monthlyData.value = monthlyResult;
        }
    } catch (error) {
        console.error('Error loading all data:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load data',
            life: 5000
        });
    } finally {
        loading.value = false;
    }
};

// Legacy function for backward compatibility
const loadData = loadAllData;

// Manual search handler (only loads reviews, but loads statistics if dealer changes)
const handleSearch = () => {
    let dealerChanged = false;

    // For SUPER_ADMIN, update selected dealer from form field
    if (showAhassFilter.value && filters.no_ahass) {
        dealerChanged = selectedDealerId.value !== filters.no_ahass;
        selectedDealerId.value = filters.no_ahass;
    }

    pagination.page = 1; // Reset to first page when searching

    // Load reviews data
    loadReviewsOnly();

    // If dealer changed, also load statistics (independent of date filters)
    if (dealerChanged) {
        loadStatisticsData();
    }
};

// Pagination handler (only loads reviews, not statistics)
const onPageChange = (event) => {
    pagination.page = event.page + 1;
    loadReviewsOnly();
};

// Filter actions (only reloads reviews, not statistics)
const clearFilters = () => {
    // Only clear AHASS filter for SUPER_ADMIN
    if (showAhassFilter.value) {
        filters.no_ahass = '';
        selectedDealerId.value = null; // Clear selected dealer too
    }
    filters.reviewer_name = '';
    filters.text_search = '';
    filters.stars = null;
    // Reset to current month defaults instead of null
    selectedDateFrom.value = getCurrentMonthFirstDay();
    selectedDateTo.value = getCurrentMonthLastDay();
    pagination.page = 1;
    loadReviewsOnly();
};

// Sidebar handlers
const openScrapingSidebar = () => {
    showScrapingSidebar.value = true;
};

const handleScrapeSuccess = () => {
    // Refresh all data after successful scraping (affects both reviews and statistics)
    loadAllData();
};

// Legacy analyze sentiment action (kept for any existing usage)
const handleAnalyzeSentiment = async () => {
    if (!currentDealerId.value) {
        toast.add({
            severity: 'warn',
            summary: 'Warning',
            detail: 'Please select a dealer to analyze sentiment',
            life: 5000
        });
        return;
    }

    loadingActions.value.analyzing = true;
    try {
        const result = await GoogleReviewService.analyzeReviewsSentiment(currentDealerId.value, {
            limit: 50,
            batch_size: 10
        });

        if (result.success) {
            toast.add({
                severity: 'success',
                summary: 'Success',
                detail: result.message || 'Sentiment analysis completed',
                life: 5000
            });
            loadAllData(); // Refresh all data after analysis (affects both reviews and statistics)
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: result.message || 'Failed to analyze sentiment',
                life: 5000
            });
        }
    } catch (error) {
        console.error('Error analyzing sentiment:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to analyze sentiment',
            life: 5000
        });
    } finally {
        loadingActions.value.analyzing = false;
    }
};

// Date formatting utilities
const formatDate = (dateString) => {
    return formatIndonesiaDateTime(dateString);
};

const formatPublishedDate = (dateString) => {
    if (!dateString) return '-';
    try {
        return new Date(dateString).toLocaleDateString('id-ID', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch {
        return dateString;
    }
};

// Show details dialog
const showDetails = (review) => {
    selectedReview.value = review;
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

const getStarColor = (starPosition, rating) => {
    if (!rating) return 'text-gray-300';
    return starPosition <= rating ? 'text-yellow-400' : 'text-gray-300';
};

const parseSentimentThemes = (themesString) => {
    if (!themesString) return [];
    try {
        const themes = JSON.parse(themesString);
        return Array.isArray(themes) ? themes : [];
    } catch {
        return themesString.includes(',') ? themesString.split(',').map((theme) => theme.trim()) : [themesString.trim()];
    }
};

// Initialize
onMounted(async () => {
    // Load dealer options for SUPER_ADMIN
    if (showAhassFilter.value) {
        await loadDealerOptions();
    }

    // Auto-load all data if dealer is already selected (initial load)
    if (currentDealerId.value) {
        console.log('Loading all data for dealer:', currentDealerId.value);
        loadAllData();
    }
});
</script>

<template>
    <div class="space-y-6">
        <!-- Filter Controls -->
        <div class="flex justify-end items-center space-x-4 mb-6">
            <!-- Dealer Selection (Only for SUPER_ADMIN) -->
            <div v-if="showAhassFilter" class="flex items-center space-x-2">
                <label for="dealer-filter" class="text-sm font-medium">Dealer:</label>
                <Dropdown
                    id="dealer-filter"
                    v-model="filters.no_ahass"
                    :options="dealerOptions"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Select Dealer"
                    :loading="loadingDealers"
                    class="w-48"
                    :filter="true"
                    filterPlaceholder="Search dealers..."
                />
            </div>

            <!-- Text Search Filter -->
            <div class="flex items-center space-x-2">
                <InputText v-model="filters.text_search" placeholder="Search reviews..." class="w-40" />
            </div>

            <!-- Stars Filter -->
            <div class="flex items-center space-x-2">
                <label for="stars-filter" class="text-sm font-medium">Stars:</label>
                <select id="stars-filter" v-model="filters.stars" class="p-inputtext p-component w-20">
                    <option :value="null">All</option>
                    <option :value="5">5★</option>
                    <option :value="4">4★</option>
                    <option :value="3">3★</option>
                    <option :value="2">2★</option>
                    <option :value="1">1★</option>
                </select>
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

            <!-- Scraping Sidebar Toggle (Only for SUPER_ADMIN) -->
            <div v-if="canManageReviews" class="flex items-center space-x-2">
                <Button
                    @click="openScrapingSidebar"
                    label="Manage Scraping"
                    icon="pi pi-cog"
                    severity="info"
                    size="small"
                />
            </div>
        </div>

        <!-- 2-Column Layout: GAProfile and Overview Cards -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Left Column: Google Profile -->
            <div class="lg:col-span-1">
                <GAProfile :dealerId="currentDealerId" :loading="loading" />
            </div>

            <!-- Right Column: Overview Cards -->
            <div class="lg:col-span-1">
                <div class="grid grid-cols-1 gap-4">
                    <!-- Sentiment Analysis Chart -->
                    <SentimentAnalysisGAChart :stats="sentimentStatistics" :loading="loading" />

                    <!-- Monthly Review Totals Chart -->
                    <SentimentAnalysisGATotalReview :monthlyData="monthlyData" :loading="loading" />
                </div>
            </div>
        </div>

        <!-- Reviews Table -->
        <Card>
            <template #title>
                <h2 class="text-xl font-bold text-surface-900 dark:text-surface-0">Google Reviews</h2>
            </template>
            <template #content>
                <DataTable :value="reviewsData" :loading="loading" responsiveLayout="scroll" :paginator="false" dataKey="id" class="p-datatable-reviews">
                    <!-- No (Index) Column -->
                    <Column header="No" style="min-width: 60px">
                        <template #body="{ index }">
                            <span class="font-medium text-sm">
                                {{ (pagination.page - 1) * pagination.per_page + index + 1 }}
                            </span>
                        </template>
                    </Column>

                      <!-- Published Date Column -->
                      <Column field="published_at_date" header="Tanggal" style="min-width: 100px">
                        <template #body="{ data }">
                            <span class="text-sm">{{ formatPublishedDate(data.published_at_date) }}</span>
                        </template>
                    </Column>

                    <!-- Reviewer Name Column -->
                    <Column field="reviewer.name" header="Nama" style="min-width: 150px">
                        <template #body="{ data }">
                            <div class="flex items-center space-x-2">
                                <div>
                                    <div class="font-medium text-sm">{{ data.reviewer?.name || 'Anonymous' }}</div>
                                    <div v-if="data.reviewer?.number_of_reviews" class="text-xs text-surface-500">
                                        {{ data.reviewer.number_of_reviews }} reviews
                                    </div>
                                    <div v-if="data.reviewer?.is_local_guide" class="text-xs text-blue-600">Local Guide</div>
                                </div>
                            </div>
                        </template>
                    </Column>

                   
                    <!-- Review Text Column -->
                    <Column field="review_text" header="Review" style="min-width: 300px">
                        <template #body="{ data }">
                            <div class="text-sm">
                                <p v-if="data.review_text" class="cursor-help" v-tooltip.left="data.review_text">
                                    {{ data.review_text.length > 100 ? data.review_text.substring(0, 100) + '...' : data.review_text }}
                                </p>
                                <span v-else class="text-gray-400">N/A</span>
                            </div>
                        </template>
                    </Column>

                    

                    <!-- Sentiment Column -->
                    <Column field="sentiment_info.sentiment" header="Sentiment" style="min-width: 120px">
                        <template #body="{ data }">
                            <div v-if="data.sentiment_info?.sentiment" class="flex align-items-center gap-2">
                                <Tag :value="data.sentiment_info.sentiment" :severity="getSentimentSeverity(data.sentiment_info.sentiment)" class="text-xs" />
                                <div v-if="data.sentiment_info.sentiment_score" class="text-xs font-mono">
                                    {{ parseFloat(data.sentiment_info.sentiment_score).toFixed(1) }}
                                </div>
                            </div>
                            <span v-else class="text-gray-400 text-sm">-</span>
                        </template>
                    </Column>

                   <!-- Rating Column -->
                   <Column field="stars" header="Rating" style="min-width: 120px">
                        <template #body="{ data }">
                            <div v-if="data.stars" class="flex items-center space-x-2">
                                <Tag :value="data.stars" severity="info" class="text-xs" />
                                <div class="flex">
                                    <i v-for="star in 5" :key="star" class="pi pi-star-fill text-xs"
                                       :class="getStarColor(star, data.stars)"></i>
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
                <Paginator
                    :rows="pagination.per_page"
                    :totalRecords="pagination.total_items"
                    :rowsPerPageOptions="[10, 20, 50]"
                    @page="onPageChange"
                    class="mt-4"
                />
            </template>
        </Card>

        <!-- Details Dialog -->
        <Dialog v-model:visible="showDetailsDialog" :header="`Google Review Details`" :modal="true" :style="{ width: '80vw', maxWidth: '800px' }" class="review-details-dialog">
            <div v-if="selectedReview" class="space-y-4">
                <!-- Reviewer Info Section -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-4">
                        <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 border-b border-surface-200 dark:border-surface-700 pb-2">Reviewer Information</h4>

                        <div class="space-y-3">
                            <div class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Name:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right">{{ selectedReview.reviewer?.name || 'Anonymous' }}</span>
                            </div>
                            <div v-if="selectedReview.reviewer?.number_of_reviews" class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Total Reviews:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right">{{ selectedReview.reviewer.number_of_reviews }}</span>
                            </div>
                            <div class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Local Guide:</span>
                                <Tag :value="selectedReview.reviewer?.is_local_guide ? 'Yes' : 'No'"
                                     :severity="selectedReview.reviewer?.is_local_guide ? 'success' : 'secondary'"
                                     class="text-xs" />
                            </div>
                            <div class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Published:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right">{{ formatDate(selectedReview.published_at_date) }}</span>
                            </div>
                        </div>
                    </div>

                    <div class="space-y-4">
                        <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 border-b border-surface-200 dark:border-surface-700 pb-2">Review Details</h4>

                        <div class="space-y-3">
                            <div class="flex justify-between items-center">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Rating:</span>
                                <div class="flex items-center gap-2">
                                    <Tag v-if="selectedReview.stars" :value="selectedReview.stars" severity="info" class="text-xs" />
                                    <div v-if="selectedReview.stars" class="flex">
                                        <i v-for="star in 5" :key="star" class="pi pi-star-fill text-sm"
                                           :class="getStarColor(star, selectedReview.stars)"></i>
                                    </div>
                                    <span v-if="!selectedReview.stars" class="text-surface-500 dark:text-surface-400">-</span>
                                </div>
                            </div>
                            <div v-if="selectedReview.likes_count" class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Likes:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right">{{ selectedReview.likes_count }}</span>
                            </div>
                            <div v-if="selectedReview.visited_in" class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Visited In:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right">{{ selectedReview.visited_in }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Sentiment Analysis Section -->
                <div v-if="selectedReview.sentiment_info && (selectedReview.sentiment_info.sentiment || selectedReview.sentiment_info.sentiment_score || selectedReview.sentiment_info.sentiment_reasons)" class="space-y-3">
                    <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 border-b border-surface-200 dark:border-surface-700 pb-2">Sentiment Analysis</h4>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- Sentiment & Score -->
                        <div class="space-y-3">
                            <div v-if="selectedReview.sentiment_info.sentiment" class="flex justify-between items-center">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Sentiment:</span>
                                <Tag :value="selectedReview.sentiment_info.sentiment" :severity="getSentimentSeverity(selectedReview.sentiment_info.sentiment)" class="text-sm font-medium" />
                            </div>
                            <div v-if="selectedReview.sentiment_info.sentiment_score !== null && selectedReview.sentiment_info.sentiment_score !== undefined" class="flex justify-between items-center">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Sentiment Score:</span>
                                <span class="text-surface-900 dark:text-surface-100 font-mono text-lg">
                                    {{ parseFloat(selectedReview.sentiment_info.sentiment_score).toFixed(2) }}
                                </span>
                            </div>
                            <div v-if="selectedReview.sentiment_info.sentiment_analyzed_at" class="flex justify-between items-start">
                                <span class="font-medium text-surface-600 dark:text-surface-400">Analyzed At:</span>
                                <span class="text-surface-900 dark:text-surface-100 text-right text-sm">
                                    {{ formatDate(selectedReview.sentiment_info.sentiment_analyzed_at) }}
                                </span>
                            </div>
                        </div>

                        <!-- Themes -->
                        <div v-if="selectedReview.sentiment_info.sentiment_themes" class="space-y-2">
                            <span class="font-medium text-surface-600 dark:text-surface-400">Themes:</span>
                            <div class="flex flex-wrap gap-1">
                                <Tag v-for="theme in parseSentimentThemes(selectedReview.sentiment_info.sentiment_themes)"
                                     :key="theme" :value="theme" severity="secondary" class="text-xs" />
                            </div>
                        </div>
                    </div>

                    <!-- Reasons -->
                    <div v-if="selectedReview.sentiment_info.sentiment_reasons" class="space-y-2">
                        <span class="font-medium text-surface-600 dark:text-surface-400">Analysis Reasons:</span>
                        <p class="text-surface-900 dark:text-surface-100 text-sm bg-surface-50 dark:bg-surface-800 p-3 rounded-lg border border-surface-200 dark:border-surface-600 leading-relaxed">
                            {{ selectedReview.sentiment_info.sentiment_reasons }}
                        </p>
                    </div>

                    <!-- Suggestions -->
                    <div v-if="selectedReview.sentiment_info.sentiment_suggestion" class="space-y-2">
                        <span class="font-medium text-surface-600 dark:text-surface-400">AI Suggestions:</span>
                        <p class="text-surface-900 dark:text-surface-100 text-sm bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg border border-blue-200 dark:border-blue-800 leading-relaxed">
                            {{ selectedReview.sentiment_info.sentiment_suggestion }}
                        </p>
                    </div>
                </div>

                <!-- Owner Response Section -->
                <div v-if="selectedReview.owner_response?.text" class="space-y-3">
                    <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 border-b border-surface-200 dark:border-surface-700 pb-2">Owner Response</h4>
                    <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
                        <p class="text-sm text-surface-900 dark:text-surface-100 leading-relaxed whitespace-pre-wrap">
                            {{ selectedReview.owner_response.text }}
                        </p>
                        <div v-if="selectedReview.owner_response.date" class="text-xs text-surface-500 dark:text-surface-400 mt-2">
                            Response date: {{ formatDate(selectedReview.owner_response.date) }}
                        </div>
                    </div>
                </div>

                <!-- Full Review Text Section -->
                <div class="space-y-3">
                    <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 border-b border-surface-200 dark:border-surface-700 pb-2">Full Review</h4>
                    <div class="bg-surface-50 dark:bg-surface-800 p-4 rounded-lg border border-surface-200 dark:border-surface-600 max-h-64 overflow-y-auto">
                        <p class="text-sm text-surface-900 dark:text-surface-100 leading-relaxed whitespace-pre-wrap">
                            {{ selectedReview.review_text || 'No review text available' }}
                        </p>
                    </div>
                </div>

                <!-- Additional Data Section -->
                <div v-if="selectedReview.created_at || selectedReview.updated_at" class="space-y-3">
                    <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 border-b border-surface-200 dark:border-surface-700 pb-2">System Information</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div v-if="selectedReview.created_at" class="flex justify-between">
                            <span class="font-medium text-surface-600 dark:text-surface-400">Scraped:</span>
                            <span class="text-surface-900 dark:text-surface-100">{{ formatDate(selectedReview.created_at) }}</span>
                        </div>
                        <div v-if="selectedReview.updated_at" class="flex justify-between">
                            <span class="font-medium text-surface-600 dark:text-surface-400">Updated:</span>
                            <span class="text-surface-900 dark:text-surface-100">{{ formatDate(selectedReview.updated_at) }}</span>
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

        <!-- Google Review Scraping Sidebar -->
        <GoogleReviewScrapingSidebar
            :visible="showScrapingSidebar"
            @update:visible="showScrapingSidebar = $event"
            @scrape-success="handleScrapeSuccess"
        />
    </div>
</template>

<style scoped>
/* Custom styles for the Google Reviews page */

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
@media (max-width: 1024px) {
    .grid.lg\\:grid-cols-2 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
    }
}

@media (max-width: 768px) {
    .grid.md\\:grid-cols-2 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
    }
}

/* Table responsive styling */
:deep(.p-datatable-reviews .p-datatable-tbody > tr > td) {
    padding: 0.75rem 1rem;
}

:deep(.p-datatable-reviews .p-datatable-thead > tr > th) {
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

/* Select input styling */
select.p-inputtext {
    appearance: none;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
    background-position: right 0.5rem center;
    background-repeat: no-repeat;
    background-size: 1.5em 1.5em;
    padding-right: 2.5rem;
}
</style>