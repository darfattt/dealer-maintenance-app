<script setup>
import { ref, onMounted, computed, watch } from 'vue';
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
const rows = ref(10);

// Methods
const fetchDeliveryDataHistory = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Dummy data matching the table structure from the image
        const dummyData = [
            {
                no: 1,
                idDeliveryDoc: 'DD001',
                tglPengiriman: '2024-01-15',
                statusPengiriman: 'Completed',
                namaDriver: 'Muhammad Naufal',
                idSpk: 'SPK001',
                namaPenerima: 'John Doe',
                noHpPenerima: '081234567890',
                alamatPenerima: 'Jl. Sudirman No. 123, Jakarta',
                estimasiPengiriman: '2024-01-16'
            },
            {
                no: 2,
                idDeliveryDoc: 'DD002',
                tglPengiriman: '2024-01-16',
                statusPengiriman: 'In Progress',
                namaDriver: 'Anton Rahmad',
                idSpk: 'SPK002',
                namaPenerima: 'Jane Smith',
                noHpPenerima: '081234567891',
                alamatPenerima: 'Jl. Thamrin No. 456, Jakarta',
                estimasiPengiriman: '2024-01-17'
            },
            {
                no: 3,
                idDeliveryDoc: 'DD003',
                tglPengiriman: '2024-01-17',
                statusPengiriman: 'Ready',
                namaDriver: 'Valentio Nurul',
                idSpk: 'SPK003',
                namaPenerima: 'Bob Johnson',
                noHpPenerima: '081234567892',
                alamatPenerima: 'Jl. Gatot Subroto No. 789, Jakarta',
                estimasiPengiriman: '2024-01-18'
            },
            {
                no: 4,
                idDeliveryDoc: 'DD004',
                tglPengiriman: '2024-01-18',
                statusPengiriman: 'Back to Dealer',
                namaDriver: 'Ahmad Rizki',
                idSpk: 'SPK004',
                namaPenerima: 'Alice Brown',
                noHpPenerima: '081234567893',
                alamatPenerima: 'Jl. Kuningan No. 321, Jakarta',
                estimasiPengiriman: '2024-01-19'
            },
            {
                no: 5,
                idDeliveryDoc: 'DD005',
                tglPengiriman: '2024-01-19',
                statusPengiriman: 'Completed',
                namaDriver: 'Budi Santoso',
                idSpk: 'SPK005',
                namaPenerima: 'Charlie Wilson',
                noHpPenerima: '081234567894',
                alamatPenerima: 'Jl. Senayan No. 654, Jakarta',
                estimasiPengiriman: '2024-01-20'
            }
        ];

        deliveryData.value = dummyData;
        totalRecords.value = dummyData.length;

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
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchDeliveryDataHistory();
}, { deep: true });

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
                    <Button 
                        icon="pi pi-filter" 
                        size="small" 
                        text 
                        severity="secondary"
                        class="p-1"
                    />
                    <Button 
                        icon="pi pi-download" 
                        size="small" 
                        text 
                        severity="secondary"
                        class="p-1"
                    />
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
                <DataTable
                    :value="deliveryData"
                    :loading="loading"
                    :paginator="false"
                    :rows="rows"
                    :first="first"
                    stripedRows
                    size="small"
                    class="text-xs"
                >
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
                    <div class="text-xs text-muted-color">
                        Showing {{ first + 1 }} to {{ Math.min(first + rows, totalRecords) }} of {{ totalRecords }} entries
                    </div>
                    <Paginator
                        :first="first"
                        :rows="rows"
                        :totalRecords="totalRecords"
                        :rowsPerPageOptions="[5, 10, 20]"
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
