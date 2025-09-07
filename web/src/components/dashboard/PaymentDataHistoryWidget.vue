<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
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

// API configuration
const API_ENDPOINT = `/api/v1/dashboard/payment-data-history`;

// Methods
const fetchData = async (page = 1, perPage = 20) => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        console.log(`Fetching payment data history for dealer ${effectiveDealerId.value}, page ${page}, per_page ${perPage}`);

        const response = await axios.get(API_ENDPOINT, {
            params: {
                dealer_id: effectiveDealerId.value,
                date_from: props.dateFrom,
                date_to: props.dateTo,
                page: page,
                per_page: perPage
            }
        });

        if (response.data && response.data.success) {
            data.value = response.data.data || [];
            totalRecords.value = response.data.total_records || 0;

            console.log(`Successfully loaded ${data.value.length} payment records (total: ${totalRecords.value})`);
        } else {
            throw new Error(response.data?.message || 'Invalid response format');
        }
    } catch (err) {
        console.error('Error fetching payment data:', err);

        if (err.response) {
            // Server responded with error status
            error.value = `Server error: ${err.response.data?.detail || err.response.statusText}`;
        } else if (err.request) {
            // Request was made but no response received
            error.value = 'Network error: Unable to connect to server';
        } else {
            // Something else happened
            error.value = err.message || 'Failed to fetch payment data';
        }

        // Reset data on error
        data.value = [];
        totalRecords.value = 0;
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
        case 'New':
            return 'info';
        case 'Process':
            return 'warning';
        case 'Accepted':
            return 'success';
        case 'Done':
            return 'secondary';
        default:
            return 'info';
    }
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        first.value = 0;
        fetchData(1, rows.value);
    },
    { immediate: false }
);

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
                <DataTable :value="data" :loading="loading" stripedRows size="small" class="text-xs" :scrollable="true" scrollHeight="400px">
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
                            <span class="px-2 py-1 rounded-full text-xs font-medium" :class="data.tipe_pembayaran === 'Cash' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'">
                                {{ data.tipe_pembayaran }}
                            </span>
                        </template>
                    </Column>

                    <Column field="cara_bayar" header="Cara Bayar" style="min-width: 100px">
                        <template #body="{ data }">
                            <span class="px-2 py-1 rounded-full text-xs font-medium" :class="data.cara_bayar === 'Cash' ? 'bg-green-100 text-green-800' : 'bg-cyan-100 text-cyan-800'">
                                {{ data.cara_bayar }}
                            </span>
                        </template>
                    </Column>

                    <Column field="status" header="Status" style="min-width: 100px">
                        <template #body="{ data }">
                            <span
                                class="px-2 py-1 rounded-full text-xs font-medium"
                                :class="{
                                    'bg-blue-100 text-blue-800': data.status === 'New',
                                    'bg-yellow-100 text-yellow-800': data.status === 'Process',
                                    'bg-green-100 text-green-800': data.status === 'Accepted',
                                    'bg-gray-100 text-gray-800': data.status === 'Done'
                                }"
                            >
                                {{ data.status }}
                            </span>
                        </template>
                    </Column>
                </DataTable>

                <!-- Pagination -->
                <div class="flex justify-between items-center pt-4 border-t border-surface-200">
                    <div class="text-xs text-muted-color">Showing {{ first + 1 }} to {{ Math.min(first + rows, totalRecords) }} of {{ totalRecords }} entries</div>
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
