<script setup>
import { ref, onMounted, watch } from 'vue';
import Card from 'primevue/card';
import Message from 'primevue/message';
import axios from 'axios';

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
const paymentData = ref([]);

// Methods
const fetchPaymentTypeData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call real API endpoint
        const response = await axios.get('/api/v1/dashboard/payment-type/statistics', {
            params: {
                dealer_id: props.dealerId,
                date_from: props.dateFrom,
                date_to: props.dateTo
            }
        });

        if (response.data.success) {
            // Transform API response to component format
            paymentData.value = response.data.data.map(item => ({
                type: mapPaymentType(item.tipe_pembayaran),
                amount: parseFloat(item.total_amount) || 0,
                color: getPaymentTypeColor(item.tipe_pembayaran)
            }));
        } else {
            error.value = response.data.message || 'Failed to fetch payment type data';
        }
    } catch (err) {
        console.error('Error fetching payment type data:', err);
        if (err.response?.status === 404) {
            error.value = 'Payment type data not available for this dealer';
        } else if (err.response?.status === 500) {
            error.value = 'Server error while fetching payment type data';
        } else {
            error.value = 'Failed to fetch payment type data';
        }
    } finally {
        loading.value = false;
    }
};

// Helper function to map payment type codes to labels
const mapPaymentType = (tipeCode) => {
    const typeMap = {
        '1': 'CASH',
        '2': 'CREDIT',
        '3': 'LEASING',
        'CASH': 'CASH',
        'CREDIT': 'CREDIT',
        'LEASING': 'LEASING'
    };
    return typeMap[tipeCode] || tipeCode || 'UNKNOWN';
};

// Helper function to get color for payment type
const getPaymentTypeColor = (paymentType) => {
    const colorMap = {
        '1': '#10B981',      // Cash - Green
        '2': '#3B82F6',      // Credit - Blue
        '3': '#F59E0B',      // Leasing - Orange
        'CASH': '#10B981',
        'CREDIT': '#3B82F6',
        'LEASING': '#F59E0B',
        'OTHER': '#6B7280'
    };
    return colorMap[paymentType] || '#6B7280';
};

// Helper function to format amount
const formatAmount = (amount) => {
    if (!amount || amount === 0) return '0';

    // Convert to millions for better readability
    const millions = amount / 1000000;

    if (millions >= 1000) {
        // Show in billions
        return `${(millions / 1000).toFixed(1)}B`;
    } else if (millions >= 1) {
        // Show in millions
        return `${millions.toFixed(0)}M`;
    } else {
        // Show in thousands
        return `${(amount / 1000).toFixed(0)}K`;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchPaymentTypeData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchPaymentTypeData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <span>Tipe Pembayaran</span>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Payment Type Data -->
            <div v-if="!error && paymentData.length > 0" class="space-y-4">
                <div
                    v-for="(payment, index) in paymentData"
                    :key="index"
                    class="flex items-center justify-between p-4 rounded-lg border border-surface-200"
                >
                    <div class="flex items-center space-x-3">
                        <div
                            class="w-4 h-4 rounded"
                            :style="{ backgroundColor: payment.color }"
                        ></div>
                        <span class="font-semibold text-lg">{{ payment.type }}</span>
                    </div>
                    <div class="text-right">
                        <div
                            class="text-2xl font-bold"
                            :style="{ color: payment.color }"
                        >
                            {{ formatAmount(payment.amount) }}
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
