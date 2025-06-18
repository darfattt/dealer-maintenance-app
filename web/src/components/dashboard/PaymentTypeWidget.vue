<script setup>
import { ref, onMounted, watch } from 'vue';
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
        // Dummy data for now
        paymentData.value = [
            { type: 'CASH', amount: 3256, color: '#10B981' },
            { type: 'CREDIT', amount: 2495, color: '#3B82F6' }
        ];
    } catch (err) {
        console.error('Error fetching payment type data:', err);
        error.value = 'Failed to fetch payment type data';
    } finally {
        loading.value = false;
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
                            {{ payment.amount.toLocaleString() }}
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
