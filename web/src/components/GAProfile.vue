<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';
import Chart from 'primevue/chart';
import GoogleReviewService from '@/service/GoogleReviewService';

// Props
const props = defineProps({
    dealerId: {
        type: String,
        required: true
    },
    loading: {
        type: Boolean,
        default: false
    }
});

// Reactive data
const profileData = ref(null);
const internalLoading = ref(false);
const activeTab = ref('reviews'); // 'overview' or 'reviews'
const chartData = ref({});
const chartOptions = ref({});

// Computed properties
const isLoading = computed(() => props.loading || internalLoading.value);

const hasData = computed(() => {
    return profileData.value && profileData.value.data && profileData.value.data.has_data;
});

const businessInfo = computed(() => {
    return profileData.value?.data?.business_info || {};
});

const reviewSummary = computed(() => {
    return profileData.value?.data?.review_summary || {};
});

const reviewTags = computed(() => {
    return profileData.value?.data?.review_tags || [];
});

const starRating = computed(() => {
    // Use precise average from review summary if available, otherwise fallback to business info
    return reviewSummary.value.average_rating || businessInfo.value.rating || 0;
});

const totalReviews = computed(() => {
    return businessInfo.value.total_reviews || 0;
});

const photosCount = computed(() => {
    return businessInfo.value.photos_count || 0;
});

// Helper functions
const getStarClass = (starPosition, rating) => {
    const difference = starPosition - rating;

    if (difference <= 0) {
        // Full star
        return 'text-yellow-400';
    } else if (difference <= 0.5) {
        // Half star
        return 'text-yellow-400';
    } else {
        // Empty star
        return 'text-gray-300';
    }
};

const getStarDisplay = (starPosition, rating) => {
    const difference = starPosition - rating;

    if (difference <= 0) {
        // Full star - Unicode filled star
        return '★';
    } else if (difference <= 0.5) {
        // Half star - Use CSS to create half-filled effect
        return '★';
    } else {
        // Empty star - Unicode outline star
        return '☆';
    }
};

const formatReviewCount = (count) => {
    if (count >= 1000) {
        return `${(count / 1000).toFixed(1)}K`;
    }
    return count.toString();
};




// Initialize star distribution chart
const initStarChart = () => {
    // Always create chart with all 5 star ratings, even if no data
    let distribution = reviewSummary.value.star_distribution || [];

    // Create complete distribution array with all 5 star ratings
    const completeDistribution = [];
    for (let stars = 1; stars <= 5; stars++) {
        const existing = distribution.find(item => item.stars === stars);
        completeDistribution.push({
            stars: stars,
            count: existing ? existing.count : 0,
            percentage: existing ? existing.percentage : 0
        });
    }

    // Create horizontal bar chart data
    const labels = completeDistribution.map(item => `${item.stars} stars`);
    const data = completeDistribution.map(item => item.percentage);
    const counts = completeDistribution.map(item => item.count);

    // Colors for each star level
    const backgroundColor = [
        '#EF4444', // 1 star - Red
        '#F97316', // 2 stars - Orange
        '#EAB308', // 3 stars - Yellow
        '#22C55E', // 4 stars - Green
        '#16A34A'  // 5 stars - Dark Green
    ];

    chartData.value = {
        labels: labels.reverse(), // Show 5 stars at top
        datasets: [
            // Background bars (always full width - 100%)
            {
                data: Array(5).fill(100),
                backgroundColor: 'rgba(200, 200, 200, 0.3)',
                borderWidth: 0,
                barThickness: 8,
                categoryPercentage: 1,
                barPercentage: 1,
                stack: 'background'
            },
            // Foreground bars (actual percentages)
            {
                data: data.reverse(),
                backgroundColor: backgroundColor.reverse(),
                borderWidth: 0,
                barThickness: 8,
                categoryPercentage: 1,
                barPercentage: 1,
                stack: 'foreground'
            }
        ]
    };

    chartOptions.value = {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        // Only show tooltip for the foreground dataset (index 1)
                        if (context.datasetIndex === 1) {
                            const index = context.dataIndex;
                            const reversedIndex = completeDistribution.length - 1 - index;
                            const count = counts[reversedIndex];
                            const percentage = context.parsed.x;
                            return `${count} reviews (${percentage.toFixed(1)}%)`;
                        }
                        return null; // Hide tooltip for background bars
                    }
                }
            }
        },
        scales: {
            x: {
                beginAtZero: true,
                max: 100,
                display: false,
                stacked: true,
                grid: {
                    display: false
                }
            },
            y: {
                display: false,
                stacked: true,
                grid: {
                    display: false
                }
            }
        },
        elements: {
            bar: {
                borderRadius: 2
            }
        },
        layout: {
            padding: {
                top: 5,
                bottom: 5,
                left: 0,
                right: 0
            }
        }
    };
};

// Load profile data
const loadProfile = async () => {
    if (!props.dealerId) return;

    internalLoading.value = true;
    try {
        const result = await GoogleReviewService.getDealerProfile(props.dealerId);
        profileData.value = result;

        // Initialize chart after data is loaded
        if (result.success && result.data && result.data.has_data) {
            initStarChart();
        }
    } catch (error) {
        console.error('Error loading dealer profile:', error);
        profileData.value = null;
    } finally {
        internalLoading.value = false;
    }
};

// Watch for dealer ID changes
watch(() => props.dealerId, () => {
    if (props.dealerId) {
        loadProfile();
    }
}, { immediate: true });

// Watch for review summary changes to update chart
watch(() => reviewSummary.value, () => {
    if (reviewSummary.value.star_distribution) {
        initStarChart();
    }
}, { deep: true });

// Initialize on mount
onMounted(() => {
    if (props.dealerId) {
        loadProfile();
    }
});
</script>

<template>
    <Card class="ga-profile">
        <template #content>
            <div v-if="isLoading" class="flex justify-center items-center h-96">
                <div class="flex flex-col items-center space-y-3">
                    <ProgressSpinner style="width: 40px; height: 40px;" />
                    <div class="text-surface-500 dark:text-surface-400 text-sm">Loading business profile...</div>
                </div>
            </div>

            <div v-else-if="!hasData" class="flex flex-col items-center justify-center h-96">
                <div class="text-center space-y-3">
                    <i class="pi pi-info-circle text-4xl text-surface-400"></i>
                    <div class="text-surface-600 dark:text-surface-300">No Google Business Profile data available</div>
                    <div class="text-xs text-surface-500 dark:text-surface-400">
                        Google Reviews need to be scraped first to display business profile
                    </div>
                </div>
            </div>

            <div v-else class="space-y-6">
                <!-- Business Header -->
                <div class="space-y-3">
                    <div class="flex items-start justify-between">
                        <div class="flex-1">
                            <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0 mb-2">
                                {{ businessInfo.name || 'Business Name' }}
                            </h1>

                            <!-- Rating and Reviews -->
                            <div class="flex items-center space-x-3 mb-2">
                                <div class="flex items-center space-x-1">
                                    <span class="text-lg font-semibold text-surface-900 dark:text-surface-0">
                                        {{ starRating.toFixed(2) }}
                                    </span>
                                    <div class="flex">
                                        <span v-for="star in 5" :key="star"
                                              class="text-sm font-bold"
                                              :class="getStarClass(star, starRating)">{{ getStarDisplay(star, starRating) }}</span>
                                    </div>
                                    <span class="text-sm text-surface-600 dark:text-surface-400">
                                        ({{ formatReviewCount(totalReviews) }})
                                    </span>
                                </div>
                            </div>

                            <!-- Business Category and Location -->
                            <div class="text-sm text-surface-600 dark:text-surface-400 space-y-1">
                                <div v-if="businessInfo.category">{{ businessInfo.category }}</div>
                                <div v-if="businessInfo.location">{{ businessInfo.location }}</div>
                            </div>
                        </div>

                        <!-- Action Button -->
                        <div class="flex-shrink-0">
                            <Button icon="pi pi-ellipsis-h" severity="secondary" text size="small" />
                        </div>
                    </div>
                </div>

                <!-- Photos Section -->
                <div class="relative">
                    <div class="grid grid-cols-4 gap-2 h-48">
                        <!-- Main large photo -->
                        <div class="col-span-2 bg-surface-100 dark:bg-surface-700 rounded-lg relative overflow-hidden">
                            <div class="absolute inset-0 flex items-center justify-center">
                                <i class="pi pi-image text-3xl text-surface-400"></i>
                            </div>
                        </div>

                        <!-- Smaller photos -->
                        <div class="space-y-2">
                            <div class="h-20 bg-surface-100 dark:bg-surface-700 rounded-lg relative overflow-hidden">
                                <div class="absolute inset-0 flex items-center justify-center">
                                    <i class="pi pi-image text-lg text-surface-400"></i>
                                </div>
                            </div>
                            <div class="h-20 bg-surface-100 dark:bg-surface-700 rounded-lg relative overflow-hidden">
                                <div class="absolute inset-0 flex items-center justify-center">
                                    <i class="pi pi-image text-lg text-surface-400"></i>
                                </div>
                            </div>
                        </div>

                        <div class="space-y-2">
                            <div class="h-20 bg-surface-100 dark:bg-surface-700 rounded-lg relative overflow-hidden">
                                <div class="absolute inset-0 flex items-center justify-center">
                                    <i class="pi pi-image text-lg text-surface-400"></i>
                                </div>
                            </div>
                            <!-- Photos count overlay -->
                            <div class="h-20 bg-surface-100 dark:bg-surface-700 rounded-lg relative overflow-hidden">
                                <div class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
                                    <span class="text-white text-sm font-medium">
                                        {{ formatReviewCount(photosCount) }}+ Photos
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Tab Navigation -->
                <div class="border-b border-surface-200 dark:border-surface-700">
                    <nav class="flex space-x-8">
                        <button
                            @click="activeTab = 'overview'"
                            :class="[
                                'py-2 px-1 text-sm font-medium border-b-2 transition-colors',
                                activeTab === 'overview'
                                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                                    : 'border-transparent text-surface-500 hover:text-surface-700 dark:text-surface-400 dark:hover:text-surface-300'
                            ]"
                        >
                            Overview
                        </button>
                        <button
                            @click="activeTab = 'reviews'"
                            :class="[
                                'py-2 px-1 text-sm font-medium border-b-2 transition-colors',
                                activeTab === 'reviews'
                                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                                    : 'border-transparent text-surface-500 hover:text-surface-700 dark:text-surface-400 dark:hover:text-surface-300'
                            ]"
                        >
                            Reviews
                        </button>
                    </nav>
                </div>

                <!-- Tab Content -->
                <div class="min-h-64">
                    <!-- Overview Tab -->
                    <div v-if="activeTab === 'overview'" class="space-y-6">
                        <!-- Description -->
                        <div class="text-surface-600 dark:text-surface-400">
                            <p v-if="businessInfo.description">{{ businessInfo.description }}</p>
                            <p v-else>Business overview information will appear here when available.</p>
                        </div>

                        <!-- Address -->
                        <div v-if="businessInfo.address" class="space-y-2">
                            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0">Address</h3>
                            <div class="flex items-start space-x-2">
                                <i class="pi pi-map-marker text-surface-500 mt-1"></i>
                                <span class="text-sm text-surface-700 dark:text-surface-300">{{ businessInfo.address }}</span>
                            </div>
                        </div>

                        <!-- Hours -->
                        <div v-if="businessInfo.hours" class="space-y-2">
                            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0">Hours</h3>
                            <div class="space-y-1">
                                <div v-if="typeof businessInfo.hours === 'object'" class="text-sm">
                                    <div v-for="(hours, day) in businessInfo.hours" :key="day" class="flex justify-between">
                                        <span class="text-surface-700 dark:text-surface-300 capitalize">{{ day }}:</span>
                                        <span class="text-surface-600 dark:text-surface-400">{{ hours }}</span>
                                    </div>
                                </div>
                                <div v-else class="text-sm text-surface-700 dark:text-surface-300">
                                    {{ businessInfo.hours }}
                                </div>
                            </div>
                        </div>

                        <!-- Contact Information -->
                        <div v-if="businessInfo.website || businessInfo.phone" class="space-y-2">
                            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0">Contact</h3>
                            <div class="space-y-1">
                                <div v-if="businessInfo.phone" class="flex items-center space-x-2">
                                    <i class="pi pi-phone text-surface-500"></i>
                                    <span class="text-sm text-surface-700 dark:text-surface-300">
                                        {{ businessInfo.phone }}
                                    </span>
                                </div>
                                <div v-if="businessInfo.website" class="flex items-center space-x-2">
                                    <i class="pi pi-globe text-surface-500"></i>
                                    <a :href="businessInfo.website" target="_blank"
                                       class="text-blue-600 hover:text-blue-800 text-sm">
                                        {{ businessInfo.website }}
                                    </a>
                                </div>
                            </div>
                        </div>

                        <!-- Products and Services -->
                        <div v-if="businessInfo.services && businessInfo.services.length > 0" class="space-y-2">
                            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0">Products and Services</h3>
                            <div class="flex flex-wrap gap-2">
                                <Tag
                                    v-for="service in businessInfo.services"
                                    :key="service"
                                    :value="service"
                                    severity="secondary"
                                    class="text-xs"
                                />
                            </div>
                        </div>

                        <!-- Appointments -->
                        <div v-if="businessInfo.appointments" class="space-y-2">
                            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0">Appointments</h3>
                            <div class="flex items-center space-x-2">
                                <i class="pi pi-calendar text-surface-500"></i>
                                <span class="text-sm text-surface-700 dark:text-surface-300">
                                    <span v-if="businessInfo.appointments.available" class="text-green-600">Available</span>
                                    <span v-else class="text-orange-600">Contact for availability</span>
                                    <span v-if="businessInfo.appointments.info"> - {{ businessInfo.appointments.info }}</span>
                                </span>
                            </div>
                        </div>
                    </div>

                    <!-- Reviews Tab -->
                    <div v-if="activeTab === 'reviews'" class="space-y-6">
                        <!-- Google review summary header -->
                        <div class="flex items-center space-x-2">
                            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0">Google review summary</h3>
                            <i class="pi pi-info-circle text-surface-400" title="Based on scraped review data"></i>
                        </div>

                        <!-- Star distribution and overall rating -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <!-- Star Distribution Chart -->
                            <div class="space-y-3">
                                <div class="chart-container h-32" v-if="chartData.labels && chartData.labels.length > 0">
                                    <Chart type="bar" :data="chartData" :options="chartOptions" class="w-full h-full" />
                                </div>
                                <div v-else class="h-32 flex items-center justify-center text-surface-500 dark:text-surface-400">
                                    No rating distribution data
                                </div>
                            </div>

                            <!-- Overall Rating Display -->
                            <div class="text-center">
                                <div class="text-6xl font-bold text-surface-900 dark:text-surface-0 mb-2">
                                    {{ starRating.toFixed(2) }}
                                </div>
                                <div class="flex justify-center mb-2">
                                    <div class="flex">
                                        <span v-for="star in 5" :key="star"
                                              class="text-lg font-bold"
                                              :class="getStarClass(star, starRating)">{{ getStarDisplay(star, starRating) }}</span>
                                    </div>
                                </div>
                                <div class="text-sm text-surface-600 dark:text-surface-400">
                                    {{ formatReviewCount(reviewSummary.total_reviews || 0) }} reviews
                                </div>
                            </div>
                        </div>

                        <!-- Review Tags Section -->
                        <div v-if="reviewTags.length > 0" class="space-y-3">
                            <h4 class="text-md font-medium text-surface-900 dark:text-surface-0">Reviews</h4>

                            <!-- Popular review tags -->
                            <div class="flex flex-wrap gap-2">
                                <Tag
                                    v-for="tag in reviewTags.slice(0, 8)"
                                    :key="tag.tag"
                                    :value="`${tag.tag} ${tag.count}`"
                                    severity="secondary"
                                    class="px-3 py-1 text-sm cursor-default hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
                                />
                            </div>

                            <!-- Show all reviews indicator -->
                            <div class="text-sm text-surface-600 dark:text-surface-400">
                                <span class="font-medium">All</span> {{ formatReviewCount(reviewSummary.total_reviews || 0) }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </Card>
</template>

<style scoped>
.ga-profile :deep(.p-card-body) {
    padding: 1.5rem;
}

.chart-container {
    position: relative;
}

/* Tag hover effects */
.ga-profile :deep(.p-tag) {
    transition: all 0.2s ease;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .grid.md\\:grid-cols-2 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
    }

    .space-x-8 {
        gap: 1rem;
    }
}

/* Photo grid responsive */
@media (max-width: 640px) {
    .grid.grid-cols-4 {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .col-span-2 {
        grid-column: span 2 / span 2;
    }
}

/* Tab navigation styling */
button:focus {
    outline: none;
}

/* Custom scrollbar for mobile */
@media (max-width: 768px) {
    .overflow-x-auto::-webkit-scrollbar {
        display: none;
    }

    .overflow-x-auto {
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
}
</style>