<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useDealers } from '@/composables/useDealers';
import { useConfirmDialog } from '@/composables/useConfirmDialog';
import { useToast } from 'primevue/usetoast';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Paginator from 'primevue/paginator';
import Tag from 'primevue/tag';
import WhatsAppTemplateService from '@/service/WhatsAppTemplateService';
import WhatsAppTemplateEditSidebar from '@/components/WhatsAppTemplateEditSidebar.vue';
import WhatsAppTemplateCopySidebar from '@/components/WhatsAppTemplateCopySidebar.vue';
import { formatIndonesiaDateTime } from '@/utils/dateFormatter';

const authStore = useAuthStore();
const toast = useToast();
const { confirmDelete } = useConfirmDialog();

// Use dealers composable for dynamic dealer loading
const { dealerOptions, isLoading: dealersLoading } = useDealers();

// Role-based access control
const isAdmin = computed(() => authStore.userRole === 'SUPER_ADMIN');
const isDealerUser = computed(() => authStore.userRole === 'DEALER_ADMIN');
const showDealerDropdown = computed(() => isAdmin.value);
const canCopyTemplates = computed(() => isAdmin.value);

// Filter controls
const getInitialDealer = () => {
    if (isDealerUser.value) {
        return authStore.userDealerId;
    }
    return null; // Admin users start with no dealer filter (show all)
};

const filters = reactive({
    dealerId: getInitialDealer(),
    reminderTarget: '',
    templateContent: '',
    page: 1,
    size: 10
});

// Reminder target options
const reminderTargetOptions = ref([]);
const reminderTargetsLoading = ref(false);

// Templates data
const templates = ref([]);
const pagination = ref({
    page: 1,
    size: 10,
    total: 0,
    total_pages: 0,
    has_next: false,
    has_previous: false
});
const loading = ref(false);

// Sidebar states
const editSidebarVisible = ref(false);
const copySidebarVisible = ref(false);
const selectedTemplate = ref(null);

// Load reminder target options
const loadReminderTargets = async () => {
    reminderTargetsLoading.value = true;
    try {
        const response = await WhatsAppTemplateService.getReminderTargetOptions();
        if (response.success && response.data) {
            reminderTargetOptions.value = response.data;
        } else {
            console.warn('Failed to load reminder targets, using fallback');
            reminderTargetOptions.value = response.data || [];
        }
    } catch (error) {
        console.error('Error loading reminder targets:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load reminder target options',
            life: 3000
        });
    } finally {
        reminderTargetsLoading.value = false;
    }
};

// Load templates
const loadTemplates = async () => {
    loading.value = true;
    try {
        const response = await WhatsAppTemplateService.getTemplates({
            dealer_id: filters.dealerId,
            reminder_target: filters.reminderTarget || null,
            template: filters.templateContent || null,
            page: filters.page,
            size: filters.size
        });

        if (response.success) {
            templates.value = response.data || [];
            pagination.value = response.pagination || pagination.value;
        } else {
            throw new Error(response.message || 'Failed to load templates');
        }
    } catch (error) {
        console.error('Error loading templates:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: error.message || 'Failed to load WhatsApp templates',
            life: 5000
        });
        templates.value = [];
    } finally {
        loading.value = false;
    }
};

// Filter handlers
const handleFilterChange = () => {
    filters.page = 1; // Reset to first page when filters change
    loadTemplates();
};

const clearFilters = () => {
    if (!isDealerUser.value) {
        filters.dealerId = null;
    }
    filters.reminderTarget = '';
    filters.templateContent = '';
    filters.page = 1;
    loadTemplates();
};

// Pagination handler
const onPageChange = (event) => {
    filters.page = event.page + 1; // PrimeVue uses 0-based pages
    filters.size = event.rows;
    loadTemplates();
};

// Template actions
const handleEditTemplate = (template) => {
    selectedTemplate.value = { ...template };
    editSidebarVisible.value = true;
};

const handleDeleteTemplate = async (template) => {
    const confirmed = await confirmDelete(template);
    if (!confirmed) return;

    try {
        const response = await WhatsAppTemplateService.deleteTemplate(template.id);
        if (response.success) {
            toast.add({
                severity: 'success',
                summary: 'Success',
                detail: 'Template deleted successfully',
                life: 3000
            });
            await loadTemplates(); // Refresh the list
        } else {
            throw new Error(response.message || 'Failed to delete template');
        }
    } catch (error) {
        console.error('Error deleting template:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: error.message || 'Failed to delete template',
            life: 5000
        });
    }
};

const handleCopyTemplates = () => {
    copySidebarVisible.value = true;
};

// Sidebar event handlers
const onTemplateUpdated = () => {
    editSidebarVisible.value = false;
    selectedTemplate.value = null;
    loadTemplates();
    toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Template updated successfully',
        life: 3000
    });
};

const onTemplatesCopied = () => {
    copySidebarVisible.value = false;
    loadTemplates();
};

// Utility functions
const formatDate = (dateString) => {
    return formatIndonesiaDateTime(dateString);
};

const truncateText = (text, maxLength = 100) => {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
};

const getDealerDisplayName = (dealerId) => {
    if (!dealerId) return 'Global';
    const dealer = dealerOptions.value.find((d) => d.value === dealerId);
    return dealer ? dealer.label : dealerId;
};

// Watchers
watch(
    () => filters.dealerId,
    () => handleFilterChange(),
    { immediate: false }
);

watch(
    () => filters.reminderTarget,
    () => handleFilterChange(),
    { immediate: false }
);

// Lifecycle
onMounted(async () => {
    await Promise.all([loadReminderTargets(), loadTemplates()]);
});
</script>

<template>
    <div class="space-y-6">
        <!-- Filter Controls -->
        <div class="flex justify-end items-center space-x-4 mb-6">
            <!-- Dealer Filter (Admin only) -->
            <div v-if="showDealerDropdown" class="flex items-center space-x-2">
                <label for="dealer-filter" class="text-sm font-medium">Dealer:</label>
                <Dropdown
                    id="dealer-filter"
                    v-model="filters.dealerId"
                    :options="[{ label: 'All Dealers', value: null }, ...dealerOptions]"
                    option-label="label"
                    option-value="value"
                    placeholder="Select Dealer"
                    class="w-36"
                    :loading="dealersLoading"
                    show-clear
                />
            </div>

            <!-- Reminder Target Filter -->
            <div class="flex items-center space-x-2">
                <label for="target-filter" class="text-sm font-medium">Target:</label>
                <Dropdown id="target-filter" v-model="filters.reminderTarget" :options="reminderTargetOptions" option-label="label" option-value="value" placeholder="All Targets" class="w-36" :loading="reminderTargetsLoading" show-clear />
            </div>

            <!-- Template Content Filter -->
            <div class="flex items-center space-x-2">
                <label for="content-filter" class="text-sm font-medium">Content:</label>
                <InputText id="content-filter" v-model="filters.templateContent" placeholder="Search in template content..." class="w-48" @keyup.enter="handleFilterChange" />
            </div>

            <!-- Search and Clear Buttons -->
            <div class="flex items-center space-x-2">
                <Button @click="handleFilterChange" icon="pi pi-search" severity="primary" size="small" title="Search" />
                <Button @click="clearFilters" icon="pi pi-times" severity="secondary" size="small" title="Clear Filters" />
            </div>

            <!-- Action Buttons -->
            <div class="flex items-center space-x-2">
                <Button v-if="canCopyTemplates" @click="handleCopyTemplates" label="Copy Templates" icon="pi pi-copy" severity="info" size="small" />
                <Button @click="loadTemplates" icon="pi pi-refresh" severity="secondary" size="small" title="Refresh" />
            </div>
        </div>

        <!-- Templates Table -->
        <Card>
            <template #title>
                <h2 class="text-xl font-bold text-surface-900 dark:text-surface-0">WhatsApp Template Management</h2>
            </template>
            <template #content>
                <DataTable :value="templates" :loading="loading" responsiveLayout="scroll" :paginator="false" dataKey="id" class="p-datatable-customers" :empty-message="loading ? 'Loading templates...' : 'No templates found'" striped-rows>
                    <!-- No (Index) Column -->
                    <Column header="No" style="min-width: 60px">
                        <template #body="{ index }">
                            <span class="font-medium text-sm">
                                {{ (pagination.page - 1) * pagination.size + index + 1 }}
                            </span>
                        </template>
                    </Column>

                    <Column field="reminder_target" header="Reminder Target"  style="min-width: 150px">
                        <template #body="{ data }">
                            <Tag :value="data.reminder_target" severity="info" />
                        </template>
                    </Column>

                    <Column field="reminder_type" header="Reminder Type"  style="min-width: 180px">
                        <template #body="{ data }">
                            <span class="text-sm">{{ data.reminder_type }}</span>
                        </template>
                    </Column>

                    <Column field="template" header="Template Content" style="min-width: 200px">
                        <template #body="{ data }">
                            <div class="text-sm cursor-help" v-tooltip.left="data.template || 'No template content'">
                                {{ truncateText(data.template, 80) }}
                            </div>
                        </template>
                    </Column>

                    <Column field="dealer_id" header="Dealer" v-if="showDealerDropdown" style="min-width: 120px">
                        <template #body="{ data }">
                            <Tag :value="getDealerDisplayName(data.dealer_id)" :severity="data.dealer_id ? 'success' : 'secondary'" class="text-xs" />
                        </template>
                    </Column>

                    <!-- <Column field="last_modified_date" header="Last Modified"  style="min-width: 150px">
                        <template #body="{ data }">
                            <div class="text-xs text-gray-600">
                                <div>{{ formatDate(data.last_modified_date) }}</div>
                                <div v-if="data.last_modified_by" class="text-gray-500">by {{ data.last_modified_by }}</div>
                            </div>
                        </template>
                    </Column> -->

                    <Column header="Actions" :exportable="false" style="min-width: 120px">
                        <template #body="{ data }">
                            <div class="flex gap-2">
                                <Button @click="handleEditTemplate(data)" icon="pi pi-pencil" severity="info" text size="small" v-tooltip.top="'Edit template'" />
                                <Button @click="handleDeleteTemplate(data)" icon="pi pi-trash" severity="danger" text size="small" v-tooltip.top="'Delete template'" />
                            </div>
                        </template>
                    </Column>
                </DataTable>

                <!-- Pagination -->
                <Paginator v-if="pagination.total > 0" :rows="pagination.size" :totalRecords="pagination.total" :rowsPerPageOptions="[10, 20, 50]" @page="onPageChange" class="mt-4" />

                <!-- Empty State -->
                <div v-if="!loading && templates.length === 0" class="text-center py-8">
                    <i class="pi pi-comments text-gray-400 text-4xl mb-3"></i>
                    <h3 class="text-gray-600 mb-2">No Templates Found</h3>
                    <p class="text-gray-500 text-sm mb-4">
                        {{ filters.dealerId || filters.reminderTarget || filters.templateContent ? 'Try adjusting your filters to see more results.' : 'No WhatsApp templates have been configured yet.' }}
                    </p>
                </div>
            </template>
        </Card>
    </div>

    <!-- Edit Template Sidebar -->
    <WhatsAppTemplateEditSidebar v-model:visible="editSidebarVisible" :template="selectedTemplate" :reminder-target-options="reminderTargetOptions" @template-updated="onTemplateUpdated" />

    <!-- Copy Templates Sidebar (Admin only) -->
    <WhatsAppTemplateCopySidebar v-if="canCopyTemplates" v-model:visible="copySidebarVisible" @templates-copied="onTemplatesCopied" />
</template>

<style scoped>
/* Custom styles for the WhatsApp template management page */

/* Section spacing */
.space-y-6 > * + * {
    margin-top: 1.5rem;
}

/* Card hover effects */
:deep(.p-card) {
    transition: box-shadow 0.2s ease;
}

:deep(.p-card:hover) {
    box-shadow: 0 4px 25px 0 rgba(0, 0, 0, 0.1);
}

/* Responsive grid adjustments */
@media (max-width: 768px) {
    .grid.md\:grid-cols-4 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
    }
}

/* Table responsive styling */
:deep(.p-datatable-customers .p-datatable-tbody > tr > td) {
    padding: 0.75rem 1rem;
}

:deep(.p-datatable-customers .p-datatable-thead > tr > th) {
    background-color: var(--surface-50);
    font-weight: 600;
}

/* Status tag styling */
:deep(.p-tag) {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
}

/* Filter controls responsive */
@media (max-width: 1024px) {
    .flex.justify-end {
        flex-wrap: wrap;
        gap: 0.5rem;
    }
}

/* Button spacing adjustments */
.space-x-4 > * + * {
    margin-left: 1rem;
}

.space-x-2 > * + * {
    margin-left: 0.5rem;
}

/* Responsive filter layout for smaller screens */
@media (max-width: 768px) {
    .flex.justify-end.items-center.space-x-4 {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }

    .flex.items-center.space-x-2 {
        flex-direction: row;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .w-36,
    .w-48 {
        width: 100%;
        min-width: 200px;
    }
}

/* Dark mode support for text colors */
@media (prefers-color-scheme: dark) {
    .text-gray-400 {
        color: rgb(156 163 175);
    }

    .text-gray-500 {
        color: rgb(107 114 128);
    }

    .text-gray-600 {
        color: rgb(75 85 99);
    }
}
</style>
