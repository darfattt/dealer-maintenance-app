<template>
    <div class="summary-component">
        <ProgressSpinner v-if="loading" class="flex justify-center" />

        <div v-else-if="!summaryData" class="empty-state">
            <i class="pi pi-inbox text-6xl text-gray-300"></i>
            <p class="text-gray-500 mt-4">No data available</p>
        </div>

        <div v-else class="space-y-4">
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
                    <span class="text-lg">Scrape Status Distribution</span>
                </template>
                <template #content>
                    <div class="flex justify-center">
                        <canvas ref="chartCanvas" height="250" width="250"></canvas>
                    </div>
                </template>
            </Card>

            <!-- DataTable -->
            <Card>
                <template #title>
                    <span class="text-lg">Dealer Breakdown</span>
                </template>
                <template #content>
                    <DataTable :value="summaryData.summaries" :paginator="true" :rows="5" responsiveLayout="scroll">
                        <Column field="dealer_name" header="Dealer Name" :sortable="true"></Column>
                        <Column field="total_scrapes" header="Total Scrapes" :sortable="true">
                            <template #body="slotProps">
                                <Badge :value="slotProps.data.total_scrapes" severity="info" />
                            </template>
                        </Column>
                        <Column header="Status">
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
                                </div>
                            </template>
                        </Column>
                        <Column field="total_reviews_scraped" header="Reviews" :sortable="true">
                            <template #body="slotProps">
                                {{ slotProps.data.total_reviews_scraped }}
                            </template>
                        </Column>
                        <Column field="total_new_reviews" header="New" :sortable="true">
                            <template #body="slotProps">
                                <Badge :value="slotProps.data.total_new_reviews" severity="success" />
                            </template>
                        </Column>
                        <Column field="sentiment_completed_count" header="Sentiment" :sortable="true">
                            <template #body="slotProps">
                                <span class="text-sm">{{ slotProps.data.sentiment_completed_count }} / {{ slotProps.data.sentiment_analysis_enabled_count }}</span>
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

const totalFailed = computed(() => {
    if (!summaryData.value?.summaries) return 0;
    return summaryData.value.summaries.reduce((sum, dealer) => sum + dealer.failed_scrapes, 0);
});

const totalProcessing = computed(() => {
    if (!summaryData.value?.summaries) return 0;
    return summaryData.value.summaries.reduce((sum, dealer) => sum + dealer.processing_scrapes, 0);
});

const successRate = computed(() => {
    return totalScrapes.value > 0 ? Math.round((totalCompleted.value / totalScrapes.value) * 100) : 0;
});

const createChart = async () => {
    await nextTick();
    if (!chartCanvas.value || !summaryData.value?.summaries) return;

    // Destroy existing chart
    if (chartInstance.value) {
        chartInstance.value.destroy();
    }

    const ctx = chartCanvas.value.getContext('2d');
    chartInstance.value = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'Failed', 'Processing', 'Partial'],
            datasets: [{
                data: [
                    totalCompleted.value,
                    totalFailed.value,
                    totalProcessing.value,
                    summaryData.value.summaries.reduce((sum, d) => sum + d.partial_scrapes, 0)
                ],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(59, 130, 246, 0.8)'
                ],
                borderColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(59, 130, 246, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: false
                }
            }
        }
    });
};

const loadData = async () => {
    loading.value = true;
    try {
        const result = await ActivityService.getGoogleReviewsTodaySummary();
        if (result.success) {
            summaryData.value = result.data;
            emit('loaded');
            await createChart();
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.message, life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load Google Reviews summary', life: 3000 });
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
