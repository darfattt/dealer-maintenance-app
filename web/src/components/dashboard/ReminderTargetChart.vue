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

// Helper function to get reminder target display name
const getReminderTargetLabel = (target) => {
    const labelMap = {
        'KPB 1': 'KPB 1',
        'KPB-1': 'KPB 1',
        'KPB 2': 'KPB 2', 
        'KPB-2': 'KPB 2',
        'KPB 3': 'KPB 3',
        'KPB-3': 'KPB 3',
        'KPB 4': 'KPB 4',
        'KPB-4': 'KPB 4',
        'Non KPB': 'Non KPB',
        'Booking Service': 'Booking Service',
        'Ultah Konsumen': 'Ultah Konsumen'
    };
    return labelMap[target] || target || 'Unknown';
};

// Helper function to get colors for reminder targets
const getReminderTargetColor = (target, index) => {
    const colorMap = {
        'KPB 1': '#3B82F6',    // Blue
        'KPB-1': '#3B82F6',    // Blue
        'KPB 2': '#10B981',    // Green
        'KPB-2': '#10B981',    // Green
        'KPB 3': '#F59E0B',    // Orange
        'KPB-3': '#F59E0B',    // Orange
        'KPB 4': '#8B5CF6',    // Purple
        'KPB-4': '#8B5CF6',    // Purple
        'Non KPB': '#6B7280',  // Gray
        'Booking Service': '#EC4899', // Pink
        'Ultah Konsumen': '#EF4444'   // Red
    };
    
    // Default colors for unknown targets
    const defaultColors = [
        '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', 
        '#EC4899', '#EF4444', '#6B7280', '#14B8A6'
    ];
    
    return colorMap[target] || defaultColors[index % defaultColors.length];
};

// Computed properties
const hasData = computed(() => {
    const breakdown = props.stats.reminder_target_breakdown;
    return breakdown && Object.keys(breakdown).length > 0;
});

const totalReminders = computed(() => {
    if (!hasData.value) return 0;
    const breakdown = props.stats.reminder_target_breakdown;
    return Object.values(breakdown).reduce((sum, count) => sum + count, 0);
});

const chartTitle = computed(() => {
    return `Reminder Targets (${totalReminders.value} total)`;
});

// Sorted reminder targets for consistent display
const sortedTargetData = computed(() => {
    if (!hasData.value) return [];
    
    const breakdown = props.stats.reminder_target_breakdown;
    return Object.entries(breakdown)
        .map(([target, count]) => ({
            target,
            label: getReminderTargetLabel(target),
            count
        }))
        .sort((a, b) => b.count - a.count); // Sort by count descending
});

// Initialize chart configuration
const initChart = () => {
    if (!hasData.value) {
        chartData.value = {};
        return;
    }

    const data = sortedTargetData.value;
    const labels = data.map(item => item.label);
    const values = data.map(item => item.count);
    const colors = data.map((item, index) => getReminderTargetColor(item.target, index));

    chartData.value = {
        labels: labels,
        datasets: [{
            data: values,
            backgroundColor: colors,
            borderWidth: 2,
            borderColor: '#ffffff'
        }]
    };

    chartOptions.value = {
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 15,
                    usePointStyle: true,
                    font: {
                        size: 11
                    }
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const value = context.parsed;
                        const total = totalReminders.value;
                        const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                        return `${context.label}: ${value} (${percentage}%)`;
                    }
                }
            }
        },
        responsive: true,
        maintainAspectRatio: false,
        cutout: '35%'
    };
};

// Watch for stats changes
watch(() => props.stats, initChart, { immediate: true, deep: true });

// Initialize on mount
onMounted(() => {
    initChart();
});
</script>

<template>
    <Card class="reminder-target-chart">
        <template #title>
            <h3 class="text-lg font-semibold text-surface-900 mb-2">{{ chartTitle }}</h3>
        </template>
        <template #content>
            <div v-if="loading" class="flex justify-center items-center h-64">
                <div class="text-surface-500">Loading chart data...</div>
            </div>
            
            <div v-else-if="!hasData" class="flex flex-col items-center justify-center h-64">
                <Message severity="info" :closable="false">
                    No reminder target data available
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

            <!-- Top Targets Summary -->
            <div v-if="hasData && !loading && sortedTargetData.length > 0" class="mt-4">
                <h4 class="text-sm font-medium text-surface-700 dark:text-surface-300 mb-3">Top Reminder Targets</h4>
                <div class="space-y-2">
                    <div 
                        v-for="(item, index) in sortedTargetData.slice(0, 5)" 
                        :key="item.target"
                        class="flex justify-between items-center p-2 bg-surface-50 dark:bg-surface-800 rounded-lg border border-surface-200 dark:border-surface-600"
                    >
                        <div class="flex items-center space-x-2">
                            <div 
                                class="w-3 h-3 rounded-full"
                                :style="{ backgroundColor: getReminderTargetColor(item.target, index) }"
                            ></div>
                            <span class="text-sm font-medium text-surface-900 dark:text-surface-100">{{ item.label }}</span>
                        </div>
                        <div class="text-right">
                            <div class="text-sm font-semibold text-surface-900 dark:text-surface-100">{{ item.count }}</div>
                            <div class="text-xs text-surface-500 dark:text-surface-400">
                                {{ ((item.count / totalReminders) * 100).toFixed(1) }}%
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Show more indicator if there are more than 5 targets -->
                <div v-if="sortedTargetData.length > 5" class="text-center mt-2">
                    <span class="text-xs text-surface-500 dark:text-surface-400">
                        and {{ sortedTargetData.length - 5 }} more...
                    </span>
                </div>
            </div>
        </template>
    </Card>
</template>

<style scoped>
.reminder-target-chart :deep(.p-card-body) {
    padding: 1.5rem;
}

.reminder-target-chart :deep(.p-card-title) {
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
    
    .reminder-target-chart :deep(.p-card-body) {
        padding: 1rem;
    }
}
</style>