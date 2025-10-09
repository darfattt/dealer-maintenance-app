<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Sidebar from 'primevue/sidebar';
import Tag from 'primevue/tag';
import Paginator from 'primevue/paginator';
import ProgressSpinner from 'primevue/progressspinner';
import Dropdown from 'primevue/dropdown';
import Password from 'primevue/password';
import InputSwitch from 'primevue/inputswitch';
import DealerService from '@/service/DealerService';

const toast = useToast();
const confirm = useConfirm();

// Data state
const dealers = ref([]);
const loading = ref(false);
const totalRecords = ref(0);

// Pagination state
const pagination = reactive({
    page: 1,
    page_size: 10
});

// Filter state
const filters = reactive({
    search: '',
    is_active: null
});

// Filter options
const statusOptions = [
    { label: 'All', value: null },
    { label: 'Active', value: true },
    { label: 'Inactive', value: false }
];

// Edit sidebar state
const showEditSidebar = ref(false);
const editingDealer = ref(null);
const editForm = reactive({
    dealer_name: '',
    api_key: '',
    api_token: '',
    secret_key: '',
    fonnte_api_key: '',
    fonnte_api_url: 'https://api.fonnte.com/send',
    phone_number: '',
    google_location_url: '',
    is_active: true
});

// Load dealers data
const loadData = async () => {
    loading.value = true;
    try {
        const result = await DealerService.getAllDealers({
            page: pagination.page,
            page_size: pagination.page_size,
            search: filters.search || undefined,
            is_active: filters.is_active
        });

        if (result.success) {
            dealers.value = result.data;
            totalRecords.value = result.total_records;
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: result.message || 'Failed to load dealers',
                life: 5000
            });
        }
    } catch (error) {
        console.error('Error loading dealers:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'Failed to load dealer data',
            life: 5000
        });
    } finally {
        loading.value = false;
    }
};

// Handle search
const handleSearch = () => {
    pagination.page = 1; // Reset to first page
    loadData();
};

// Handle pagination
const onPageChange = (event) => {
    pagination.page = event.page + 1;
    pagination.page_size = event.rows;
    loadData();
};

// Clear filters
const clearFilters = () => {
    filters.search = '';
    filters.is_active = null;
    pagination.page = 1;
    loadData();
};

// Open edit sidebar
const openEditSidebar = async (dealer) => {
    try {
        //loading.value = true;
        const result = await DealerService.getDealerById(dealer.dealer_id);

        editingDealer.value = dealer;
        editForm.dealer_name = result.dealer_name;
        editForm.api_key = result.api_key || '';
        editForm.api_token = result.api_token || '';
        editForm.secret_key = result.secret_key || '';
        editForm.fonnte_api_key = result.fonnte_api_key || '';
        editForm.fonnte_api_url = result.fonnte_api_url || 'https://api.fonnte.com/send';
        editForm.phone_number = result.phone_number || '';
        editForm.google_location_url = result.google_location_url || '';
        editForm.is_active = result.is_active;

        showEditSidebar.value = true;
    } catch (error) {
        console.error('Error loading dealer details:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load dealer details',
            life: 5000
        });
    } finally {
        //loading.value = false;
    }
};

// Save dealer changes
const saveDealer = async () => {
    try {
        loading.value = true;
        const result = await DealerService.updateDealer(editingDealer.value.dealer_id, editForm);

        if (result.success) {
            toast.add({
                severity: 'success',
                summary: 'Success',
                detail: 'Dealer updated successfully',
                life: 5000
            });
            showEditSidebar.value = false;
            loadData(); // Reload data
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: result.message || 'Failed to update dealer',
                life: 5000
            });
        }
    } catch (error) {
        console.error('Error updating dealer:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'Failed to update dealer',
            life: 5000
        });
    } finally {
        loading.value = false;
    }
};

// Toggle dealer status with confirmation
const toggleStatus = (dealer) => {
    const newStatus = !dealer.is_active;
    const actionText = newStatus ? 'activate' : 'deactivate';
    const actionTextCap = newStatus ? 'Activate' : 'Deactivate';

    confirm.require({
        message: `Are you sure you want to ${actionText} dealer "${dealer.dealer_name}" (${dealer.dealer_id})?`,
        header: `${actionTextCap} Dealer`,
        icon: `pi pi-${newStatus ? 'check-circle' : 'exclamation-triangle'}`,
        acceptLabel: actionTextCap,
        rejectLabel: 'Cancel',
        acceptClass: newStatus ? 'p-button-success' : 'p-button-danger',
        accept: async () => {
            try {
                loading.value = true;
                const result = await DealerService.toggleDealerStatus(dealer.dealer_id, newStatus);

                if (result.success) {
                    const statusText = newStatus ? 'activated' : 'deactivated';
                    toast.add({
                        severity: 'success',
                        summary: 'Success',
                        detail: `Dealer ${dealer.dealer_name} ${statusText} successfully`,
                        life: 5000
                    });
                    loadData(); // Reload data
                } else {
                    toast.add({
                        severity: 'error',
                        summary: 'Error',
                        detail: result.message || 'Failed to update dealer status',
                        life: 5000
                    });
                }
            } catch (error) {
                console.error('Error toggling dealer status:', error);
                toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: error.response?.data?.detail || 'Failed to update dealer status',
                    life: 5000
                });
            } finally {
                loading.value = false;
            }
        }
    });
};

// Cancel edit
const cancelEdit = () => {
    showEditSidebar.value = false;
    editingDealer.value = null;
};

// Initialize
onMounted(() => {
    loadData();
});
</script>

<template>
    <div class="space-y-6">
        <!-- Header -->
        <div class="flex justify-between items-center">
            <div>
                <h1 class="text-3xl font-bold text-surface-900 dark:text-surface-0">Dealer Management</h1>
                <p class="text-muted-color mt-2">Manage all dealers in the system</p>
            </div>
        </div>

        <!-- Filters -->
        <Card>
            <template #content>
                <div class="flex flex-wrap gap-4 items-end">
                    <!-- Search -->
                    <div class="flex-1 min-w-[250px]">
                        <label for="search" class="block text-sm font-medium mb-2">Search</label>
                        <InputText
                            id="search"
                            v-model="filters.search"
                            placeholder="Search by dealer ID or name"
                            class="w-full"
                            @keyup.enter="handleSearch"
                        />
                    </div>

                    <!-- Status Filter -->
                    <div class="w-48">
                        <label for="status-filter" class="block text-sm font-medium mb-2">Status</label>
                        <Dropdown
                            id="status-filter"
                            v-model="filters.is_active"
                            :options="statusOptions"
                            optionLabel="label"
                            optionValue="value"
                            placeholder="Filter by status"
                            class="w-full"
                        />
                    </div>

                    <!-- Action Buttons -->
                    <div class="flex gap-2">
                        <Button label="Search" icon="pi pi-search" @click="handleSearch" />
                        <Button label="Clear" icon="pi pi-times" severity="secondary" @click="clearFilters" />
                    </div>
                </div>
            </template>
        </Card>

        <!-- Data Table -->
        <Card>
            <template #content>
                <div v-if="loading" class="flex justify-center items-center py-12">
                    <ProgressSpinner />
                </div>

                <DataTable
                    v-else
                    :value="dealers"
                    stripedRows
                    class="p-datatable-sm"
                    :loading="loading"
                >
                    <!-- Dealer ID -->
                    <Column field="dealer_id" header="Dealer ID" sortable style="min-width: 120px">
                        <template #body="{ data }">
                            <span class="font-semibold">{{ data.dealer_id }}</span>
                        </template>
                    </Column>

                    <!-- Dealer Name -->
                    <Column field="dealer_name" header="Dealer Name" sortable style="min-width: 250px" />

                    <!-- DGI API Configuration Status -->
                    <Column header="DGI API" style="min-width: 120px">
                        <template #body="{ data }">
                            <Tag
                                :value="data.dgi_api_configured ? 'Configured' : 'Not Set'"
                                :severity="data.dgi_api_configured ? 'success' : 'warn'"
                            />
                        </template>
                    </Column>

                    <!-- WhatsApp API Configuration Status -->
                    <Column header="WhatsApp" style="min-width: 120px">
                        <template #body="{ data }">
                            <Tag
                                :value="data.whatsapp_api_configured ? 'Configured' : 'Not Set'"
                                :severity="data.whatsapp_api_configured ? 'success' : 'warn'"
                            />
                        </template>
                    </Column>

                    <!-- Google Maps Configuration Status -->
                    <Column header="Google Maps" style="min-width: 130px">
                        <template #body="{ data }">
                            <Tag
                                :value="data.google_location_configured ? 'Configured' : 'Not Set'"
                                :severity="data.google_location_configured ? 'success' : 'warn'"
                            />
                        </template>
                    </Column>

                    <!-- Active Status -->
                    <Column header="Status" style="min-width: 120px">
                        <template #body="{ data }">
                            <Tag
                                :value="data.is_active ? 'Active' : 'Inactive'"
                                :severity="data.is_active ? 'success' : 'secondary'"
                            />
                        </template>
                    </Column>

                    <!-- Created At -->
                    <Column field="created_at" header="Created" style="min-width: 150px">
                        <template #body="{ data }">
                            {{ data.created_at ? new Date(data.created_at).toLocaleDateString() : '-' }}
                        </template>
                    </Column>

                    <!-- Updated At -->
                    <Column field="updated_at" header="Last Updated" style="min-width: 150px">
                        <template #body="{ data }">
                            {{ data.updated_at ? new Date(data.updated_at).toLocaleDateString() : '-' }}
                        </template>
                    </Column>

                    <!-- Actions -->
                    <Column header="Actions" style="min-width: 250px">
                        <template #body="{ data }">
                            <div class="flex gap-2">
                                <Button
                                    icon="pi pi-pencil"
                                    label="Edit"
                                    size="small"
                                    severity="info"
                                    @click="openEditSidebar(data)"
                                    v-tooltip.top="'Edit dealer information'"
                                />
                                <Button
                                    :icon="data.is_active ? 'pi pi-ban' : 'pi pi-check'"
                                    :label="data.is_active ? 'Deactivate' : 'Activate'"
                                    size="small"
                                    :severity="data.is_active ? 'danger' : 'success'"
                                    @click="toggleStatus(data)"
                                    v-tooltip.top="data.is_active ? 'Click to deactivate dealer' : 'Click to activate dealer'"
                                />
                            </div>
                        </template>
                    </Column>
                </DataTable>

                <!-- Pagination -->
                <div class="mt-4">
                    <Paginator
                        :rows="pagination.page_size"
                        :totalRecords="totalRecords"
                        :rowsPerPageOptions="[10, 20, 50, 100]"
                        @page="onPageChange"
                    />
                </div>
            </template>
        </Card>

        <!-- Edit Sidebar -->
        <Sidebar
            v-model:visible="showEditSidebar"
            position="right"
            :style="{ width: '500px' }"
            header="Edit Dealer"
        >
            <div class="flex flex-col gap-4 h-full">
                <!-- Basic Information Section -->
                <Card>
                    <template #title>
                        <div class="flex items-center gap-2">
                            <i class="pi pi-info-circle text-primary"></i>
                            <span>Basic Information</span>
                        </div>
                    </template>
                    <template #content>
                        <div class="space-y-4">
                            <!-- Dealer ID (Read-only) -->
                            <div>
                                <label class="block text-sm font-medium mb-2">Dealer ID</label>
                                <InputText
                                    :value="editingDealer?.dealer_id"
                                    disabled
                                    class="w-full"
                                />
                            </div>

                            <!-- Dealer Name -->
                            <div>
                                <label class="block text-sm font-medium mb-2">Dealer Name *</label>
                                <InputText
                                    v-model="editForm.dealer_name"
                                    class="w-full"
                                    placeholder="Enter dealer name"
                                />
                            </div>
                        </div>
                    </template>
                </Card>

                <!-- DGI API Configuration Section -->
                <Card>
                    <template #title>
                        <div class="flex items-center gap-2">
                            <i class="pi pi-key text-primary"></i>
                            <span>DGI API Configuration</span>
                        </div>
                    </template>
                    <template #content>
                        <div class="space-y-4">
                            <!-- API Key -->
                            <div>
                                <label class="block text-sm font-medium mb-2">API Key</label>
                                <Password
                                    v-model="editForm.api_key"
                                    class="w-full"
                                    placeholder="Enter API key"
                                    :feedback="false"
                                    toggleMask
                                    inputClass="w-full"
                                />
                                <small class="text-gray-500">DGI API authentication key</small>
                            </div>

                            <!-- 
                            <div>
                                <label class="block text-sm font-medium mb-2">API Token</label>
                                <Password
                                    v-model="editForm.api_token"
                                    class="w-full"
                                    placeholder="Enter API token"
                                    :feedback="false"
                                    toggleMask
                                    inputClass="w-full"
                                />
                                <small class="text-gray-500">DGI API access token</small>
                            </div>
                            API Token -->

                            <!-- Secret Key -->
                            <div>
                                <label class="block text-sm font-medium mb-2">Secret Key</label>
                                <Password
                                    v-model="editForm.secret_key"
                                    class="w-full"
                                    placeholder="Enter secret key"
                                    :feedback="false"
                                    toggleMask
                                    inputClass="w-full"
                                />
                                <small class="text-gray-500">DGI API secret key for encryption</small>
                            </div>
                        </div>
                    </template>
                </Card>

                <!-- WhatsApp/Fonnte Configuration Section -->
                <Card>
                    <template #title>
                        <div class="flex items-center gap-2">
                            <i class="pi pi-whatsapp text-primary"></i>
                            <span>WhatsApp Configuration</span>
                        </div>
                    </template>
                    <template #content>
                        <div class="space-y-4">
                            <!-- Phone Number -->
                            <div>
                                <label class="block text-sm font-medium mb-2">Phone Number</label>
                                <InputText
                                    v-model="editForm.phone_number"
                                    class="w-full"
                                    placeholder="e.g., 628123456789"
                                />
                                <small class="text-gray-500">WhatsApp business number (with country code)</small>
                            </div>

                            <!-- Fonnte API Key -->
                            <div>
                                <label class="block text-sm font-medium mb-2">Fonnte API Key</label>
                                <Password
                                    v-model="editForm.fonnte_api_key"
                                    class="w-full"
                                    placeholder="Enter Fonnte API key"
                                    :feedback="false"
                                    toggleMask
                                    inputClass="w-full"
                                />
                                <small class="text-gray-500">Fonnte WhatsApp API key</small>
                            </div>

                            <!-- Fonnte API URL -->
                            <div>
                                <label class="block text-sm font-medium mb-2">Fonnte API URL</label>
                                <InputText
                                    v-model="editForm.fonnte_api_url"
                                    class="w-full"
                                    placeholder="https://api.fonnte.com/send"
                                />
                                <small class="text-gray-500">Default: https://api.fonnte.com/send</small>
                            </div>
                        </div>
                    </template>
                </Card>

                <!-- Google Maps Configuration Section -->
                <Card>
                    <template #title>
                        <div class="flex items-center gap-2">
                            <i class="pi pi-map-marker text-primary"></i>
                            <span>Google Maps Configuration</span>
                        </div>
                    </template>
                    <template #content>
                        <div class="space-y-4">
                            <!-- Google Location URL -->
                            <div>
                                <label class="block text-sm font-medium mb-2">Google Location URL</label>
                                <InputText
                                    v-model="editForm.google_location_url"
                                    class="w-full"
                                    placeholder="https://maps.google.com/..."
                                />
                                <small class="text-gray-500">Google Maps location URL for review scraping</small>
                            </div>
                        </div>
                    </template>
                </Card>

                <!-- Status Section -->
                <Card>
                    <template #title>
                        <div class="flex items-center gap-2">
                            <i class="pi pi-cog text-primary"></i>
                            <span>Status</span>
                        </div>
                    </template>
                    <template #content>
                        <div class="flex items-center justify-between">
                            <div>
                                <label class="block text-sm font-medium mb-1">Active Status</label>
                                <small class="text-gray-500">Enable or disable this dealer</small>
                            </div>
                            <InputSwitch v-model="editForm.is_active" />
                        </div>
                    </template>
                </Card>

                <!-- Footer Buttons -->
                <div class="mt-auto pt-4 border-t flex gap-2 justify-end">
                    <Button label="Cancel" icon="pi pi-times" severity="secondary" @click="cancelEdit" />
                    <Button label="Save" icon="pi pi-check" @click="saveDealer" :disabled="!editForm.dealer_name" />
                </div>
            </div>
        </Sidebar>
    </div>
</template>

<style scoped>
.p-datatable-sm :deep(.p-datatable-tbody > tr > td) {
    padding: 0.5rem;
}

.p-sidebar {
    background: var(--p-surface-0);
}

/* Password component full width fix */
:deep(.p-password) {
    width: 100%;
}

:deep(.p-password input) {
    width: 100%;
}
</style>
