<script setup>
import { ref, reactive, computed, watch } from 'vue';
import { useTemplateVariables } from '@/composables/useTemplateVariables';
import { useConfirmDialog } from '@/composables/useConfirmDialog';
import { useToast } from 'primevue/usetoast';
import Sidebar from 'primevue/sidebar';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Tag from 'primevue/tag';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import WhatsAppTemplateService from '@/service/WhatsAppTemplateService';
import { formatIndonesiaDateTime } from '@/utils/dateFormatter';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    template: {
        type: Object,
        default: null
    },
    reminderTargetOptions: {
        type: Array,
        default: () => []
    }
});

const emit = defineEmits(['update:visible', 'template-updated']);

const toast = useToast();
const { confirmUnsavedChanges } = useConfirmDialog();
const { variablesByCategory, validateTemplate, generatePreview } = useTemplateVariables();

// Form state
const formData = reactive({
    id: '',
    template: '',
    reminder_target: '',
    reminder_type: ''
});

const originalData = ref(null);
const saving = ref(false);
const showPreview = ref(false);
const showAvailableVariables = ref(false);
const showTemplateLogs = ref(false);

// Template logs state
const templateLogs = ref([]);
const loadingLogs = ref(false);

// Form validation
const validation = computed(() => {
    return validateTemplate(formData.template);
});

const hasUnsavedChanges = computed(() => {
    if (!originalData.value) return false;
    return formData.template !== originalData.value.template || formData.reminder_target !== originalData.value.reminder_target || formData.reminder_type !== originalData.value.reminder_type;
});

const isValid = computed(() => {
    return formData.template.trim().length > 0 && formData.reminder_target.trim().length > 0 && formData.reminder_type.trim().length > 0 && validation.value.isValid;
});

const previewText = computed(() => {
    return generatePreview(formData.template);
});

// Get reminder target options without "All Targets"
const reminderTargetDropdownOptions = computed(() => {
    return props.reminderTargetOptions.filter((option) => option.value !== '');
});

// Initialize form with template data
const initializeForm = () => {
    if (props.template) {
        formData.id = props.template.id || '';
        formData.template = props.template.template || '';
        formData.reminder_target = props.template.reminder_target || '';
        formData.reminder_type = props.template.reminder_type || '';

        // Store original data for change detection
        originalData.value = {
            template: formData.template,
            reminder_target: formData.reminder_target,
            reminder_type: formData.reminder_type
        };
    } else {
        resetForm();
    }
};

const resetForm = () => {
    formData.id = '';
    formData.template = '';
    formData.reminder_target = '';
    formData.reminder_type = '';
    originalData.value = null;
    showPreview.value = false;
};

// Load template logs
const refreshTemplateLogs = async () => {
    if (!formData.id) return;

    loadingLogs.value = true;
    try {
        const response = await WhatsAppTemplateService.getTemplateLogs({
            template_id: formData.id,
            limit: 10,
            offset: 0
        });

        if (response.success) {
            templateLogs.value = response.data || [];
        }
    } catch (error) {
        console.error('Error fetching template logs:', error);
    } finally {
        loadingLogs.value = false;
    }
};

// Utility functions for logs
const getOperationSeverity = (operation) => {
    switch (operation) {
        case 'CREATE':
            return 'success';
        case 'UPDATE':
            return 'info';
        case 'DELETE':
            return 'danger';
        case 'COPY':
            return 'warning';
        default:
            return 'secondary';
    }
};

const formatDate = (dateString) => {
    return formatIndonesiaDateTime(dateString);
};

// Save template
const saveTemplate = async () => {
    if (!isValid.value) {
        toast.add({
            severity: 'warn',
            summary: 'Validation Error',
            detail: 'Please fix validation errors before saving',
            life: 3000
        });
        return;
    }

    saving.value = true;
    try {
        const updateData = {
            template: formData.template.trim(),
            reminder_target: formData.reminder_target,
            reminder_type: formData.reminder_type.trim()
        };

        const response = await WhatsAppTemplateService.updateTemplate(formData.id, updateData);

        if (response.success) {
            emit('template-updated');
        } else {
            throw new Error(response.message || 'Failed to update template');
        }
    } catch (error) {
        console.error('Error saving template:', error);
        toast.add({
            severity: 'error',
            summary: 'Save Error',
            detail: error.message || 'Failed to save template',
            life: 5000
        });
    } finally {
        saving.value = false;
    }
};

// Close sidebar with unsaved changes check
const closeSidebar = async () => {
    if (hasUnsavedChanges.value) {
        // const confirmed = await confirmUnsavedChanges();
        // if (!confirmed) return;
        
    }
    emit('update:visible', false);
};

// Watchers
watch(
    () => props.visible,
    (newVisible) => {
        if (newVisible) {
            initializeForm();
            refreshTemplateLogs();
        } else {
            showPreview.value = false;
            templateLogs.value = [];
        }
    }
);

watch(
    () => props.template,
    () => {
        if (props.visible) {
            initializeForm();
            refreshTemplateLogs();
        }
    }
);
</script>

<template>
    <Sidebar :visible="visible" @update:visible="$emit('update:visible', $event)" position="right" :style="{ width: '750px' }" header="Edit WhatsApp Template" :modal="false" @hide="closeSidebar">
        <div v-if="!template" class="text-center py-4">
            <Message severity="info" :closable="false"> No template selected for editing </Message>
        </div>

        <div v-else class="grid grid-cols-1 gap-4 h-full w-full">
            <!-- Template Information -->
            <Card class="w-full">
                <template #title>
                    <div class="flex align-items-center gap-2">
                        <i class="pi pi-info-circle text-primary"></i>
                        <span>Template Information</span>
                    </div>
                </template>
                <template #content>
                    <div class="grid">
                        <div class="col-12">
                            <small class="text-gray-600">Template ID: {{ template.id }}</small>
                        </div>
                        <div class="col-12" v-if="template.dealer_id">
                            <small class="text-gray-600">Dealer: {{ template.dealer_id }}</small>
                        </div>
                        <div class="col-12" v-else>
                            <Tag value="Global Template" severity="secondary" class="text-xs" />
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Edit Form -->
            <Card class="w-full">
                <template #title>
                    <div class="flex justify-content-between align-items-center">
                        <div class="flex align-items-center gap-2">
                            <i class="pi pi-pencil text-primary"></i>
                            <span>Edit Template</span>
                        </div>
                        <Button @click="showPreview = !showPreview" :icon="showPreview ? 'pi pi-eye-slash' : 'pi pi-eye'" :label="showPreview ? 'Hide Preview' : 'Show Preview'" text size="small" />
                    </div>
                </template>
                <template #content>
                    <div class="space-y-4">
                        <!-- Reminder Target -->
                        <div class="field">
                            <label for="reminder-target" class="block text-sm font-medium mb-2"> Reminder Target <span class="text-red-500">*</span> </label>
                            <Dropdown
                                id="reminder-target"
                                v-model="formData.reminder_target"
                                :options="reminderTargetDropdownOptions"
                                option-label="label"
                                option-value="value"
                                placeholder="Select reminder target"
                                class="w-full"
                                :class="{ 'p-invalid': !formData.reminder_target && formData.reminder_target !== '' }"
                            />
                        </div>

                        <!-- Reminder Type -->
                        <div class="field">
                            <label for="reminder-type" class="block text-sm font-medium mb-2"> Reminder Type <span class="text-red-500">*</span> </label>
                            <InputText id="reminder-type" v-model="formData.reminder_type" placeholder="Enter reminder type (e.g., H+30 tanggal beli (by WA))" class="w-full" :class="{ 'p-invalid': !formData.reminder_type.trim() }" maxlength="100" />
                            <small class="text-gray-500">{{ formData.reminder_type.length }}/100 characters</small>
                        </div>

                        <!-- Template Content -->
                        <div class="field">
                            <label for="template-content" class="block text-sm font-medium mb-2"> Template Content <span class="text-red-500">*</span> </label>
                            <Textarea
                                id="template-content"
                                v-model="formData.template"
                                placeholder="Enter your WhatsApp template content..."
                                :rows="8"
                                class="w-full"
                                :class="{ 'p-invalid': !formData.template.trim() || !validation.isValid }"
                                maxlength="2000"
                            />
                            <small class="text-gray-500">{{ formData.template.length }}/2000 characters</small>

                            <!-- Validation Messages -->
                            <div v-if="validation.errors.length > 0" class="mt-2">
                                <Message v-for="(error, index) in validation.errors" :key="index" severity="error" :closable="false" class="text-sm">
                                    {{ error }}
                                </Message>
                            </div>

                            <div v-if="validation.warnings.length > 0" class="mt-2">
                                <Message v-for="(warning, index) in validation.warnings" :key="index" severity="warn" :closable="false" class="text-sm">
                                    {{ warning }}
                                </Message>
                            </div>

                            <!-- Variable Count -->
                            <div v-if="validation.foundVariables > 0" class="mt-2">
                                <small class="text-blue-600">
                                    <i class="pi pi-info-circle"></i>
                                    {{ validation.foundVariables }} variable(s) found in template
                                </small>
                            </div>
                        </div>

                        <!-- Preview -->
                        <div v-if="showPreview && formData.template" class="field">
                            <label class="block text-sm font-medium mb-2">
                                <i class="pi pi-eye text-blue-500"></i>
                                Preview with Sample Data
                            </label>
                            <div class="p-3 border rounded-lg bg-gray-50">
                                <div class="text-sm whitespace-pre-wrap">{{ previewText }}</div>
                            </div>
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Available Variables (Expandable) -->
            <Card class="w-full">
                <template #title>
                    <div class="flex align-items-center justify-between">
                        <div class="flex align-items-center gap-2">
                            <i class="pi pi-code text-primary"></i>
                            <span>Available Variables</span>
                        </div>
                        <Button
                            @click="showAvailableVariables = !showAvailableVariables"
                            :icon="showAvailableVariables ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
                            size="small"
                            text
                            :label="showAvailableVariables ? 'Hide' : 'Show'"
                            v-tooltip.top="showAvailableVariables ? 'Hide available variables' : 'Show available variables'"
                        />
                    </div>
                </template>
                <template #content v-if="showAvailableVariables">
                    <div class="text-sm text-gray-600 mb-3">Copy and paste these variables into your template:</div>
                    <div class="space-y-3">
                        <div v-for="(variables, category) in variablesByCategory" :key="category">
                            <h5 class="text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">{{ category }}</h5>
                            <div class="grid gap-2">
                                <div v-for="variable in variables" :key="variable.variable" class="col-12 md:col-6 lg:col-4">
                                    <div class="p-2 border rounded bg-surface-50 dark:bg-surface-800">
                                        <div class="flex items-center justify-between">
                                            <code class="text-xs font-mono text-primary">{{ variable.variable }}</code>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Action Buttons -->
            <div class="flex justify-content-end gap-2 mt-auto">
                <Button @click="closeSidebar" label="Cancel" severity="secondary" :disabled="saving" />
                <Button @click="saveTemplate" label="Save Changes" icon="pi pi-save" :loading="saving" :disabled="!isValid || saving" />
            </div>

            <!-- Template Logs (Expandable) -->
            <Card class="w-full">
                <template #title>
                    <div class="flex align-items-center justify-between">
                        <div class="flex align-items-center gap-2">
                            <i class="pi pi-history text-primary"></i>
                            <span>Template History</span>
                        </div>
                        <div class="flex align-items-center gap-2">
                            <Button @click="refreshTemplateLogs" icon="pi pi-refresh" size="small" text v-tooltip.top="'Refresh logs'" />
                            <Button
                                @click="showTemplateLogs = !showTemplateLogs"
                                :icon="showTemplateLogs ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
                                size="small"
                                text
                                :label="showTemplateLogs ? 'Hide' : 'Show'"
                                v-tooltip.top="showTemplateLogs ? 'Hide template history' : 'Show template history'"
                            />
                        </div>
                    </div>
                </template>
                <template #content v-if="showTemplateLogs">
                    <div v-if="loadingLogs" class="text-center py-4">
                        <ProgressSpinner style="width: 30px; height: 30px" />
                    </div>
                    <div v-else-if="templateLogs.length === 0" class="text-center py-4 text-gray-500 text-sm">No recent operations for this template</div>
                    <div v-else class="space-y-2 max-h-48 overflow-y-auto">
                        <div v-for="log in templateLogs" :key="log.id" class="p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                            <div class="flex justify-between items-start">
                                <div class="flex-1 min-w-0">
                                    <div class="flex items-center gap-2">
                                        <Tag :value="log.operation" :severity="getOperationSeverity(log.operation)" class="text-xs" />
                                        <span class="text-sm font-medium text-gray-900">{{ log.operation }}</span>
                                    </div>
                                    <div class="text-xs text-gray-500 mt-1">
                                        {{ formatDate(log.operation_timestamp) }}
                                        <span v-if="log.user_email"> by {{ log.user_email }}</span>
                                    </div>
                                </div>
                            </div>
                            <div v-if="log.operation_notes" class="text-xs text-gray-600 mt-2">
                                {{ log.operation_notes }}
                            </div>
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Unsaved Changes Indicator -->
            <div v-if="hasUnsavedChanges" class="fixed bottom-4 right-4 z-5">
                <Tag value="Unsaved Changes" severity="warning" icon="pi pi-exclamation-triangle" />
            </div>
        </div>
    </Sidebar>
</template>

<style scoped>
.field {
    margin-bottom: 1rem;
}

.space-y-4 > * + * {
    margin-top: 1rem;
}

.p-sidebar {
    background: var(--p-surface-0);
}

.p-accordion .p-accordion-tab .p-accordion-header .p-accordion-header-link {
    padding: 0.75rem 1rem;
}

.p-accordion .p-accordion-tab .p-accordion-content {
    padding: 1rem;
}
</style>
