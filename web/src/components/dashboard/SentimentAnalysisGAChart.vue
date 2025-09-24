<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';

// Props
const props = defineProps({
    stats: {
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
    const stats = props.stats;
    return stats && stats.data && stats.data.total_reviews && stats.data.total_reviews > 0 &&
           stats.data.analyzed_reviews && stats.data.analyzed_reviews > 0;
});

const chartTitle = computed(() => {
    const analyzed = props.stats?.data?.analyzed_reviews || 0;
    const total = props.stats?.data?.total_reviews || 0;
    return `Google Review Sentiment (${analyzed}/${total} analyzed)`;
});

const sentimentDistribution = computed(() => {
    if (!props.stats?.data?.sentiment_distribution) return [];

    const dist = props.stats.data.sentiment_distribution;
    return [
        { sentiment: 'Positive', count: dist.Positive || 0 },
        { sentiment: 'Neutral', count: dist.Neutral || 0 },
        { sentiment: 'Negative', count: dist.Negative || 0 }
    ].filter(item => item.count > 0);
});

// Initialize chart configuration
const initChart = () => {
    if (!hasData.value || sentimentDistribution.value.length === 0) {
        chartData.value = {};
        return;
    }

    const distribution = sentimentDistribution.value;

    // Prepare data for pie chart
    const labels = [];
    const data = [];
    const backgroundColor = [];

    // Sort by count to maintain consistent order
    const sortedDistribution = [...distribution].sort((a, b) => b.count - a.count);

    sortedDistribution.forEach((item) => {
        if (item.sentiment && item.count > 0) {
            labels.push(item.sentiment);
            data.push(item.count);

            // Set colors based on sentiment
            switch (item.sentiment.toLowerCase()) {
                case 'positive':
                    backgroundColor.push('#10B981'); // Green
                    break;
                case 'negative':
                    backgroundColor.push('#EF4444'); // Red
                    break;
                case 'neutral':
                    backgroundColor.push('#6B7280'); // Gray
                    break;
                default:
                    backgroundColor.push('#3B82F6'); // Blue
            }
        }
    });

    if (data.length === 0) {
        chartData.value = {};
        return;
    }

    chartData.value = {
        labels: labels,
        datasets: [
            {
                data: data,
                backgroundColor: backgroundColor,
                borderWidth: 2,
                borderColor: '#ffffff'
            }
        ]
    };

    const totalCount = data.reduce((sum, val) => sum + val, 0);

    chartOptions.value = {
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 20,
                    usePointStyle: true,
                    font: {
                        size: 12
                    },
                    generateLabels: function (chart) {
                        const data = chart.data;
                        if (data.labels.length && data.datasets.length) {
                            return data.labels.map((label, i) => {
                                const meta = chart.getDatasetMeta(0);
                                const style = meta.controller.getStyle(i);
                                const value = data.datasets[0].data[i];
                                const percentage = totalCount > 0 ? ((value / totalCount) * 100).toFixed(1) : 0;

                                return {
                                    text: `${label} (${percentage}%)`,
                                    fillStyle: style.backgroundColor,
                                    strokeStyle: style.borderColor,
                                    lineWidth: style.borderWidth,
                                    pointStyle: 'circle',
                                    hidden: isNaN(data.datasets[0].data[i]) || meta.data[i].hidden,
                                    index: i
                                };
                            });
                        }
                        return [];
                    }
                }
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        const value = context.parsed;
                        const percentage = totalCount > 0 ? ((value / totalCount) * 100).toFixed(1) : 0;
                        return `${context.label}: ${value} reviews (${percentage}%)`;
                    }
                }
            }
        },
        responsive: true,
        maintainAspectRatio: false,
        cutout: '40%',
        elements: {
            arc: {
                borderWidth: 2
            }
        },
        layout: {
            padding: {
                top: 10,
                bottom: 10
            }
        }
    };
};

// Watch for stats changes
watch(
    () => props.stats,
    () => {
        if (props.stats) {
            initChart();
        }
    },
    { immediate: true, deep: true }
);

// Helper methods for styling
const getSentimentCardClass = (sentiment) => {
    switch (sentiment.toLowerCase()) {
        case 'positive':
            return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
        case 'negative':
            return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
        case 'neutral':
            return 'bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-800';
        default:
            return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800';
    }
};

const getSentimentTextClass = (sentiment) => {
    switch (sentiment.toLowerCase()) {
        case 'positive':
            return 'text-green-600 dark:text-green-400';
        case 'negative':
            return 'text-red-600 dark:text-red-400';
        case 'neutral':
            return 'text-gray-600 dark:text-gray-400';
        default:
            return 'text-blue-600 dark:text-blue-400';
    }
};

// Analysis completion rate
const analysisCompletionRate = computed(() => {
    if (!props.stats?.data) return 0;
    const total = props.stats.data.total_reviews || 0;
    const analyzed = props.stats.data.analyzed_reviews || 0;
    return total > 0 ? ((analyzed / total) * 100).toFixed(1) : 0;
});

// Initialize on mount
onMounted(() => {
    if (props.stats) {
        initChart();
    }
});
</script>

<template>
    <Card class="sentiment-analysis-ga-chart">
        <template #title>
            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-2">{{ chartTitle }}</h3>
        </template>
        <template #content>
            <div v-if="loading" class="flex justify-center items-center h-64">
                <div class="flex flex-col items-center space-y-3">
                    <ProgressSpinner style="width: 40px; height: 40px;" />
                    <div class="text-surface-500 dark:text-surface-400 text-sm">Loading sentiment data...</div>
                </div>
            </div>

            <div v-else-if="!hasData" class="flex flex-col items-center justify-center h-64">
                <Message severity="info" :closable="false">
                    <template #default>
                        <div class="text-surface-600 dark:text-surface-300">No Google Reviews sentiment data available</div>
                    </template>
                </Message>
                <div class="text-xs text-surface-500 dark:text-surface-400 mt-2 text-center">
                    Reviews need to be scraped and analyzed first
                </div>
            </div>

            <div v-else class="space-y-4">
                <!-- Chart Container -->
                <div class="chart-container h-64">
                    <Chart type="doughnut" :data="chartData" :options="chartOptions" class="w-full h-full" />
                </div>

                <!-- Analysis Progress Info -->
                <div class="bg-surface-50 dark:bg-surface-800 p-3 rounded-lg border border-surface-200 dark:border-surface-600">
                    <div class="flex justify-between items-center text-sm">
                        <span class="font-medium text-surface-700 dark:text-surface-300">Analysis Progress</span>
                        <span class="text-surface-900 dark:text-surface-100 font-semibold">{{ analysisCompletionRate }}%</span>
                    </div>
                    <div class="mt-2 text-xs text-surface-500 dark:text-surface-400">
                        {{ stats?.data?.analyzed_reviews || 0 }} of {{ stats?.data?.total_reviews || 0 }} reviews analyzed
                    </div>
                </div>

                <!-- Average Sentiment Score -->
                <div v-if="stats?.data?.average_sentiment_score !== null && stats?.data?.average_sentiment_score !== undefined"
                     class="text-center border-t border-surface-200 dark:border-surface-700 pt-3">
                    <div class="text-sm text-surface-500 dark:text-surface-400">Average Sentiment Score</div>
                    <div class="text-xl font-bold text-surface-900 dark:text-surface-100 mt-1">
                        {{ parseFloat(stats.data.average_sentiment_score || 0).toFixed(2) }}
                    </div>
                    <!-- <div class="text-xs text-surface-500 dark:text-surface-400">Scale: -5.00 (Very Negative) to +5.00 (Very Positive)</div> -->
                </div>
            </div>
        </template>
    </Card>
</template>

<style scoped>
.sentiment-analysis-ga-chart :deep(.p-card-body) {
    padding: 1.5rem;
}

.sentiment-analysis-ga-chart :deep(.p-card-title) {
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
}

/* Dark mode message styling */
.sentiment-analysis-ga-chart :deep(.p-message .p-message-text) {
    color: inherit;
}
</style>