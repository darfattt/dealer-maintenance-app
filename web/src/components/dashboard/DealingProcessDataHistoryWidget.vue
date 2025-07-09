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
const spkData = ref([]);
const totalRecords = ref(0);
const totalPages = ref(0);
const currentPage = ref(1);
const first = ref(0);
const rows = ref(20);

// Computed properties
const effectiveDealerId = computed(() => {
    return props.dealerId || '12284';
});

// Methods
const fetchSPKDataHistory = async (page = 1, perPage = rows.value) => {
    if (!effectiveDealerId.value) {
        error.value = 'Missing dealer ID parameter';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call SPK dealing process API endpoint
        const response = await axios.get('/api/v1/dashboard/spk-dealing-process/data', {
            params: {
                dealer_id: effectiveDealerId.value,
                page: page,
                per_page: perPage
            }
        });

        if (response.data.success) {
            const data = response.data.data;
            
            if (data.length === 0 && page === 1) {
                error.value = 'No SPK dealing process data found for the selected criteria';
                spkData.value = [];
                totalRecords.value = 0;
                totalPages.value = 0;
                return;
            }

            // Transform API response to component format
            spkData.value = data.map((item, index) => ({
                no: ((page - 1) * perPage) + index + 1,
                id_spk: item.id_spk || '-',
                nama_customer: item.nama_customer || '-',
                alamat: item.alamat || '-',
                no_kontak: item.no_kontak || '-',
                email: item.email || '-',
                status_prospect: item.status_spk || '-', // Using status_spk from API
                nama_bpkbp: item.nama_bpkb || '-' // Using nama_bpkb from API
            }));

            totalRecords.value = response.data.total_records;
            totalPages.value = response.data.total_pages;
            currentPage.value = response.data.current_page;
            
        } else {
            error.value = response.data.message || 'Failed to fetch SPK dealing process data';
        }
    } catch (err) {
        console.error('Error fetching SPK dealing process data:', err);
        error.value = 'Failed to fetch SPK dealing process data';
    } finally {
        loading.value = false;
    }
};

// Pagination methods
const onPageChange = (event) => {
    first.value = event.first;
    rows.value = event.rows;
    
    const newPage = Math.floor(event.first / event.rows) + 1;
    fetchSPKDataHistory(newPage, event.rows);
};

// Status styling method for prospect status
const getStatusClass = (status) => {
    const statusClasses = {
        '1': 'bg-green-100 text-green-800', // Active/New
        '2': 'bg-blue-100 text-blue-800',   // In Progress
        '3': 'bg-yellow-100 text-yellow-800', // Follow Up
        '4': 'bg-red-100 text-red-800',    // Closed/Lost
        '5': 'bg-purple-100 text-purple-800', // Won
        '-': 'bg-gray-100 text-gray-800'   // Unknown/Default
    };
    return statusClasses[status] || 'bg-gray-100 text-gray-800';
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    first.value = 0; // Reset to first page
    fetchSPKDataHistory(1, rows.value);
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchSPKDataHistory();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <span class="text-sm font-bold uppercase">SPK DEALING PROCESS DATA HISTORY</span>
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
                    :value="spkData"
                    :loading="loading"
                    :paginator="false"
                    :rows="rows"
                    :first="first"
                    stripedRows
                    size="small"
                    class="text-xs"
                >
                    <Column field="no" header="No" style="width: 60px">
                        <template #body="{ data }">
                            {{ data.no }}
                        </template>
                    </Column>
                    <Column field="id_spk" header="ID SPK" style="width: 120px"></Column>
                    <Column field="nama_customer" header="Nama Customer" style="min-width: 150px"></Column>
                    <Column field="alamat" header="Alamat" style="min-width: 200px">
                        <template #body="{ data }">
                            <div class="truncate max-w-xs" :title="data.alamat">
                                {{ data.alamat }}
                            </div>
                        </template>
                    </Column>
                    <Column field="no_kontak" header="No Kontak" style="width: 120px"></Column>
                    <Column field="email" header="Email" style="min-width: 150px">
                        <template #body="{ data }">
                            <div class="truncate max-w-xs" :title="data.email">
                                {{ data.email }}
                            </div>
                        </template>
                    </Column>
                    <Column field="status_prospect" header="Status Prospect" style="width: 120px">
                        <template #body="{ data }">
                            <span class="px-2 py-1 rounded-full text-xs font-medium"
                                  :class="getStatusClass(data.status_prospect)">
                                {{ data.status_prospect }}
                            </span>
                        </template>
                    </Column>
                    <Column field="nama_bpkbp" header="Nama BPKBP" style="min-width: 150px"></Column>
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
