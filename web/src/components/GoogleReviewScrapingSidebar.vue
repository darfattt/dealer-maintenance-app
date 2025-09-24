<script setup>
import { ref, watch, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import Sidebar from 'primevue/sidebar';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import InputNumber from 'primevue/inputnumber';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';
import Checkbox from 'primevue/checkbox';
import GoogleReviewService from '@/service/GoogleReviewService';
import CustomerService from '@/service/CustomerService';
import { formatIndonesiaDate, formatIndonesiaDateTime, formatDateForAPI, getCurrentMonthIndonesia, formatIndonesiaTime } from '@/utils/dateFormatter';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['update:visible', 'scrape-success']);

const toast = useToast();

// Scraping state
const selectedDealer = ref(null);
const maxReviews = ref(10);
const language = ref('id');
const analyzeSentiment = ref(true);
const scraping = ref(false);
const scrapeResult = ref(null);

// Dealer options
const dealerOptions = ref([]);
const loadingDealers = ref(false);

// History state
const showHistory = ref(true);
const loadingHistory = ref(false);
const scrapeHistory = ref([]);

// Load dealer options from CustomerService
const loadDealerOptions = async () => {
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

// Scrape reviews
const scrapeReviews = async () => {
    if (!selectedDealer.value) {
        toast.add({
            severity: 'warn',
            summary: 'Warning',
            detail: 'Please select a dealer first',
            life: 3000
        });
        return;
    }

    scraping.value = true;
    scrapeResult.value = null;

    try {
        const result = await GoogleReviewService.scrapeReviews({
            dealer_id: selectedDealer.value,
            max_reviews: maxReviews.value,
            language: language.value,
            auto_analyze_sentiment: analyzeSentiment.value
        });

        if (result.success) {
            scrapeResult.value = result;
            toast.add({
                severity: 'success',
                summary: 'Success',
                detail: result.message,
                life: 5000
            });

            // Refresh history and emit success event
            await refreshHistory();
            emit('scrape-success');
        } else {
            toast.add({
                severity: 'error',
                summary: 'Scraping Failed',
                detail: result.message,
                life: 5000
            });
        }
    } catch (error) {
        console.error('Scraping error:', error);
        toast.add({
            severity: 'error',
            summary: 'Scraping Error',
            detail: error.response?.data?.detail || 'An error occurred during scraping',
            life: 5000
        });
    } finally {
        scraping.value = false;
    }
};

// Manual sentiment analysis
const analyzeSentimentManually = async () => {
    if (!selectedDealer.value) {
        toast.add({
            severity: 'warn',
            summary: 'Warning',
            detail: 'Please select a dealer first',
            life: 3000
        });
        return;
    }

    // Show immediate info message that analysis is starting in background
    toast.add({
        severity: 'info',
        summary: 'Processing',
        detail: 'Sentiment analysis started in background. This may take a few minutes to complete.',
        life: 5000
    });

    // Start sentiment analysis in background (fire and forget)
    GoogleReviewService.analyzeSentiment({
        dealer_id: selectedDealer.value,
        limit: 100,
        batch_size: 10
    }).then(result => {
        console.log('Background sentiment analysis completed:', result);
    }).catch(error => {
        console.error('Background sentiment analysis error:', error);
    });
};

// Scraping history
const refreshHistory = async () => {
    loadingHistory.value = true;
    try {
        const result = await GoogleReviewService.getScrapeHistory({
            page: 1,
            per_page: 5
        });

        if (result.success) {
            scrapeHistory.value = result.trackers || [];
        }
    } catch (error) {
        console.error('Error fetching scrape history:', error);
    } finally {
        loadingHistory.value = false;
    }
};

// Utilities
const formatDate = (dateString) => {
    return formatIndonesiaDateTime(dateString);
};

const getStatusSeverity = (status) => {
    switch (status) {
        case 'COMPLETED':
            return 'success';
        case 'FAILED':
            return 'danger';
        case 'PROCESSING':
            return 'info';
        case 'PARTIAL':
            return 'warning';
        default:
            return 'secondary';
    }
};

const getSentimentStatusSeverity = (status) => {
    switch (status) {
        case 'COMPLETED':
            return 'success';
        case 'FAILED':
            return 'danger';
        case 'PROCESSING':
            return 'info';
        case 'PENDING':
            return 'warning';
        default:
            return 'secondary';
    }
};

// Watch visibility to load data when sidebar opens
watch(
    () => props.visible,
    (newVisible) => {
        if (newVisible) {
            loadDealerOptions();
            if (showHistory.value) {
                refreshHistory();
            }
        }
    }
);

// Load data on mount
onMounted(() => {
    if (props.visible) {
        loadDealerOptions();
        if (showHistory.value) {
            refreshHistory();
        }
    }
});
</script>

<template>
    <Sidebar :visible="visible" position="right" :style="{ width: '400px' }" @update:visible="$emit('update:visible', $event)" header="Google Reviews Scraping" :modal="false">
        <div class="flex flex-col gap-4 h-full">
            <!-- Scraping Configuration Section -->
            <Card>
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-google text-primary"></i>
                        <span>Scrape Reviews</span>
                    </div>
                </template>
                <template #content>
                    <div class="space-y-4">
                        <!-- Dealer Selection -->
                        <div>
                            <label for="dealer-dropdown" class="block text-sm font-medium text-gray-700 mb-2">
                                Select Dealer
                            </label>
                            <Dropdown
                                id="dealer-dropdown"
                                v-model="selectedDealer"
                                :options="dealerOptions"
                                optionLabel="label"
                                optionValue="value"
                                placeholder="Choose a dealer"
                                :loading="loadingDealers"
                                class="w-full"
                                :filter="true"
                                filterPlaceholder="Search dealers..."
                            />
                        </div>

                        <!-- Max Reviews -->
                        <div>
                            <label for="max-reviews" class="block text-sm font-medium text-gray-700 mb-2">
                                Max Reviews
                            </label>
                            <InputNumber
                                id="max-reviews"
                                v-model="maxReviews"
                                :min="1"
                                :max="50"
                                class="w-full"
                                placeholder="Number of reviews to scrape"
                            />
                            <small class="text-gray-500">Maximum 50 reviews per scrape</small>
                        </div>


                        <!-- Analyze Sentiment Option -->
                        <div class="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                            <Checkbox v-model="analyzeSentiment" inputId="sentiment-checkbox" :binary="true" />
                            <div class="flex-1">
                                <label for="sentiment-checkbox" class="text-sm font-medium text-blue-800 cursor-pointer">
                                    Analyze Sentiment
                                </label>
                                <p class="text-xs text-blue-600 mt-1">
                                    Automatically analyze sentiment after scraping reviews
                                </p>
                            </div>
                        </div>

                        <!-- Scraping Instructions -->
                        <div class="p-3 bg-green-50 rounded-lg border border-green-200">
                            <div class="text-xs text-green-800">
                                <strong>Requirements:</strong> Dealer must have Google location URL configured<br />
                                <strong>Language:</strong> Indonesian (default)<br />
                                <strong>Sentiment:</strong> Optional automatic analysis after scraping<br />
                                <strong>Rate Limit:</strong> Max 50 reviews per request
                            </div>
                        </div>

                        <!-- Scrape Button -->
                        <Button
                            @click="scrapeReviews"
                            :disabled="!selectedDealer || scraping"
                            :loading="scraping"
                            label="Scrape Reviews"
                            icon="pi pi-download"
                            class="w-full"
                            severity="success"
                        />

                        <!-- Manual Sentiment Analysis -->
                        <Button
                            @click="analyzeSentimentManually"
                            :disabled="!selectedDealer"
                            label="Analyze Sentiment"
                            icon="pi pi-chart-line"
                            class="w-full"
                            severity="info"
                            outlined
                        />
                    </div>
                </template>
            </Card>

            <!-- Scraping Result -->
            <Card v-if="scrapeResult">
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-info-circle text-info"></i>
                        <span>Scraping Result</span>
                    </div>
                </template>
                <template #content>
                    <div class="space-y-2">
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">Status:</span>
                            <Tag :value="scrapeResult.data?.scraping_status || 'UNKNOWN'" :severity="getStatusSeverity(scrapeResult.data?.scraping_status)" />
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">Business:</span>
                            <span class="text-sm">{{ scrapeResult.data?.business_name || 'N/A' }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">Total Available:</span>
                            <span class="text-sm">{{ scrapeResult.data?.reviews_count || 0 }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">Scraped:</span>
                            <span class="text-sm text-green-600">{{ scrapeResult.data?.scraped_reviews_count || 0 }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">New Reviews:</span>
                            <span class="text-sm text-blue-600">{{ scrapeResult.data?.new_reviews_count || 0 }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">Rating:</span>
                            <span class="text-sm">{{ scrapeResult.data?.total_score || 'N/A' }}</span>
                        </div>
                        <div v-if="scrapeResult.data?.auto_analyze_sentiment" class="flex justify-between">
                            <span class="text-sm font-medium">Sentiment:</span>
                            <Tag :value="scrapeResult.data?.sentiment_status || 'PENDING'" :severity="getSentimentStatusSeverity(scrapeResult.data?.sentiment_status)" class="text-xs" />
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Scraping History -->
            <Card v-if="showHistory">
                <template #title>
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-history text-secondary"></i>
                            <span>Recent Scrapes</span>
                        </div>
                        <Button @click="refreshHistory" icon="pi pi-refresh" size="small" text />
                    </div>
                </template>
                <template #content>
                    <div v-if="loadingHistory" class="text-center py-4">
                        <ProgressSpinner style="width: 30px; height: 30px" />
                    </div>
                    <div v-else-if="scrapeHistory.length === 0" class="text-center py-4 text-gray-500 text-sm">No recent scrapes</div>
                    <div v-else class="space-y-2 max-h-60 overflow-y-auto">
                        <div v-for="scrape in scrapeHistory" :key="scrape.id" class="p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                            <div class="flex justify-between items-start">
                                <div class="flex-1 min-w-0">
                                    <div class="text-sm font-medium text-gray-900 truncate">
                                        {{ scrape.dealer_name || scrape.dealer_id }}
                                    </div>
                                    <div class="text-xs text-gray-500 mt-1">
                                        {{ formatDate(scrape.scrape_date) }}
                                    </div>
                                </div>
                                <div class="flex flex-col gap-1 ml-2">
                                    <Tag :value="scrape.scrape_status" :severity="getStatusSeverity(scrape.scrape_status)" class="text-xs" />
                                    <Tag v-if="scrape.analyze_sentiment_enabled && scrape.sentiment_analysis_status"
                                         :value="scrape.sentiment_analysis_status"
                                         :severity="getSentimentStatusSeverity(scrape.sentiment_analysis_status)"
                                         class="text-xs" />
                                </div>
                            </div>
                            <div class="text-xs text-gray-600 mt-2">
                                {{ scrape.scraped_reviews || 0 }} reviews • {{ scrape.success_rate || 0 }}% success
                                <span v-if="scrape.sentiment_completion_rate !== undefined"> • {{ scrape.sentiment_completion_rate }}% sentiment</span>
                            </div>
                        </div>
                    </div>
                </template>
            </Card>
        </div>
    </Sidebar>
</template>

<style scoped>
.p-sidebar {
    background: var(--p-surface-0);
}
</style>