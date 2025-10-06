<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';

// Props
const props = defineProps({
    monthlyData: {
        type: Object,
        default: () => ({})
    },
    loading: {
        type: Boolean,
        default: false
    }
});

// Reactive data
const chartData = ref({});
const chartOptions = ref({});

// Computed properties
const hasData = computed(() => {
    const data = props.monthlyData;
    return data && data.success && data.data && data.data.monthly_totals &&
           data.data.monthly_totals.length > 0 &&
           data.data.total_year_reviews > 0;
});

const chartTitle = computed(() => {
    const year = props.monthlyData?.data?.year || new Date().getFullYear();
    const total = props.monthlyData?.data?.total_year_reviews || 0;
    return `Monthly Reviews ${year} (${total} total)`;
});

const currentYear = computed(() => {
    return props.monthlyData?.data?.year || new Date().getFullYear();
});

const totalYearReviews = computed(() => {
    return props.monthlyData?.data?.total_year_reviews || 0;
});

// Initialize chart configuration
const initChart = () => {
    if (!hasData.value) {
        chartData.value = {};
        return;
    }

    const monthlyTotals = props.monthlyData.data.monthly_totals;

    // Prepare data for vertical bar chart
    const labels = monthlyTotals.map(month => month.month_name);
    const data = monthlyTotals.map(month => month.total_reviews);

    // Generate colors - darker blue for months with more reviews
    const maxReviews = Math.max(...data);
    const backgroundColor = data.map(value => {
        if (value === 0) return '#E5E7EB'; // Gray for no reviews
        const intensity = maxReviews > 0 ? (value / maxReviews) * 0.8 + 0.2 : 0.2;
        return `rgba(59, 130, 246, ${intensity})`; // Blue with varying opacity
    });

    const borderColor = data.map(value => {
        if (value === 0) return '#9CA3AF'; // Gray border for no reviews
        return '#3B82F6'; // Blue border
    });

    chartData.value = {
        labels: labels,
        datasets: [
            {
                label: 'Reviews',
                data: data,
                backgroundColor: backgroundColor,
                borderColor: borderColor,
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }
        ]
    };

    chartOptions.value = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false // Hide legend for single dataset
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#ffffff',
                bodyColor: '#ffffff',
                borderColor: 'rgba(255, 255, 255, 0.2)',
                borderWidth: 1,
                callbacks: {
                    title: function(context) {
                        const monthIndex = context[0].dataIndex;
                        const monthData = monthlyTotals[monthIndex];
                        return `${monthData.month_name} ${currentYear.value}`;
                    },
                    label: function(context) {
                        const value = context.parsed.y;
                        return `${value} review${value !== 1 ? 's' : ''}`;
                    }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    font: {
                        size: 12
                    },
                    color: '#6B7280'
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.1)',
                    lineWidth: 1
                },
                ticks: {
                    stepSize: 1,
                    font: {
                        size: 12
                    },
                    color: '#6B7280',
                    callback: function(value) {
                        if (Number.isInteger(value)) {
                            return value;
                        }
                    }
                }
            }
        },
        elements: {
            bar: {
                borderRadius: 4
            }
        },
        layout: {
            padding: {
                top: 10,
                bottom: 5,
                left: 5,
                right: 5
            }
        },
        interaction: {
            intersect: false,
            mode: 'index'
        }
    };
};

// Watch for monthlyData changes
watch(
    () => props.monthlyData,
    () => {
        if (props.monthlyData) {
            initChart();
        }
    },
    { immediate: true, deep: true }
);

// Get peak month info
const peakMonth = computed(() => {
    if (!hasData.value) return null;

    const monthlyTotals = props.monthlyData.data.monthly_totals;
    const peak = monthlyTotals.reduce((max, month) =>
        month.total_reviews > max.total_reviews ? month : max
    );

    return peak.total_reviews > 0 ? peak : null;
});

// Get average monthly reviews
const averageMonthlyReviews = computed(() => {
    if (!hasData.value) return 0;

    const monthlyTotals = props.monthlyData.data.monthly_totals;
    const total = monthlyTotals.reduce((sum, month) => sum + month.total_reviews, 0);
    return (total / 12).toFixed(1);
});

// Initialize on mount
onMounted(() => {
    if (props.monthlyData) {
        initChart();
    }
});
</script>

<template>
    <Card class="sentiment-analysis-ga-total-review">
        <template #title>
            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-2">{{ chartTitle }}</h3>
        </template>
        <template #content>
            <div v-if="loading" class="flex justify-center items-center h-64">
                <div class="flex flex-col items-center space-y-3">
                    <ProgressSpinner style="width: 40px; height: 40px;" />
                    <div class="text-surface-500 dark:text-surface-400 text-sm">Loading monthly review data...</div>
                </div>
            </div>

            <div v-else-if="!hasData" class="flex flex-col items-center justify-center h-64">
                <Message severity="info" :closable="false">
                    <template #default>
                        <div class="text-surface-600 dark:text-surface-300">No Google Reviews data available for {{ currentYear }}</div>
                    </template>
                </Message>
                <div class="text-xs text-surface-500 dark:text-surface-400 mt-2 text-center">
                    Reviews need to be scraped first to show monthly trends
                </div>
            </div>

            <div v-else class="space-y-4">
                <!-- Chart Container -->
                <div class="chart-container h-64">
                    <Chart type="bar" :data="chartData" :options="chartOptions" class="w-full h-full" />
                </div>

                <!-- Summary Stats -->
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                    <!-- Total Reviews -->
                    <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg border border-blue-200 dark:border-blue-800">
                        <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ totalYearReviews }}</div>
                        <div class="text-sm text-blue-700 dark:text-blue-300">Total Reviews</div>
                        <div class="text-xs text-blue-600 dark:text-blue-400 opacity-75">{{ currentYear }}</div>
                    </div>

                    <!-- Peak Month -->
                    <div v-if="peakMonth" class="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg border border-green-200 dark:border-green-800">
                        <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ peakMonth.total_reviews }}</div>
                        <div class="text-sm text-green-700 dark:text-green-300">Peak Month</div>
                        <div class="text-xs text-green-600 dark:text-green-400 opacity-75">{{ peakMonth.month_name }}</div>
                    </div>

                    <!-- Average Monthly -->
                    <div class="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-lg border border-purple-200 dark:border-purple-800">
                        <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">{{ averageMonthlyReviews }}</div>
                        <div class="text-sm text-purple-700 dark:text-purple-300">Avg/Month</div>
                        <div class="text-xs text-purple-600 dark:text-purple-400 opacity-75">{{ currentYear }}</div>
                    </div>
                </div>

                <!-- Additional Info -->
                <!-- <div class="bg-surface-50 dark:bg-surface-800 p-3 rounded-lg border border-surface-200 dark:border-surface-600">
                    <div class="text-xs text-surface-500 dark:text-surface-400 text-center">
                        Monthly review distribution for {{ currentYear }} • Updated when new reviews are scraped
                    </div>
                </div> -->
            </div>
        </template>
    </Card>
</template>

<style scoped>
.sentiment-analysis-ga-total-review :deep(.p-card-body) {
    padding: 1.5rem;
}

.sentiment-analysis-ga-total-review :deep(.p-card-title) {
    margin-bottom: 1rem;
}

.chart-container {
    position: relative;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .chart-container {
        height: 200px;
    }

    .grid.sm\\:grid-cols-3 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
        gap: 0.5rem;
    }
}

/* Dark mode message styling */
.sentiment-analysis-ga-total-review :deep(.p-message .p-message-text) {
    color: inherit;
}
</style>