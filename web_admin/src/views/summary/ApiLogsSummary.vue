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
                    <span class="text-lg">Top Dealers by Request Volume</span>
                </template>
                <template #content>
                    <canvas ref="chartCanvas" height="200"></canvas>
                </template>
            </Card>

            <!-- DataTable -->
            <Card>
                <template #title>
                    <span class="text-lg">Dealer Breakdown</span>
                </template>
                <template #content>
                    <DataTable :value="summaryData.summaries" :paginator="true" :rows="5" responsiveLayout="scroll">
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
                        <Column header="Request Types">
                            <template #body="slotProps">
                                <Button icon="pi pi-eye" text size="small" @click="showRequestTypes(slotProps.data)" />
                            </template>
                        </Column>
                    </DataTable>
                </template>
            </Card>
        </div>

        <!-- Request Types Dialog -->
        <Dialog v-model:visible="requestTypesDialog" header="Request Types Breakdown" :style="{ width: '450px' }" modal>
            <div v-if="selectedDealer" class="space-y-2">
                <p class="font-semibold mb-3">Dealer: {{ selectedDealer.dealer_id }}</p>
                <div v-for="(count, type) in selectedDealer.request_count_by_type" :key="type" class="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <span class="text-gray-700">{{ type }}</span>
                    <Badge :value="count" />
                </div>
            </div>
        </Dialog>
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
const requestTypesDialog = ref(false);
const selectedDealer = ref(null);

const totalRequests = computed(() => {
    if (!summaryData.value?.summaries) return 0;
    return summaryData.value.summaries.reduce((sum, dealer) => sum + dealer.total_requests, 0);
});

const successRate = computed(() => {
    if (!summaryData.value?.summaries) return 0;
    const totalSuccessful = summaryData.value.summaries.reduce((sum, dealer) => sum + dealer.successful_requests, 0);
    return totalRequests.value > 0 ? Math.round((totalSuccessful / totalRequests.value) * 100) : 0;
});

const avgProcessingTime = computed(() => {
    if (!summaryData.value?.summaries) return 0;
    const avgTimes = summaryData.value.summaries.map(d => d.avg_processing_time_ms);
    const sum = avgTimes.reduce((a, b) => a + b, 0);
    return Math.round(sum / avgTimes.length) || 0;
});

const showRequestTypes = (dealer) => {
    selectedDealer.value = dealer;
    requestTypesDialog.value = true;
};

const createChart = async () => {
    await nextTick();
    if (!chartCanvas.value || !summaryData.value?.summaries) return;

    // Destroy existing chart
    if (chartInstance.value) {
        chartInstance.value.destroy();
    }

    // Sort dealers by total requests and take top 5
    const topDealers = [...summaryData.value.summaries]
        .sort((a, b) => b.total_requests - a.total_requests)
        .slice(0, 5);

    const ctx = chartCanvas.value.getContext('2d');
    chartInstance.value = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topDealers.map(d => d.dealer_id),
            datasets: [
                {
                    label: 'Total Requests',
                    data: topDealers.map(d => d.total_requests),
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
};

const loadData = async () => {
    loading.value = true;
    try {
        const result = await ActivityService.getApiLogsTodaySummary();
        if (result.success) {
            summaryData.value = result.data;
            emit('loaded');
            await createChart();
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.message, life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load API logs summary', life: 3000 });
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
