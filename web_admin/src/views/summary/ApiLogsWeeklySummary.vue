<template>
    <div class="summary-component">
        <ProgressSpinner v-if="loading" class="flex justify-center" />

        <div v-else-if="!summaryData || availableWeeks.length === 0" class="empty-state">
            <i class="pi pi-inbox text-6xl text-gray-300"></i>
            <p class="text-gray-500 mt-4">No data available</p>
        </div>

        <div v-else class="space-y-4">
            <!-- Week Selector -->
            <Card class="bg-gradient-to-r from-blue-50 to-purple-50">
                <template #content>
                    <div class="flex items-center justify-between flex-wrap gap-4">
                        <div class="flex-1">
                            <p class="text-sm text-gray-600 mb-2">Select Week Period</p>
                            <Select
                                v-model="selectedWeek"
                                :options="availableWeeks"
                                optionLabel="label"
                                optionValue="value"
                                placeholder="Choose a week"
                                class="w-full md:w-80"
                            />
                        </div>
                        <div class="text-right">
                            <p class="text-sm text-gray-600">Total Historical Weeks</p>
                            <p class="text-2xl font-bold text-purple-600">{{ summaryData.total_weeks }}</p>
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Stats Cards -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card class="stat-card">
                    <template #content>
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-500">Dealers (Week)</p>
                                <p class="text-2xl font-bold text-blue-600">{{ weekDealerCount }}</p>
                            </div>
                            <i class="pi pi-building text-3xl text-blue-400"></i>
                        </div>
                    </template>
                </Card>

                <Card class="stat-card">
                    <template #content>
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-500">Total Requests</p>
                                <p class="text-2xl font-bold text-purple-600">{{ totalRequests }}</p>
                            </div>
                            <i class="pi pi-send text-3xl text-purple-400"></i>
                        </div>
                    </template>
                </Card>

                <Card class="stat-card">
                    <template #content>
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-500">Success Rate</p>
                                <p class="text-2xl font-bold text-green-600">{{ successRate }}%</p>
                            </div>
                            <i class="pi pi-check-circle text-3xl text-green-400"></i>
                        </div>
                    </template>
                </Card>

                <Card class="stat-card">
                    <template #content>
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-500">Avg Time</p>
                                <p class="text-2xl font-bold text-orange-600">{{ avgProcessingTime }}ms</p>
                            </div>
                            <i class="pi pi-clock text-3xl text-orange-400"></i>
                        </div>
                    </template>
                </Card>
            </div>

            <!-- Chart -->
            <Card>
                <template #title>
                    <span class="text-lg">Request Trends by Dealer ({{ selectedWeekLabel }})</span>
                </template>
                <template #content>
                    <div class="chart-container h-64">
                        <Chart type="line" :data="chartData" :options="chartOptions" class="w-full h-full" />
                    </div>
                </template>
            </Card>

            <!-- DataTable -->
            <Card>
                <template #title>
                    <span class="text-lg">Weekly Dealer Summary ({{ selectedWeekLabel }})</span>
                </template>
                <template #content>
                    <DataTable :value="filteredSummaries" :paginator="true" :rows="10" responsiveLayout="scroll">
                        <Column field="dealer_id" header="Dealer ID" :sortable="true"></Column>
                        <Column field="total_requests" header="Total Requests" :sortable="true">
                            <template #body="slotProps">
                                <Badge :value="slotProps.data.total_requests" severity="info" />
                            </template>
                        </Column>
                        <Column field="successful_requests" header="Successful" :sortable="true">
                            <template #body="slotProps">
                                <Badge :value="slotProps.data.successful_requests" severity="success" />
                            </template>
                        </Column>
                        <Column field="failed_requests" header="Failed" :sortable="true">
                            <template #body="slotProps">
                                <Badge :value="slotProps.data.failed_requests" :severity="slotProps.data.failed_requests > 0 ? 'danger' : 'secondary'" />
                            </template>
                        </Column>
                        <Column field="avg_processing_time_ms" header="Avg Time (ms)" :sortable="true">
                            <template #body="slotProps">
                                {{ Math.round(slotProps.data.avg_processing_time_ms) }}ms
                            </template>
                        </Column>
                        <Column header="Success %">
                            <template #body="slotProps">
                                <ProgressBar
                                    :value="calculateSuccessRate(slotProps.data)"
                                    :showValue="true"
                                    :pt="{
                                        value: { style: getProgressBarColor(calculateSuccessRate(slotProps.data)) }
                                    }"
                                />
                            </template>
                        </Column>
                    </DataTable>
                </template>
            </Card>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import ActivityService from '@/service/ActivityService';
import Chart from 'primevue/chart';

const emit = defineEmits(['loaded']);
const toast = useToast();

const loading = ref(false);
const summaryData = ref(null);
const selectedWeek = ref(null);

// Computed: Available weeks from the data
const availableWeeks = computed(() => {
    if (!summaryData.value?.summaries) return [];

    // Extract unique weeks
    const weeksMap = new Map();
    summaryData.value.summaries.forEach(summary => {
        const key = `${summary.week_start_date}_${summary.week_end_date}`;
        if (!weeksMap.has(key)) {
            weeksMap.set(key, {
                label: `${summary.week_start_date} to ${summary.week_end_date}`,
                value: key,
                start: summary.week_start_date,
                end: summary.week_end_date
            });
        }
    });

    // Sort by start date descending (most recent first)
    return Array.from(weeksMap.values()).sort((a, b) =>
        new Date(b.start) - new Date(a.start)
    );
});

// Computed: Filtered summaries for selected week
const filteredSummaries = computed(() => {
    if (!summaryData.value?.summaries || !selectedWeek.value) return [];

    const [weekStart, weekEnd] = selectedWeek.value.split('_');
    return summaryData.value.summaries.filter(s =>
        s.week_start_date === weekStart && s.week_end_date === weekEnd
    );
});

// Computed: Selected week label
const selectedWeekLabel = computed(() => {
    if (!selectedWeek.value) return '';
    const week = availableWeeks.value.find(w => w.value === selectedWeek.value);
    return week ? week.label : '';
});

// Computed: Week dealer count
const weekDealerCount = computed(() => filteredSummaries.value.length);

// Computed: Total requests for selected week
const totalRequests = computed(() => {
    return filteredSummaries.value.reduce((sum, dealer) => sum + dealer.total_requests, 0);
});

// Computed: Success rate for selected week
const successRate = computed(() => {
    const totalSuccessful = filteredSummaries.value.reduce((sum, dealer) => sum + dealer.successful_requests, 0);
    return totalRequests.value > 0 ? Math.round((totalSuccessful / totalRequests.value) * 100) : 0;
});

// Computed: Average processing time for selected week
const avgProcessingTime = computed(() => {
    if (filteredSummaries.value.length === 0) return 0;
    const avgTimes = filteredSummaries.value.map(d => d.avg_processing_time_ms);
    const sum = avgTimes.reduce((a, b) => a + b, 0);
    return Math.round(sum / avgTimes.length) || 0;
});

// Computed: Chart data
const chartData = computed(() => {
    if (filteredSummaries.value.length === 0) return { labels: [], datasets: [] };

    // Sort dealers by total requests and take top 10
    const topDealers = [...filteredSummaries.value]
        .sort((a, b) => b.total_requests - a.total_requests)
        .slice(0, 10);

    return {
        labels: topDealers.map(d => d.dealer_id),
        datasets: [
            {
                label: 'Total Requests',
                data: topDealers.map(d => d.total_requests),
                borderColor: 'rgba(139, 92, 246, 1)',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                tension: 0.4,
                fill: true
            },
            {
                label: 'Successful',
                data: topDealers.map(d => d.successful_requests),
                borderColor: 'rgba(16, 185, 129, 1)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            },
            {
                label: 'Failed',
                data: topDealers.map(d => d.failed_requests),
                borderColor: 'rgba(239, 68, 68, 1)',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
                fill: true
            }
        ]
    };
});

// Computed: Chart options
const chartOptions = computed(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'top'
        }
    },
    scales: {
        y: {
            beginAtZero: true
        }
    }
}));

const calculateSuccessRate = (dealer) => {
    if (dealer.total_requests === 0) return 0;
    return Math.round((dealer.successful_requests / dealer.total_requests) * 100);
};

const getProgressBarColor = (rate) => {
    if (rate >= 90) return { backgroundColor: '#10b981' };
    if (rate >= 70) return { backgroundColor: '#f59e0b' };
    return { backgroundColor: '#ef4444' };
};

const loadData = async () => {
    loading.value = true;
    try {
        const result = await ActivityService.getApiLogsWeeklySummary();
        if (result.success) {
            summaryData.value = result.data;

            // Auto-select most recent week
            if (availableWeeks.value.length > 0) {
                selectedWeek.value = availableWeeks.value[0].value;
            }

            emit('loaded');
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.message, life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load API logs weekly summary', life: 3000 });
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    loadData();
});

defineExpose({ loadData });
</script>

<style scoped>
.summary-component {
    padding: 0.5rem;
}

.empty-state {
    text-align: center;
    padding: 4rem 0;
}

.stat-card :deep(.p-card-body) {
    padding: 1rem;
}

.stat-card :deep(.p-card-content) {
    padding: 0;
}

.chart-container {
    position: relative;
}
</style>
