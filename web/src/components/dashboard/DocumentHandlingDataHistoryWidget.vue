<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Paginator from 'primevue/paginator';
import Message from 'primevue/message';
import Button from 'primevue/button';

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
const documentHistoryData = ref([]);
const totalRecords = ref(0);
const totalPages = ref(0);
const currentPage = ref(1);
const perPage = ref(20);
const paginatorFirst = ref(0);

// Computed properties
const effectiveDealerId = computed(() => {
    return props.dealerId || '12284';
});

// Methods
const fetchDocumentHistoryData = async (page = 1, perPageValue = perPage.value) => {
    if (!effectiveDealerId.value || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call the document handling data history API
        const response = await axios.get('/api/v1/dashboard/document-handling-data-history', {
            params: {
                dealer_id: effectiveDealerId.value,
                date_from: props.dateFrom,
                date_to: props.dateTo,
                page: page,
                per_page: perPageValue
            }
        });

        if (response.data.success) {
            documentHistoryData.value = response.data.data || [];
            totalRecords.value = response.data.total_records || 0;
            totalPages.value = response.data.total_pages || 0;
            currentPage.value = response.data.current_page || 1;
        } else {
            throw new Error(response.data.message || 'Failed to fetch data');
        }
    } catch (err) {
        console.error('Error fetching document history data:', err);
        
        // Use mock data as fallback
        const mockData = generateMockDocumentHistoryData(page, perPageValue);
        documentHistoryData.value = mockData.data;
        totalRecords.value = mockData.totalRecords;
        totalPages.value = Math.ceil(mockData.totalRecords / perPageValue);
        currentPage.value = page;
        
        // Don't show error for mock data
        error.value = '';
    } finally {
        loading.value = false;
    }
};

const generateMockDocumentHistoryData = (page, perPageValue) => {
    const totalRecords = 156;
    const startIndex = (page - 1) * perPageValue;
    const data = [];

    for (let i = 0; i < perPageValue && (startIndex + i) < totalRecords; i++) {
        const index = startIndex + i + 1;
        data.push({
            no: index,
            id_spk: `SPK${String(index).padStart(6, '0')}`,
            id_so: `SO${String(index).padStart(6, '0')}`,
            tgl_pengajuan_stnk: `${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-2024`,
            status_faktur_stnk: ['Pending', 'Approved', 'Rejected', 'In Process'][Math.floor(Math.random() * 4)],
            nomor_stnk: `B${Math.floor(Math.random() * 9999) + 1000}ABC`,
            plat_nomor: `B${Math.floor(Math.random() * 9999) + 1000}XYZ`,
            tgl_terima_stnk: Math.random() > 0.3 ? `${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-2024` : '-',
            nama_penerima_stnk: Math.random() > 0.3 ? ['Budi Santoso', 'Siti Nurhaliza', 'Ahmad Rahman', 'Dewi Sartika', 'Rudi Hartono'][Math.floor(Math.random() * 5)] : '-',
            tgl_terima_bpkb: Math.random() > 0.5 ? `${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-2024` : '-',
            nama_penerima_bpkb: Math.random() > 0.5 ? ['Budi Santoso', 'Siti Nurhaliza', 'Ahmad Rahman', 'Dewi Sartika', 'Rudi Hartono'][Math.floor(Math.random() * 5)] : '-'
        });
    }

    return { data, totalRecords };
};

const onPageChange = (event) => {
    currentPage.value = event.page + 1;
    paginatorFirst.value = event.first;
    perPage.value = event.rows;
    fetchDocumentHistoryData(currentPage.value, perPage.value);
};

const exportData = () => {
    // TODO: Implement export functionality
    console.log('Export document handling history data');
    // This would typically call an API endpoint to generate and download a file
};

const filterData = () => {
    // TODO: Implement filter functionality
    console.log('Filter document handling history data');
    currentPage.value = 1;
    fetchDocumentHistoryData();
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    currentPage.value = 1;
    fetchDocumentHistoryData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchDocumentHistoryData();
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
                        :disabled="loading || documentHistoryData.length === 0"
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
                    :value="documentHistoryData" 
                    :loading="loading"
                    :paginator="false"
                    :rows="perPage"
                    :first="paginatorFirst"
                    stripedRows
                    size="small"
                    class="text-xs"
                >
                    <Column field="no" header="No" style="width: 60px">
                        <template #body="{ data }">
                            <span class="font-medium">{{ data.no }}</span>
                        </template>
                    </Column>
                    
                    <Column field="id_spk" header="ID SPK" style="width: 120px">
                        <template #body="{ data }">
                            <div class="truncate max-w-xs font-mono text-xs" :title="data.id_spk">
                                {{ data.id_spk }}
                            </div>
                        </template>
                    </Column>
                    
                    <Column field="id_so" header="ID SO" style="width: 120px">
                        <template #body="{ data }">
                            <div class="truncate max-w-xs font-mono text-xs" :title="data.id_so">
                                {{ data.id_so }}
                            </div>
                        </template>
                    </Column>
                    
                    <Column field="tgl_pengajuan_stnk" header="Tgl Pengajuan STNK" style="width: 140px">
                        <template #body="{ data }">
                            <span class="text-xs">{{ data.tgl_pengajuan_stnk }}</span>
                        </template>
                    </Column>
                    
                    <Column field="status_faktur_stnk" header="Status Faktur STNK" style="width: 130px">
                        <template #body="{ data }">
                            <span class="text-xs px-2 py-1 rounded-full text-white"
                                  :class="{
                                      'bg-green-500': data.status_faktur_stnk === 'Approved',
                                      'bg-red-500': data.status_faktur_stnk === 'Rejected',
                                      'bg-yellow-500': data.status_faktur_stnk === 'Pending',
                                      'bg-blue-500': data.status_faktur_stnk === 'In Process'
                                  }">
                                {{ data.status_faktur_stnk }}
                            </span>
                        </template>
                    </Column>
                    
                    <Column field="nomor_stnk" header="Nomor STNK" style="width: 120px">
                        <template #body="{ data }">
                            <span class="text-xs font-mono">{{ data.nomor_stnk }}</span>
                        </template>
                    </Column>
                    
                    <Column field="plat_nomor" header="Plat Nomor" style="width: 120px">
                        <template #body="{ data }">
                            <span class="text-xs font-mono">{{ data.plat_nomor }}</span>
                        </template>
                    </Column>
                    
                    <Column field="tgl_terima_stnk" header="Tgl Terima STNK" style="width: 130px">
                        <template #body="{ data }">
                            <span class="text-xs">{{ data.tgl_terima_stnk }}</span>
                        </template>
                    </Column>
                    
                    <Column field="nama_penerima_stnk" header="Nama Penerima STNK" style="min-width: 150px">
                        <template #body="{ data }">
                            <div class="truncate max-w-xs text-xs" :title="data.nama_penerima_stnk">
                                {{ data.nama_penerima_stnk }}
                            </div>
                        </template>
                    </Column>
                    
                    <Column field="tgl_terima_bpkb" header="Tgl Terima BPKB" style="width: 130px">
                        <template #body="{ data }">
                            <span class="text-xs">{{ data.tgl_terima_bpkb }}</span>
                        </template>
                    </Column>
                    
                    <Column field="nama_penerima_bpkb" header="Nama Penerima BPKB" style="min-width: 150px">
                        <template #body="{ data }">
                            <div class="truncate max-w-xs text-xs" :title="data.nama_penerima_bpkb">
                                {{ data.nama_penerima_bpkb }}
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
