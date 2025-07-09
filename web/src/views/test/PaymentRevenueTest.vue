<template>
    <div class="p-6">
        <div class="mb-6">
            <h1 class="text-3xl font-bold text-surface-900 mb-2">Payment Revenue Widget Test</h1>
            <p class="text-muted-color">Testing the PaymentRevenueWidget with real API integration</p>
        </div>

        <!-- Test Controls -->
        <div class="mb-6 p-4 border border-surface-200 rounded-lg bg-surface-50">
            <h2 class="text-lg font-semibold mb-4">Test Parameters</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                    <label class="block text-sm font-medium mb-2">Dealer ID</label>
                    <input 
                        v-model="testParams.dealerId" 
                        type="text" 
                        class="w-full p-2 border border-surface-300 rounded"
                        placeholder="Enter dealer ID"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">Date From</label>
                    <input 
                        v-model="testParams.dateFrom" 
                        type="date" 
                        class="w-full p-2 border border-surface-300 rounded"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">Date To</label>
                    <input 
                        v-model="testParams.dateTo" 
                        type="date" 
                        class="w-full p-2 border border-surface-300 rounded"
                    />
                </div>
            </div>
            <button 
                @click="refreshWidget" 
                class="mt-4 px-4 py-2 bg-primary text-white rounded hover:bg-primary-600"
            >
                Refresh Widget
            </button>
        </div>

        <!-- Widget Test -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Payment Revenue Widget -->
            <div>
                <h2 class="text-lg font-semibold mb-4">Payment Revenue Widget</h2>
                <div class="h-64">
                    <PaymentRevenueWidget
                        :key="widgetKey"
                        :dealer-id="testParams.dealerId"
                        :date-from="testParams.dateFrom"
                        :date-to="testParams.dateTo"
                    />
                </div>
            </div>

            <!-- API Response Display -->
            <div>
                <h2 class="text-lg font-semibold mb-4">Direct API Test</h2>
                <div class="p-4 border border-surface-200 rounded-lg bg-surface-50 h-64 overflow-auto">
                    <button 
                        @click="testAPI" 
                        class="mb-4 px-3 py-1 bg-secondary text-white rounded text-sm hover:bg-secondary-600"
                        :disabled="apiLoading"
                    >
                        {{ apiLoading ? 'Testing...' : 'Test API Directly' }}
                    </button>
                    
                    <div v-if="apiError" class="text-red-600 text-sm mb-2">
                        Error: {{ apiError }}
                    </div>
                    
                    <pre v-if="apiResponse" class="text-xs bg-white p-2 rounded border overflow-auto">{{ JSON.stringify(apiResponse, null, 2) }}</pre>
                </div>
            </div>
        </div>

        <!-- Test Results -->
        <div class="mt-6 p-4 border border-surface-200 rounded-lg">
            <h2 class="text-lg font-semibold mb-4">Test Information</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                    <strong>Backend API Endpoint:</strong><br>
                    <code class="text-xs bg-surface-100 p-1 rounded">GET /api/v1/dashboard/payment-revenue/total</code>
                </div>
                <div>
                    <strong>Expected Response:</strong><br>
                    <code class="text-xs bg-surface-100 p-1 rounded">{ success: true, total_revenue: number, total_records: number }</code>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import axios from 'axios';
import PaymentRevenueWidget from '@/components/dashboard/PaymentRevenueWidget.vue';

// Test parameters
const testParams = reactive({
    dealerId: '12284',
    dateFrom: '2020-01-01',
    dateTo: '2025-12-31'
});

// Widget refresh key
const widgetKey = ref(0);

// API test data
const apiLoading = ref(false);
const apiError = ref('');
const apiResponse = ref(null);

// Methods
const refreshWidget = () => {
    widgetKey.value += 1;
};

const testAPI = async () => {
    apiLoading.value = true;
    apiError.value = '';
    apiResponse.value = null;

    try {
        const response = await axios.get('/api/v1/dashboard/payment-revenue/total', {
            params: {
                dealer_id: testParams.dealerId,
                date_from: testParams.dateFrom,
                date_to: testParams.dateTo
            }
        });

        apiResponse.value = response.data;
    } catch (err) {
        console.error('API test error:', err);
        apiError.value = err.response?.data?.detail || err.message || 'Unknown error';
        apiResponse.value = err.response?.data || null;
    } finally {
        apiLoading.value = false;
    }
};
</script>

<style scoped>
pre {
    font-family: 'Courier New', monospace;
    white-space: pre-wrap;
    word-wrap: break-word;
}

code {
    font-family: 'Courier New', monospace;
}
</style>
