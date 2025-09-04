<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Paginator from 'primevue/paginator';
import Message from 'primevue/message';
import Button from 'primevue/button';
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
const unitInboundData = ref([]);
const totalRecords = ref(0);
const totalPages = ref(0);
const currentPage = ref(1);
const first = ref(0);
const rows = ref(20);

// Computed properties
const effectiveDealerId = computed(() => {
    return props.dealerId || '12284';
});

// Mock data for demonstration (will be replaced with real API later)
const mockUnitInboundData = [
    {
        id: 1,
        no_shipping_list: 'SL-2024-001',
        tgl_terima: '2024-01-15',
        no_invoice: 'INV-2024-001',
        status_shipping_list: 'Completed',
        tipe_unit: 'Scoopy Black',
        kuantitas_unit_diterima: 25
    },
    {
        id: 2,
        no_shipping_list: 'SL-2024-002',
        tgl_terima: '2024-01-16',
        no_invoice: 'INV-2024-002',
        status_shipping_list: 'In Progress',
        tipe_unit: 'Vario 160 Navy',
        kuantitas_unit_diterima: 15
    },
    {
        id: 3,
        no_shipping_list: 'SL-2024-003',
        tgl_terima: '2024-01-17',
        no_invoice: 'INV-2024-003',
        status_shipping_list: 'Pending',
        tipe_unit: 'Beat Cream',
        kuantitas_unit_diterima: 30
    }
];

// Generate mock data for fallback
const generateMockUnitInboundData = (page, perPage) => {
    const startIndex = (page - 1) * perPage;
    const endIndex = startIndex + perPage;
    const paginatedData = mockUnitInboundData.slice(startIndex, endIndex);

    // Transform mock data to component format
    const data = paginatedData.map((item, index) => ({
        no: startIndex + index + 1,
        no_shipping_list: item.no_shipping_list || '-',
        tgl_terima: item.tgl_terima || '-',
        no_invoice: item.no_invoice || '-',
        status_shipping_list: item.status_shipping_list || '-',
        tipe_unit: item.tipe_unit || '-',
        kuantitas_unit_diterima: item.kuantitas_unit_diterima || 0
    }));

    return {
        data: data,
        totalRecords: mockUnitInboundData.length
    };
};

// Methods
const fetchUnitInboundData = async (page = 1, perPage = rows.value) => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call the unit inbound data history API
        const response = await axios.get('/api/v1/dashboard/unit-inbound-data-history', {
            params: {
                dealer_id: effectiveDealerId.value,
                date_from: props.dateFrom,
                date_to: props.dateTo,
                page: page,
                per_page: perPage
            }
        });

        if (response.data.success) {
            unitInboundData.value = response.data.data || [];
            totalRecords.value = response.data.total_records || 0;
            totalPages.value = response.data.total_pages || 0;
            currentPage.value = response.data.page || 1;
        } else {
            throw new Error(response.data.message || 'Failed to fetch data');
        }
    } catch (err) {
        console.error('Error fetching unit inbound data:', err);

        // Use mock data as fallback
        const mockData = generateMockUnitInboundData(page, perPage);
        unitInboundData.value = mockData.data;
        totalRecords.value = mockData.totalRecords;
        totalPages.value = Math.ceil(mockData.totalRecords / perPage);
        currentPage.value = page;

        error.value = 'Failed to fetch unit inbound data';
    } finally {
        loading.value = false;
    }
};

// Status styling
const getStatusClass = (status) => {
    const statusClasses = {
        Completed: 'bg-green-100 text-green-800',
        'In Progress': 'bg-blue-100 text-blue-800',
        Pending: 'bg-yellow-100 text-yellow-800',
        Cancelled: 'bg-red-100 text-red-800'
    };
    return statusClasses[status] || 'bg-gray-100 text-gray-800';
};

// Pagination handler
const onPageChange = (event) => {
    first.value = event.first;
    rows.value = event.rows;
    const page = Math.floor(event.first / event.rows) + 1;
    fetchUnitInboundData(page, event.rows);
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        first.value = 0;
        currentPage.value = 1;
        fetchUnitInboundData();
    },
    { immediate: false }
);

// Lifecycle
onMounted(() => {
    fetchUnitInboundData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <span class="text-sm font-bold uppercase">DATA HISTORY</span>
                <div class="flex items-center space-x-2">
                    <!-- Filter Button (placeholder for future implementation) -->
                    <Button icon="pi pi-filter" size="small" text severity="secondary" class="p-1" />
                    <!-- Export Button (placeholder for future implementation) -->
                    <Button icon="pi pi-download" size="small" text severity="secondary" class="p-1" />
                </div>
            </div>
        </template>

        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Data Table -->
            <div v-if="!error" class="space-y-4">
                <DataTable :value="unitInboundData" :loading="loading" :paginator="false" :rows="rows" :first="first" stripedRows size="small" class="text-xs">
                    <Column field="no" header="No" style="width: 60px">
                        <template #body="{ data }">
                            {{ data.no }}
                        </template>
                    </Column>
                    <Column field="no_shipping_list" header="No Shipping List" style="width: 140px"></Column>
                    <Column field="tgl_terima" header="Tgl Terima" style="width: 120px"></Column>
                    <Column field="no_invoice" header="No Invoice" style="width: 140px"></Column>
                    <Column field="status_shipping_list" header="Status Shipping List" style="width: 150px">
                        <template #body="{ data }">
                            <span class="px-2 py-1 rounded-full text-xs font-medium" :class="getStatusClass(data.status_shipping_list)">
                                {{ data.status_shipping_list }}
                            </span>
                        </template>
                    </Column>
                    <Column field="tipe_unit" header="Tipe Unit" style="min-width: 150px"></Column>
                    <Column field="kuantitas_unit_diterima" header="Kuantitas Unit Diterima" style="width: 180px">
                        <template #body="{ data }">
                            <div class="text-center font-medium">
                                {{ data.kuantitas_unit_diterima }}
                            </div>
                        </template>
                    </Column>
                </DataTable>

                <!-- Custom Pagination -->
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
        </template>
    </Card>
</template>

<style scoped>
/* Custom styles for compact table */
.text-xs {
    font-size: 0.75rem;
}

.truncate {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.max-w-xs {
    max-width: 20rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .text-xs {
        font-size: 0.625rem;
    }
}
</style>
