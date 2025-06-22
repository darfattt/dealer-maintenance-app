<script setup>
import { ref, onMounted, watch } from 'vue';
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
const prospects = ref([]);
const totalRecords = ref(0);
const first = ref(0);
const rows = ref(10);

// Methods
const fetchDataHistory = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Dummy data matching the table structure in the image
        const dummyData = [
            {
                no: 1,
                idProspect: 'P001',
                namaLengkap: 'John Doe',
                alamat: 'Jl. Sudirman No. 123, Jakarta',
                noHp: '081234567890',
                tglProspect: '2024-01-15',
                status: 'Hot'
            },
            {
                no: 2,
                idProspect: 'P002',
                namaLengkap: 'Jane Smith',
                alamat: 'Jl. Thamrin No. 456, Jakarta',
                noHp: '081234567891',
                tglProspect: '2024-01-16',
                status: 'Medium'
            },
            {
                no: 3,
                idProspect: 'P003',
                namaLengkap: 'Bob Johnson',
                alamat: 'Jl. Gatot Subroto No. 789, Jakarta',
                noHp: '081234567892',
                tglProspect: '2024-01-17',
                status: 'Done'
            },
            {
                no: 4,
                idProspect: 'P004',
                namaLengkap: 'Alice Brown',
                alamat: 'Jl. Kuningan No. 321, Jakarta',
                noHp: '081234567893',
                tglProspect: '2024-01-18',
                status: 'Hot Deal'
            },
            {
                no: 5,
                idProspect: 'P005',
                namaLengkap: 'Charlie Wilson',
                alamat: 'Jl. Senayan No. 654, Jakarta',
                noHp: '081234567894',
                tglProspect: '2024-01-19',
                status: 'Low'
            }
        ];

        prospects.value = dummyData;
        totalRecords.value = dummyData.length;

    } catch (err) {
        console.error('Error fetching data history:', err);
        error.value = 'Failed to fetch data history';
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
        case 'Done':
            return 'success';
        case 'Hot Deal':
            return 'info';
        case 'Hot':
            return 'warning';
        case 'Medium':
            return 'secondary';
        case 'Low':
            return 'danger';
        default:
            return 'secondary';
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchDataHistory();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchDataHistory();
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
                    :value="prospects"
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
                    <Column field="idProspect" header="ID Prospect" style="width: 100px"></Column>
                    <Column field="namaLengkap" header="Nama Lengkap" style="min-width: 150px"></Column>
                    <Column field="alamat" header="Alamat" style="min-width: 200px">
                        <template #body="{ data }">
                            <div class="truncate max-w-xs" :title="data.alamat">
                                {{ data.alamat }}
                            </div>
                        </template>
                    </Column>
                    <Column field="noHp" header="No HP" style="width: 120px"></Column>
                    <Column field="tglProspect" header="Tgl Prospect" style="width: 100px"></Column>
                    <Column field="status" header="Status" style="width: 100px">
                        <template #body="{ data }">
                            <span 
                                class="px-2 py-1 rounded-full text-xs font-medium"
                                :class="{
                                    'bg-green-100 text-green-800': data.status === 'Done',
                                    'bg-blue-100 text-blue-800': data.status === 'Hot Deal',
                                    'bg-yellow-100 text-yellow-800': data.status === 'Hot',
                                    'bg-gray-100 text-gray-800': data.status === 'Medium',
                                    'bg-red-100 text-red-800': data.status === 'Low'
                                }"
                            >
                                {{ data.status }}
                            </span>
                        </template>
                    </Column>
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
