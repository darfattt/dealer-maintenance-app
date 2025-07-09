<script setup>
import { ref, onMounted, watch } from 'vue';
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import Message from 'primevue/message';

// Props from parent dashboard
const props = defineProps({
    dealerId: {
        type: String,
        default: '12284'
    },
    dateFrom: {
        type: String,
        required: true
    },
    dateTo: {
        type: String,
        required: true
    }
});

// Reactive data
const chartData = ref({});
const chartOptions = ref({});
const loading = ref(false);
const error = ref('');

// Methods
const fetchStatusProspectData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Dummy data for now
        const dummyData = [
            { status: 'Deal', count: 5, color: '#10B981' },
            { status: 'Not Deal', count: 20, color: '#EF4444' },
            { status: 'Hot', count: 434, color: '#F59E0B' },
            { status: 'Medium', count: 254, color: '#FBBF24' },
            { status: 'Low', count: 96, color: '#FDE68A' }
        ];

        const labels = dummyData.map(item => item.status);
        const values = dummyData.map(item => item.count);
        const colors = dummyData.map(item => item.color);

        chartData.value = {
            labels: labels,
            datasets: [
                {
                    data: values,
                    backgroundColor: colors,
                    borderColor: colors,
                    borderWidth: 1
                }
            ]
        };

        // Chart options for horizontal bar
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
                            return `${context.label}: ${context.parsed.x} prospects`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        display: true
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            }
        };
    } catch (err) {
        console.error('Error fetching prospect status:', err);
        error.value = 'Failed to fetch prospect status data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchStatusProspectData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchStatusProspectData();
});
</script>

<template>
    <Card class="h-full">
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Chart -->
            <div v-if="!error && Object.keys(chartData).length > 0" class="h-80">
                <Chart
                    type="bar"
                    :data="chartData"
                    :options="chartOptions"
                    class="h-full"
                />
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading...</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
.h-80 {
    height: 20rem;
}
</style>
