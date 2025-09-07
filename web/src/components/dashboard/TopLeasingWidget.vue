<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
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
const loading = ref(false);
const error = ref('');
const leasingData = ref([]);
const totalRecords = ref(0);

// Colors for top leasing companies
const chartColors = [
    '#3B82F6', // Blue
    '#10B981', // Green
    '#F59E0B', // Amber
    '#EF4444', // Red
    '#8B5CF6' // Purple
];

// Company logos mapping (can be enhanced later)
const companyLogos = {
    default: '🏦',
    adira: '🏛️',
    bca: '🏬',
    mega: '🏪',
    summit: '🏢',
    federal: '🏦'
};

// Get company logo based on name
const getCompanyLogo = (companyName) => {
    if (!companyName) return companyLogos.default;

    const name = companyName.toLowerCase();
    if (name.includes('adira')) return companyLogos.adira;
    if (name.includes('bca')) return companyLogos.bca;
    if (name.includes('mega')) return companyLogos.mega;
    if (name.includes('summit')) return companyLogos.summit;
    if (name.includes('federal')) return companyLogos.federal;

    return companyLogos.default;
};

// Methods
const fetchTopLeasingData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call the new top leasing companies API
        const response = await axios.get('/api/v1/dashboard/leasing/top-companies', {
            params: {
                dealer_id: props.dealerId,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            const data = response.data.data;
            totalRecords.value = response.data.total_records;

            if (data.length === 0) {
                error.value = 'No leasing company data found for the selected criteria';
                leasingData.value = [];
                return;
            }

            // Transform API response to component format
            const mappedData = data.map((item, index) => ({
                name: item.nama_finance_company || 'Unknown Company',
                count: item.count,
                color: chartColors[index % chartColors.length],
                logo: getCompanyLogo(item.nama_finance_company)
            }));

            leasingData.value = mappedData;
        } else {
            error.value = response.data.message || 'Failed to fetch top leasing data';
        }
    } catch (err) {
        console.error('Error fetching top leasing data:', err);
        error.value = 'Failed to fetch top leasing data';
    } finally {
        loading.value = false;
    }
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        fetchTopLeasingData();
    },
    { deep: true }
);

// Lifecycle
onMounted(() => {
    fetchTopLeasingData();
});
</script>

<template>
    <Card class="h-full">
        <template #content>
            <!-- Total Records Info -->
            <div v-if="totalRecords > 0" class="flex justify-end mb-4">
                <small class="text-muted-color"> Total: {{ totalRecords }} </small>
            </div>

            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Leasing Data -->
            <div v-if="!error && leasingData.length > 0" class="space-y-3">
                <div v-for="(leasing, index) in leasingData" :key="index" class="flex items-center justify-between p-3 rounded-lg border border-surface-200 hover:bg-surface-50 transition-colors">
                    <div class="flex items-center space-x-3">
                        <div class="text-2xl">{{ leasing.logo }}</div>
                        <div>
                            <div class="font-medium text-sm">{{ leasing.name }}</div>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-2xl font-bold" :style="{ color: leasing.color }">
                            {{ leasing.count }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading...</p>
            </div>
        </template>
    </Card>
</template>
