<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Paginator from 'primevue/paginator';
import Button from 'primevue/button';
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
const leasingHistoryData = ref([]);
const totalRecords = ref(0);
const currentPage = ref(1);
const perPage = ref(20);

// Computed properties
const totalPages = computed(() => {
    return Math.ceil(totalRecords.value / perPage.value);
});

const paginatorFirst = computed(() => {
    return (currentPage.value - 1) * perPage.value;
});

// Methods
const fetchLeasingHistoryData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // TODO: Replace with real API endpoint
        const response = await axios.get('/api/v1/dashboard/leasing/data-history', {
            params: {
                dealer_id: props.dealerId,
                date_from: props.dateFrom,
                date_to: props.dateTo,
                page: currentPage.value,
                per_page: perPage.value
            }
        });

        if (response.data.success) {
            const data = response.data.data;
            totalRecords.value = response.data.total_records || 0;

            if (data.length === 0) {
                error.value = 'No leasing history data found for the selected criteria';
                leasingHistoryData.value = [];
                return;
            }

            leasingHistoryData.value = data.map((item, index) => ({
                no: ((currentPage.value - 1) * perPage.value) + index + 1,
                id_spk: item.id_spk || '-',
                id_dokumen_pengajuan: item.id_dokumen_pengajuan || '-',
                tgl_pengajuan: item.tgl_pengajuan ? formatDate(item.tgl_pengajuan) : '-',
                jumlah_dp: item.jumlah_dp ? formatCurrency(item.jumlah_dp) : '-',
                tenor: item.tenor ? `${item.tenor} bulan` : '-',
                jumlah_cicilan: item.jumlah_cicilan ? formatCurrency(item.jumlah_cicilan) : '-',
                nama_finance_company: item.nama_finance_company || '-'
            }));

        } else {
            error.value = response.data.message || 'Failed to fetch leasing history data';
        }
    } catch (err) {
        console.error('Error fetching leasing history data:', err);
        
        // Mock data for development
        const mockData = Array.from({ length: perPage.value }, (_, index) => ({
            no: ((currentPage.value - 1) * perPage.value) + index + 1,
            id_spk: `SPK${String(1000 + index).padStart(6, '0')}`,
            id_dokumen_pengajuan: `DOC${String(2000 + index).padStart(6, '0')}`,
            tgl_pengajuan: formatDate(new Date(2024, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1)),
            jumlah_dp: formatCurrency(Math.floor(Math.random() * 10000000) + 5000000),
            tenor: `${[12, 24, 36, 48][Math.floor(Math.random() * 4)]} bulan`,
            jumlah_cicilan: formatCurrency(Math.floor(Math.random() * 2000000) + 1000000),
            nama_finance_company: ['PT. Federal International Finance (FIF)', 'Adira Finance', 'PT. Summit Oto Finance', 'PT. Mega Finance', 'PT. BCA Finance'][Math.floor(Math.random() * 5)]
        }));
        
        leasingHistoryData.value = mockData;
        totalRecords.value = 150; // Mock total
        error.value = '';
    } finally {
        loading.value = false;
    }
};

const formatDate = (date) => {
    if (!date) return '-';
    const d = new Date(date);
    return d.toLocaleDateString('id-ID', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
};

const formatCurrency = (amount) => {
    if (!amount) return '-';
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
};

const onPageChange = (event) => {
    currentPage.value = event.page + 1;
    fetchLeasingHistoryData();
};

const exportData = () => {
    // TODO: Implement export functionality
    console.log('Export leasing history data');
    // This would typically call an API endpoint to generate and download a file
};

const filterData = () => {
    // TODO: Implement filter functionality
    console.log('Filter leasing history data');
    currentPage.value = 1;
    fetchLeasingHistoryData();
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    currentPage.value = 1;
    fetchLeasingHistoryData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchLeasingHistoryData();
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
                        @click="filterData"
                        :disabled="loading"
                    />
                    <Button
                        icon="pi pi-download"
                        size="small"
                        text
                        severity="secondary"
                        class="p-1"
                        @click="exportData"
                        :disabled="loading || leasingHistoryData.length === 0"
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
                    :value="leasingHistoryData"
                    :loading="loading"
                    :paginator="false"
                    :rows="perPage"
                    :first="paginatorFirst"
                    stripedRows
                    size="small"
                    class="text-xs"
                >
                    <Column field="no" header="No" style="width: 60px" class="text-center">
                        <template #body="{ data }">
                            <span class="font-medium">{{ data.no }}</span>
                        </template>
                    </Column>
                    
                    <Column field="id_spk" header="ID SPK" style="min-width: 120px">
                        <template #body="{ data }">
                            <span class="font-mono text-xs">{{ data.id_spk }}</span>
                        </template>
                    </Column>
                    
                    <Column field="id_dokumen_pengajuan" header="ID Dokumen Pengajuan" style="width: 150px">
                        <template #body="{ data }">
                            <div class="truncate max-w-xs font-mono text-xs" :title="data.id_dokumen_pengajuan">
                                {{ data.id_dokumen_pengajuan }}
                            </div>
                        </template>
                    </Column>
                    
                    <Column field="tgl_pengajuan" header="Tgl Pengajuan" style="min-width: 120px">
                        <template #body="{ data }">
                            <span class="text-xs">{{ data.tgl_pengajuan }}</span>
                        </template>
                    </Column>
                    
                    <Column field="jumlah_dp" header="Jumlah DP" style="min-width: 130px" class="text-right">
                        <template #body="{ data }">
                            <span class="font-medium text-xs">{{ data.jumlah_dp }}</span>
                        </template>
                    </Column>
                    
                    <Column field="tenor" header="Tenor" style="min-width: 100px" class="text-center">
                        <template #body="{ data }">
                            <span class="text-xs">{{ data.tenor }}</span>
                        </template>
                    </Column>
                    
                    <Column field="jumlah_cicilan" header="Jumlah Cicilan" style="min-width: 130px" class="text-right">
                        <template #body="{ data }">
                            <span class="font-medium text-xs">{{ data.jumlah_cicilan }}</span>
                        </template>
                    </Column>
                    
                    <Column field="nama_finance_company" header="Nama Finance Company" style="min-width: 200px">
                        <template #body="{ data }">
                            <div class="truncate max-w-xs text-xs" :title="data.nama_finance_company">
                                {{ data.nama_finance_company }}
                            </div>
                        </template>
                    </Column>
                </DataTable>

                <!-- Custom Pagination -->
                <div class="flex justify-between items-center pt-4 border-t border-surface-200">
                    <div class="text-xs text-muted-color">
                        Showing {{ paginatorFirst + 1 }} to {{ Math.min(paginatorFirst + perPage, totalRecords) }} of {{ totalRecords }} entries
                    </div>
                    <Paginator
                        :first="paginatorFirst"
                        :rows="perPage"
                        :totalRecords="totalRecords"
                        :rowsPerPageOptions="[10, 20, 50]"
                        @page="onPageChange"
                        template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
                        class="text-xs"
                    />
                </div>
            </div>

            <!-- No Data State -->
            <div v-if="!loading && !error && leasingHistoryData.length === 0" 
                 class="flex flex-col items-center justify-center h-64 text-surface-500">
                <i class="pi pi-table text-4xl mb-4"></i>
                <p class="text-lg font-medium">No Leasing History Data</p>
                <p class="text-sm">No data available for the selected period</p>
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
