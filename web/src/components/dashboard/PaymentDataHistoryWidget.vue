<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Paginator from 'primevue/paginator';
import Button from 'primevue/button';
import Message from 'primevue/message';

// Props from parent
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
const data = ref([]);
const totalRecords = ref(0);
const first = ref(0);
const rows = ref(20);

// Computed properties
const effectiveDealerId = computed(() => {
    return props.dealerId || '12284';
});

// Mock data for demonstration (will be replaced with real API later)
const generateMockData = (page = 1, perPage = 20) => {
    const paymentTypes = ['Cash', 'Credit'];
    const paymentMethods = ['Cash', 'Transfer'];
    const statuses = ['New', 'Process', 'Accepted', 'Done'];
    
    const mockData = [];
    const startIndex = (page - 1) * perPage;
    
    for (let i = 1; i <= perPage; i++) {
        const index = startIndex + i;
        mockData.push({
            no: index,
            id_invoice: `INV-${String(index).padStart(6, '0')}`,
            id_customer: `CUST-${String(index + 1000).padStart(4, '0')}`,
            amount: Math.floor(Math.random() * 50000000) + 5000000, // 5M - 55M
            tipe_pembayaran: paymentTypes[Math.floor(Math.random() * paymentTypes.length)],
            cara_bayar: paymentMethods[Math.floor(Math.random() * paymentMethods.length)],
            status: statuses[Math.floor(Math.random() * statuses.length)]
        });
    }
    
    return {
        data: mockData,
        total: 247 // Mock total records
    };
};

// Methods
const fetchData = async (page = 1, perPage = 20) => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // TODO: Replace with real API call when backend is ready
        // const response = await axios.get('/api/v1/dashboard/payment/data-history', {
        //     params: {
        //         dealer_id: effectiveDealerId.value,
        //         date_from: props.dateFrom,
        //         date_to: props.dateTo,
        //         page: page,
        //         per_page: perPage
        //     }
        // });

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Use mock data for now
        const mockResponse = generateMockData(page, perPage);
        data.value = mockResponse.data;
        totalRecords.value = mockResponse.total;

    } catch (err) {
        console.error('Error fetching payment data:', err);
        error.value = 'Failed to fetch payment data';
    } finally {
        loading.value = false;
    }
};

const onPageChange = (event) => {
    first.value = event.first;
    rows.value = event.rows;
    const page = Math.floor(event.first / event.rows) + 1;
    fetchData(page, event.rows);
};

const formatCurrency = (amount) => {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
};

const getStatusSeverity = (status) => {
    switch (status) {
        case 'New': return 'info';
        case 'Process': return 'warning';
        case 'Accepted': return 'success';
        case 'Done': return 'secondary';
        default: return 'info';
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    first.value = 0;
    fetchData(1, rows.value);
}, { immediate: false });

// Lifecycle
onMounted(() => {
    fetchData(1, rows.value);
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <span class="text-sm font-bold uppercase">DATA HISTORY</span>
                <div class="flex items-center space-x-2">
                    <Button icon="pi pi-filter" size="small" text severity="secondary" class="p-1" />
                    <Button icon="pi pi-download" size="small" text severity="secondary" class="p-1" />
                </div>
            </div>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <div v-if="!error" class="space-y-4">
                <!-- Data Table -->
                <DataTable 
                    :value="data" 
                    :loading="loading" 
                    stripedRows 
                    size="small" 
                    class="text-xs"
                    :scrollable="true"
                    scrollHeight="400px"
                >
                    <Column field="no" header="No" style="width: 60px">
                        <template #body="{ data, index }">
                            {{ first + index + 1 }}
                        </template>
                    </Column>
                    
                    <Column field="id_invoice" header="ID Invoice" style="min-width: 120px">
                        <template #body="{ data }">
                            <span class="font-mono text-xs">{{ data.id_invoice }}</span>
                        </template>
                    </Column>
                    
                    <Column field="id_customer" header="ID Customer" style="min-width: 120px">
                        <template #body="{ data }">
                            <span class="font-mono text-xs">{{ data.id_customer }}</span>
                        </template>
                    </Column>
                    
                    <Column field="amount" header="Amount" style="min-width: 140px">
                        <template #body="{ data }">
                            <span class="font-semibold text-green-600">{{ formatCurrency(data.amount) }}</span>
                        </template>
                    </Column>
                    
                    <Column field="tipe_pembayaran" header="Tipe Pembayaran" style="min-width: 120px">
                        <template #body="{ data }">
                            <span class="px-2 py-1 rounded-full text-xs font-medium"
                                  :class="data.tipe_pembayaran === 'Cash' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'">
                                {{ data.tipe_pembayaran }}
                            </span>
                        </template>
                    </Column>
                    
                    <Column field="cara_bayar" header="Cara Bayar" style="min-width: 100px">
                        <template #body="{ data }">
                            <span class="px-2 py-1 rounded-full text-xs font-medium"
                                  :class="data.cara_bayar === 'Cash' ? 'bg-green-100 text-green-800' : 'bg-cyan-100 text-cyan-800'">
                                {{ data.cara_bayar }}
                            </span>
                        </template>
                    </Column>
                    
                    <Column field="status" header="Status" style="min-width: 100px">
                        <template #body="{ data }">
                            <span class="px-2 py-1 rounded-full text-xs font-medium"
                                  :class="{
                                      'bg-blue-100 text-blue-800': data.status === 'New',
                                      'bg-yellow-100 text-yellow-800': data.status === 'Process',
                                      'bg-green-100 text-green-800': data.status === 'Accepted',
                                      'bg-gray-100 text-gray-800': data.status === 'Done'
                                  }">
                                {{ data.status }}
                            </span>
                        </template>
                    </Column>
                </DataTable>

                <!-- Pagination -->
                <div class="flex justify-between items-center pt-4 border-t border-surface-200">
                    <div class="text-xs text-muted-color">
                        Showing {{ first + 1 }} to {{ Math.min(first + rows, totalRecords) }} of {{ totalRecords }} entries
                    </div>
                    <Paginator 
                        :first="first" 
                        :rows="rows" 
                        :totalRecords="totalRecords" 
                        :rowsPerPageOptions="[10, 20, 50]" 
                        @page="onPageChange"
                        template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
                        class="text-xs"
                    />
                </div>
            </div>

            <!-- Empty State -->
            <div v-if="!loading && !error && data.length === 0" class="text-center py-8">
                <i class="pi pi-info-circle text-2xl text-muted-color mb-2"></i>
                <p class="text-muted-color text-sm">No payment data available</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* Custom scrollbar for data table */
:deep(.p-datatable-scrollable-body) {
    scrollbar-width: thin;
    scrollbar-color: #cbd5e1 #f1f5f9;
}

:deep(.p-datatable-scrollable-body::-webkit-scrollbar) {
    width: 6px;
}

:deep(.p-datatable-scrollable-body::-webkit-scrollbar-track) {
    background: #f1f5f9;
}

:deep(.p-datatable-scrollable-body::-webkit-scrollbar-thumb) {
    background-color: #cbd5e1;
    border-radius: 3px;
}

/* Responsive table adjustments */
@media (max-width: 768px) {
    :deep(.p-datatable) {
        font-size: 0.7rem;
    }
}
</style>
