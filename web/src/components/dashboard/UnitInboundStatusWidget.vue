<script setup>
import { ref, onMounted, computed } from 'vue';
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import Button from 'primevue/button';
import Message from 'primevue/message';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

// Auth store
const authStore = useAuthStore();

// Reactive data
const chartData = ref({});
const chartOptions = ref({});
const loading = ref(false);
const error = ref('');
const totalRecords = ref(0);

// Filter controls
const selectedDealer = ref('12284'); // Default dealer
const dateFrom = ref(new Date(new Date().getFullYear(), 0, 1)); // Start of current year
const dateTo = ref(new Date()); // Today
const userDealers = ref([]); // For DEALER_USER role

// Dealer options (you can expand this list)
const dealerOptions = ref([
    { label: 'Sample Dealer (12284)', value: '12284' },
    { label: 'Test Dealer (00999)', value: '00999' }
]);

// Chart colors
const chartColors = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
];

// Status mapping for unit inbound
const statusMapping = {
    '0': 'Belum Diterima',
    '1': 'Sudah Diterima'
};

// Computed properties
const formattedDateFrom = computed(() => {
    if (!dateFrom.value) return '';
    return dateFrom.value.toISOString().split('T')[0];
});

const formattedDateTo = computed(() => {
    if (!dateTo.value) return '';
    return dateTo.value.toISOString().split('T')[0];
});

// Check if user is DEALER_USER role
const isDealerUser = computed(() => {
    return authStore.userRole === 'DEALER_USER';
});

// Show dealer dropdown only for non-DEALER_USER roles
const showDealerDropdown = computed(() => {
    return !isDealerUser.value;
});

// Computed property for legend items
const legendItems = computed(() => {
    if (!chartData.value || !chartData.value.labels) return [];

    const labels = chartData.value.labels;
    const values = chartData.value.datasets[0]?.data || [];
    const colors = chartData.value.datasets[0]?.backgroundColor || [];
    const total = values.reduce((sum, val) => sum + val, 0);

    return labels.map((label, index) => ({
        label: label,
        count: values[index] || 0,
        percentage: total > 0 ? ((values[index] / total) * 100).toFixed(1) : '0.0',
        color: colors[index] || '#ccc'
    }));
});

// Methods
const fetchUserDealers = async () => {
    if (!isDealerUser.value) return;

    try {
        const response = await axios.get('/api/v1/user-dealers/me/dealers');
        userDealers.value = response.data;

        // Set the first dealer as selected if available
        if (userDealers.value.length > 0) {
            selectedDealer.value = userDealers.value[0];
        }
    } catch (err) {
        console.error('Error fetching user dealers:', err);
        error.value = 'Failed to fetch assigned dealers';
    }
};

const fetchUnitInboundStatus = async () => {
    if (!selectedDealer.value || !dateFrom.value || !dateTo.value) {
        error.value = 'Please select dealer and date range';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        const response = await axios.get('/api/v1/dashboard/unit-inbound/status-counts', {
            params: {
                dealer_id: selectedDealer.value,
                date_from: formattedDateFrom.value,
                date_to: formattedDateTo.value
            }
        });

        if (response.data.success) {
            const data = response.data.data;
            totalRecords.value = response.data.total_records;

            if (data.length === 0) {
                error.value = 'No data found for the selected criteria';
                chartData.value = {};
                return;
            }

            // Prepare chart data - use status_label from API if available, otherwise use mapping
            const mappedData = data.map(item => ({
                status: item.status_label || statusMapping[item.status_shipping_list] || item.status_shipping_list || 'Unknown',
                count: item.count,
                originalStatus: item.status_shipping_list
            }));

            // Group by mapped status (in case multiple original statuses map to the same label)
            const groupedData = mappedData.reduce((acc, item) => {
                const existing = acc.find(x => x.status === item.status);
                if (existing) {
                    existing.count += item.count;
                } else {
                    acc.push({ status: item.status, count: item.count });
                }
                return acc;
            }, []);

            const labels = groupedData.map(item => item.status);
            const values = groupedData.map(item => item.count);
            const colors = chartColors.slice(0, groupedData.length);

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

            // Chart options
            chartOptions.value = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false // Hide default legend since we're using custom legend
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} unit (${percentage}%)`;
                            }
                        }
                    }
                }
            };
        } else {
            error.value = response.data.message || 'Failed to fetch data';
        }
    } catch (err) {
        console.error('Error fetching unit inbound status:', err);
        error.value = 'Failed to fetch unit inbound status data';
    } finally {
        loading.value = false;
    }
};

// Lifecycle
onMounted(async () => {
    // Fetch user dealers first if DEALER_USER role
    if (isDealerUser.value) {
        await fetchUserDealers();
    }

    // Then fetch the chart data
    fetchUnitInboundStatus();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <span>Unit Inbound Status Distribution</span>
                <small v-if="totalRecords > 0" class="text-muted-color">
                    Total Records: {{ totalRecords }}
                </small>
            </div>
        </template>
        
        <template #content>
            <!-- Filter Controls -->
            <div class="grid grid-cols-1 gap-4 mb-6" :class="showDealerDropdown ? 'md:grid-cols-4' : 'md:grid-cols-3'">
                <div v-if="showDealerDropdown">
                    <label for="dealer-select" class="block text-sm font-medium mb-2">Dealer</label>
                    <Dropdown
                        id="dealer-select"
                        v-model="selectedDealer"
                        :options="dealerOptions"
                        optionLabel="label"
                        optionValue="value"
                        placeholder="Select Dealer"
                        class="w-full"
                    />
                </div>

                <!-- Show assigned dealer info for DEALER_USER -->
                <div v-else-if="isDealerUser && userDealers.length > 0" class="md:col-span-1">
                    <label for="assigned-dealer" class="block text-sm font-medium mb-2">Assigned Dealer</label>
                    <div id="assigned-dealer" class="p-3 bg-surface-50 border border-surface-200 rounded-md">
                        <span class="font-medium">{{ selectedDealer }}</span>
                    </div>
                </div>
                
                <div>
                    <label for="date-from" class="block text-sm font-medium mb-2">From Date</label>
                    <Calendar
                        id="date-from"
                        v-model="dateFrom"
                        dateFormat="yy-mm-dd"
                        placeholder="Select start date"
                        class="w-full"
                    />
                </div>

                <div>
                    <label for="date-to" class="block text-sm font-medium mb-2">To Date</label>
                    <Calendar
                        id="date-to"
                        v-model="dateTo"
                        dateFormat="yy-mm-dd"
                        placeholder="Select end date"
                        class="w-full"
                    />
                </div>
                
                <div class="flex items-end">
                    <Button 
                        @click="fetchUnitInboundStatus"
                        :loading="loading"
                        label="Refresh"
                        icon="pi pi-refresh"
                        class="w-full"
                    />
                </div>
            </div>

            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Chart and Legend Container -->
            <div v-if="!error && Object.keys(chartData).length > 0" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Pie Chart -->
                <div class="lg:col-span-2 h-96">
                    <Chart
                        type="pie"
                        :data="chartData"
                        :options="chartOptions"
                        class="h-full"
                    />
                </div>

                <!-- Custom Legend -->
                <div class="lg:col-span-1 flex flex-col justify-center">
                    <h4 class="text-lg font-semibold mb-4 text-center text-surface-700">Status Distribution</h4>
                    <div class="space-y-3">
                        <div
                            v-for="(item, index) in legendItems"
                            :key="index"
                            class="flex items-center justify-between p-4 rounded-lg border border-surface-200 hover:bg-surface-50 transition-all duration-200 hover:shadow-md"
                        >
                            <div class="flex items-center space-x-3">
                                <div
                                    class="w-5 h-5 rounded-full flex-shrink-0 shadow-sm"
                                    :style="{ backgroundColor: item.color }"
                                ></div>
                                <span class="font-medium text-sm text-surface-700">{{ item.label }}</span>
                            </div>
                            <div class="text-right">
                                <div class="font-bold text-lg text-surface-800">{{ item.count }}</div>
                                <div class="text-xs text-surface-500 font-medium">{{ item.percentage }}%</div>
                            </div>
                        </div>
                    </div>

                    <!-- Total Summary -->
                    <div class="mt-4 p-3 bg-primary-50 rounded-lg border border-primary-200">
                        <div class="flex justify-between items-center">
                            <span class="font-semibold text-primary-700">Total Units</span>
                            <span class="font-bold text-xl text-primary-700">{{ totalRecords }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- No Data State -->
            <div v-else-if="!loading && !error" class="text-center py-8">
                <i class="pi pi-chart-pie text-4xl text-muted-color mb-4"></i>
                <p class="text-muted-color">No data available for the selected criteria</p>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-4xl text-primary mb-4"></i>
                <p class="text-muted-color">Loading chart data...</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
.h-96 {
    height: 24rem;
}
</style>
