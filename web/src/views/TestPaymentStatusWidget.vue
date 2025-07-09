<template>
    <div class="p-6">
        <div class="mb-6">
            <h1 class="text-2xl font-bold mb-4">Payment Status Widget Test</h1>
            <p class="text-gray-600">Testing the PaymentStatusWidget with real API integration</p>
        </div>

        <!-- Test Controls -->
        <div class="mb-6 p-4 bg-gray-50 rounded-lg">
            <h2 class="text-lg font-semibold mb-3">Test Parameters</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                    <label class="block text-sm font-medium mb-1">Dealer ID</label>
                    <input 
                        v-model="testParams.dealerId" 
                        type="text" 
                        class="w-full px-3 py-2 border border-gray-300 rounded-md"
                        placeholder="12284"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Date From</label>
                    <input 
                        v-model="testParams.dateFrom" 
                        type="date" 
                        class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Date To</label>
                    <input 
                        v-model="testParams.dateTo" 
                        type="date" 
                        class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    />
                </div>
            </div>
            <button 
                @click="refreshWidget" 
                class="mt-3 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
                Refresh Widget
            </button>
        </div>

        <!-- Widget Test -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Payment Status Widget -->
            <div>
                <h2 class="text-lg font-semibold mb-3">Payment Status Widget</h2>
                <div class="h-80">
                    <PaymentStatusWidget
                        :key="widgetKey"
                        :dealer-id="testParams.dealerId"
                        :date-from="testParams.dateFrom"
                        :date-to="testParams.dateTo"
                    />
                </div>
            </div>

            <!-- API Response Info -->
            <div>
                <h2 class="text-lg font-semibold mb-3">API Response Info</h2>
                <div class="p-4 bg-gray-100 rounded-lg">
                    <p><strong>Endpoint:</strong> /api/v1/dashboard/payment-status/statistics</p>
                    <p><strong>Method:</strong> GET</p>
                    <p><strong>Parameters:</strong></p>
                    <ul class="ml-4 mt-2">
                        <li>dealer_id: {{ testParams.dealerId }}</li>
                        <li>date_from: {{ testParams.dateFrom }}</li>
                        <li>date_to: {{ testParams.dateTo }}</li>
                    </ul>
                    <p class="mt-3"><strong>Expected Mapping:</strong></p>
                    <ul class="ml-4 mt-2">
                        <li>1 = New</li>
                        <li>2 = Process</li>
                        <li>3 = Accepted</li>
                        <li>4 = Close</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import PaymentStatusWidget from '@/components/dashboard/PaymentStatusWidget.vue';

// Test parameters
const testParams = ref({
    dealerId: '12284',
    dateFrom: '2020-01-01',
    dateTo: '2025-12-31'
});

// Widget key for forcing re-render
const widgetKey = ref(0);

// Methods
const refreshWidget = () => {
    widgetKey.value += 1;
};
</script>

<style scoped>
/* Add any specific styles for the test page */
</style>
