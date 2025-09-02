<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import Message from 'primevue/message';

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
    return stats && stats.total_analyzed_records  && stats.total_analyzed_records > 0 && stats.sentiment_distribution && stats.sentiment_distribution.length > 0;
});

const chartTitle = computed(() => {
    const total = props.stats.total_analyzed_records || 0;
    return `Sentiment Analysis (${total} analyzed)`;
});

// Initialize chart configuration
const initChart = () => {
    const stats = props.stats;
    
    if (!hasData.value) {
        chartData.value = {};
        return;
    }

    const distribution = stats.sentiment_distribution || [];
    
    // Prepare data for pie chart
    const labels = [];
    const data = [];
    const backgroundColor = [];
    
    // Sort by percentage to maintain consistent order
    const sortedDistribution = [...distribution].sort((a, b) => b.percentage - a.percentage);
    
    sortedDistribution.forEach(item => {
        if (item.sentiment && item.count > 0) {
            labels.push(item.sentiment);
            data.push(item.count); // Use count instead of percentage for better tooltip display
            
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
        datasets: [{
            data: data,
            backgroundColor: backgroundColor,
            borderWidth: 2,
            borderColor: '#ffffff'
        }]
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
                    generateLabels: function(chart) {
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
                    label: function(context) {
                        const value = context.parsed;
                        const percentage = totalCount > 0 ? ((value / totalCount) * 100).toFixed(1) : 0;
                        return `${context.label}: ${value} (${percentage}%)`;
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
watch(() => props.stats, initChart, { immediate: true, deep: true });

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

const getSentimentSubTextClass = (sentiment) => {
    switch (sentiment.toLowerCase()) {
        case 'positive':
            return 'text-green-700 dark:text-green-300';
        case 'negative':
            return 'text-red-700 dark:text-red-300';
        case 'neutral':
            return 'text-gray-700 dark:text-gray-300';
        default:
            return 'text-blue-700 dark:text-blue-300';
    }
};

// Initialize on mount
onMounted(() => {
    initChart();
});
</script>

<template>
    <Card class="sentiment-analysis-chart">
        <template #title>
            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-2">{{ chartTitle }}</h3>
        </template>
        <template #content>
            <div v-if="loading" class="flex justify-center items-center h-64">
                <div class="text-surface-500 dark:text-surface-400">Loading chart data...</div>
            </div>
            
            <div v-else-if="!hasData" class="flex flex-col items-center justify-center h-64">
                <Message severity="info" :closable="false">
                    <template #default>
                        <div class="text-surface-600 dark:text-surface-300">
                            No sentiment analysis data available for the selected period
                        </div>
                    </template>
                </Message>
            </div>
            
            <div v-else class="chart-container h-64">
                <Chart 
                    type="doughnut" 
                    :data="chartData" 
                    :options="chartOptions"
                    class="w-full h-full"
                />
            </div>

            <!-- Summary Stats -->
            <!-- <div v-if="hasData && !loading" class="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                <div 
                    v-for="item in stats.sentiment_distribution" 
                    :key="item.sentiment"
                    :class="getSentimentCardClass(item.sentiment)"
                    class="p-3 rounded-lg border"
                >
                    <div class="text-2xl font-bold" :class="getSentimentTextClass(item.sentiment)">{{ item.count || 0 }}</div>
                    <div class="text-sm" :class="getSentimentSubTextClass(item.sentiment)">{{ item.sentiment }}</div>
                    <div class="text-xs opacity-75" :class="getSentimentSubTextClass(item.sentiment)">{{ item.percentage }}%</div>
                </div>
            </div> -->

            <!-- Average Score -->
            <!-- <div v-if="hasData && !loading && stats.average_sentiment_score !== null" class="mt-4 text-center">
                <div class="text-sm text-surface-500 dark:text-surface-400">Average Sentiment Score</div>
                <div class="text-xl font-bold text-surface-900 dark:text-surface-100">
                    {{ parseFloat(stats.average_sentiment_score || 0).toFixed(2) }}
                </div>
            </div> -->
        </template>
    </Card>
</template>


<style scoped>
.sentiment-analysis-chart :deep(.p-card-body) {
    padding: 1.5rem;
}

.sentiment-analysis-chart :deep(.p-card-title) {
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
    
    .grid-cols-1.sm\\:grid-cols-3 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
        gap: 0.5rem;
    }
}

/* Dark mode message styling */
.sentiment-analysis-chart :deep(.p-message .p-message-text) {
    color: inherit;
}
</style>