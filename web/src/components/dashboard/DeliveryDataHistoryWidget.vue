<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import axios from 'axios';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Paginator from 'primevue/paginator';
import Message from 'primevue/message';
import Button from 'primevue/button';

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
const deliveryData = ref([]);
const totalRecords = ref(0);
const first = ref(0);
const rows = ref(20);

// Computed properties
const effectiveDealerId = computed(() => {
    return props.dealerId || '12284';
});

const currentPage = computed(() => {
    return Math.floor(first.value / rows.value) + 1;
});

// Methods
const fetchDeliveryDataHistory = async () => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call real API endpoint
        const response = await axios.get('/api/v1/dashboard/delivery/data-history', {
            params: {
                dealer_id: effectiveDealerId.value,
                date_from: props.dateFrom,
                date_to: props.dateTo,
                page: currentPage.value,
                per_page: rows.value
            }
        });

        if (response.data.success) {
            const data = response.data.data;

            if (data.length === 0 && currentPage.value === 1) {
                error.value = 'No delivery data found for the selected criteria';
                deliveryData.value = [];
                totalRecords.value = 0;
                return;
            }

            // Transform API response to component format
            deliveryData.value = data.map((item, index) => ({
                no: first.value + index + 1,
                idDeliveryDoc: item.delivery_document_id || '-',
                tglPengiriman: item.tanggal_pengiriman || '-',
                statusPengiriman: item.status_delivery_document || '-',
                namaDriver: item.id_driver || '-',
                idSpk: item.id_spk || '-',
                namaPenerima: item.nama_penerima || '-',
                noHpPenerima: item.no_kontak_penerima || '-',
                alamatPenerima: item.lokasi_pengiriman || '-',
                estimasiPengiriman: item.waktu_pengiriman || '-'
            }));

            totalRecords.value = response.data.total_records;
        } else {
            error.value = response.data.message || 'Failed to fetch delivery data history';
        }
    } catch (err) {
        console.error('Error fetching delivery data history:', err);
        error.value = 'Failed to fetch delivery data history';
    } finally {
        loading.value = false;
    }
};

// Pagination methods
const onPageChange = (event) => {
    first.value = event.first;
    rows.value = event.rows;
    fetchDeliveryDataHistory(); // Fetch new data when page changes
};

// Status badge styling
const getStatusSeverity = (status) => {
    switch (status) {
        case 'Completed':
            return 'success';
        case 'In Progress':
            return 'info';
        case 'Ready':
            return 'warning';
        case 'Back to Dealer':
            return 'danger';
        default:
            return 'secondary';
    }
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo],
    () => {
        fetchDeliveryDataHistory();
    },
    { deep: true }
);

// Lifecycle
onMounted(() => {
    fetchDeliveryDataHistory();
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

            <!-- Data Table -->
            <div v-if="!error" class="space-y-4">
                <DataTable :value="deliveryData" :loading="loading" :paginator="false" :rows="rows" :first="first" stripedRows size="small" class="text-xs">
                    <Column field="no" header="No" style="width: 60px">
                        <template #body="{ index }">
                            {{ first + index + 1 }}
                        </template>
                    </Column>
                    <Column field="idDeliveryDoc" header="ID Delivery Doc" style="width: 120px"></Column>
                    <Column field="tglPengiriman" header="Tgl Pengiriman" style="width: 100px"></Column>
                    <Column field="statusPengiriman" header="Status Pengiriman" style="width: 120px">
                        <template #body="{ data }">
                            <span
                                class="px-2 py-1 rounded-full text-xs font-medium"
                                :class="{
                                    'bg-green-100 text-green-800': data.statusPengiriman === 'Completed',
                                    'bg-blue-100 text-blue-800': data.statusPengiriman === 'In Progress',
                                    'bg-yellow-100 text-yellow-800': data.statusPengiriman === 'Ready',
                                    'bg-red-100 text-red-800': data.statusPengiriman === 'Back to Dealer'
                                }"
                            >
                                {{ data.statusPengiriman }}
                            </span>
                        </template>
                    </Column>
                    <Column field="namaDriver" header="Nama Driver" style="min-width: 120px"></Column>
                    <Column field="idSpk" header="ID SPK" style="width: 100px"></Column>
                    <Column field="namaPenerima" header="Nama Penerima" style="min-width: 120px"></Column>
                    <Column field="noHpPenerima" header="No Hp Penerima" style="width: 120px"></Column>
                    <Column field="alamatPenerima" header="Alamat Penerima" style="min-width: 200px">
                        <template #body="{ data }">
                            <div class="truncate max-w-xs" :title="data.alamatPenerima">
                                {{ data.alamatPenerima }}
                            </div>
                        </template>
                    </Column>
                    <Column field="estimasiPengiriman" header="Estimasi Pengiriman" style="width: 120px"></Column>
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
/* Custom styling for compact table */
:deep(.p-datatable-table) {
    font-size: 0.75rem;
}

:deep(.p-datatable-thead > tr > th) {
    padding: 0.5rem;
    font-size: 0.75rem;
    font-weight: 600;
}

:deep(.p-datatable-tbody > tr > td) {
    padding: 0.5rem;
}

:deep(.p-paginator) {
    padding: 0.5rem;
}

.truncate {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
</style>
