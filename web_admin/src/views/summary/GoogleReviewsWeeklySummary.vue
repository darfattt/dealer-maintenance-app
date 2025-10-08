<template>
    <div class="summary-component">
        <ProgressSpinner v-if="loading" class="flex justify-center" />

        <div v-else-if="!summaryData" class="empty-state">
            <i class="pi pi-inbox text-6xl text-gray-300"></i>
            <p class="text-gray-500 mt-4">No data available</p>
        </div>

        <div v-else class="space-y-4">
            <!-- Week Header -->
            <Card class="bg-gradient-to-r from-green-50 to-blue-50">
                <template #content>
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm text-gray-600">Week Period</p>
                            <p class="text-xl font-bold text-gray-800">{{ summaryData.date }}</p>
                        </div>
                        <i class="pi pi-calendar text-4xl text-green-500"></i>
                    </div>
                </template>
            </Card>

            <!-- Stats Cards -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card class="stat-card">
                    <template #content>
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-500">Total Dealers</p>
                                <p class="text-2xl font-bold text-blue-600">{{ summaryData.total_dealers }}</p>
                            </div>
                            <i class="pi pi-building text-3xl text-blue-400"></i>
                        </div>
                    </template>
                </Card>

                <Card class="stat-card">
                    <template #content>
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-500">Total Scrapes</p>
                                <p class="text-2xl font-bold text-purple-600">{{ totalScrapes }}</p>
                            </div>
                            <i class="pi pi-sync text-3xl text-purple-400"></i>
                        </div>
                    </template>
                </Card>

                <Card class="stat-card">
                    <template #content>
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-500">Reviews Scraped</p>
                                <p class="text-2xl font-bold text-green-600">{{ totalReviews }}</p>
                            </div>
                            <i class="pi pi-star text-3xl text-green-400"></i>
                        </div>
                    </template>
                </Card>

                <Card class="stat-card">
                    <template #content>
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-500">Success Rate</p>
                                <p class="text-2xl font-bold text-orange-600">{{ successRate }}%</p>
                            </div>
                            <i class="pi pi-check-circle text-3xl text-orange-400"></i>
                        </div>
                    </template>
                </Card>
            </div>

            <!-- Chart -->
            <Card>
                <template #title>
                    <span class="text-lg">Scrape Status Breakdown by Dealer</span>
                </template>
                <template #content>
                    <canvas ref="chartCanvas" height="200"></canvas>
                </template>
            </Card>

            <!-- DataTable -->
            <Card>
                <template #title>
                    <span class="text-lg">Weekly Dealer Summary</span>
                </template>
                <template #content>
                    <DataTable :value="summaryData.summaries" :paginator="true" :rows="10" responsiveLayout="scroll">
                        <Column field="dealer_name" header="Dealer Name" :sortable="true"></Column>
                        <Column field="total_scrapes" header="Total Scrapes" :sortable="true">
                            <template #body="slotProps">
                                <Badge :value="slotProps.data.total_scrapes" severity="info" />
                            </template>
                        </Column>
                        <Column header="Status Breakdown">
                            <template #body="slotProps">
                                <div class="flex gap-1 flex-wrap">
                                    <Tag v-if="slotProps.data.completed_scrapes > 0"
                                         :value="`✓ ${slotProps.data.completed_scrapes}`"
                                         severity="success" />
                                    <Tag v-if="slotProps.data.failed_scrapes > 0"
                                         :value="`✗ ${slotProps.data.failed_scrapes}`"
                                         severity="danger" />
                                    <Tag v-if="slotProps.data.processing_scrapes > 0"
                                         :value="`⟳ ${slotProps.data.processing_scrapes}`"
                                         severity="warning" />
                                    <Tag v-if="slotProps.data.partial_scrapes > 0"
                                         :value="`◐ ${slotProps.data.partial_scrapes}`"
                                         severity="info" />
                                </div>
                            </template>
                        </Column>
                        <Column field="total_reviews_scraped" header="Total Reviews" :sortable="true">
                            <template #body="slotProps">
                                {{ slotProps.data.total_reviews_scraped }}
                            </template>
                        </Column>
                        <Column field="total_new_reviews" header="New Reviews" :sortable="true">
                            <template #body="slotProps">
                                <Badge :value="slotProps.data.total_new_reviews" severity="success" />
                            </template>
                        </Column>
                        <Column field="avg_scrape_duration_seconds" header="Avg Duration" :sortable="true">
                            <template #body="slotProps">
                                {{ Math.round(slotProps.data.avg_scrape_duration_seconds) }}s
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
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useToast } from 'primevue/usetoast';
import ActivityService from '@/service/ActivityService';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const emit = defineEmits(['loaded']);
const toast = useToast();

const loading = ref(false);
const summaryData = ref(null);
const chartCanvas = ref(null);
const chartInstance = ref(null);

const totalScrapes = computed(() => {
    if (!summaryData.value?.summaries) return 0;
    return summaryData.value.summaries.reduce((sum, dealer) => sum + dealer.total_scrapes, 0);
});

const totalReviews = computed(() => {
    if (!summaryData.value?.summaries) return 0;
    return summaryData.value.summaries.reduce((sum, dealer) => sum + dealer.total_reviews_scraped, 0);
});

const totalCompleted = computed(() => {
    if (!summaryData.value?.summaries) return 0;
    return summaryData.value.summaries.reduce((sum, dealer) => sum + dealer.completed_scrapes, 0);
});

const successRate = computed(() => {
    return totalScrapes.value > 0 ? Math.round((totalCompleted.value / totalScrapes.value) * 100) : 0;
});

const calculateSuccessRate = (dealer) => {
    if (dealer.total_scrapes === 0) return 0;
    return Math.round((dealer.completed_scrapes / dealer.total_scrapes) * 100);
};

const getProgressBarColor = (rate) => {
    if (rate >= 90) return { backgroundColor: '#10b981' };
    if (rate >= 70) return { backgroundColor: '#f59e0b' };
    return { backgroundColor: '#ef4444' };
};

const createChart = async () => {
    await nextTick();
    if (!chartCanvas.value || !summaryData.value?.summaries) return;

    // Destroy existing chart
    if (chartInstance.value) {
        chartInstance.value.destroy();
    }

    // Sort dealers by total scrapes and take top 10
    const topDealers = [...summaryData.value.summaries]
        .sort((a, b) => b.total_scrapes - a.total_scrapes)
        .slice(0, 10);

    const ctx = chartCanvas.value.getContext('2d');
    chartInstance.value = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topDealers.map(d => d.dealer_name || d.dealer_id),
            datasets: [
                {
                    label: 'Completed',
                    data: topDealers.map(d => d.completed_scrapes),
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Failed',
                    data: topDealers.map(d => d.failed_scrapes),
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    borderColor: 'rgba(239, 68, 68, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Processing',
                    data: topDealers.map(d => d.processing_scrapes),
                    backgroundColor: 'rgba(245, 158, 11, 0.8)',
                    borderColor: 'rgba(245, 158, 11, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Partial',
                    data: topDealers.map(d => d.partial_scrapes),
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true
                }
            }
        }
    });
};

const loadData = async () => {
    loading.value = true;
    try {
        const result = await ActivityService.getGoogleReviewsWeeklySummary();
        if (result.success) {
            summaryData.value = result.data;
            emit('loaded');
            await createChart();
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.message, life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load Google Reviews weekly summary', life: 3000 });
    } finally {
        loading.value = false;
    }
};

watch(() => summaryData.value, () => {
    if (summaryData.value) {
        createChart();
    }
}, { deep: true });

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
</style>
