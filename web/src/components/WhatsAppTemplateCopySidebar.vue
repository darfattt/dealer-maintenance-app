<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useDealers } from '@/composables/useDealers';
import { useConfirmDialog } from '@/composables/useConfirmDialog';
import { useToast } from 'primevue/usetoast';
import Sidebar from 'primevue/sidebar';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import Checkbox from 'primevue/checkbox';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';
import WhatsAppTemplateService from '@/service/WhatsAppTemplateService';
import { formatIndonesiaDateTime } from '@/utils/dateFormatter';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['update:visible', 'templates-copied']);

const toast = useToast();
const { confirmCopy } = useConfirmDialog();
const { dealerOptions, isLoading: dealersLoading } = useDealers();

// Copy form state
const copyForm = reactive({
    sourceDealerId: '',
    targetDealerId: '',
    overwriteExisting: false
});

// Operation state
const copying = ref(false);
const copyResult = ref(null);
const sourceTemplateCount = ref(0);
const loadingSourceCount = ref(false);

// History state
const showHistory = ref(true);
const loadingHistory = ref(false);
const copyHistory = ref([]);

// Computed properties
const validDealers = computed(() => {
    return dealerOptions.value.filter((dealer) => dealer.value); // Exclude empty values
});

const targetDealerOptions = computed(() => {
    return validDealers.value.filter((dealer) => dealer.value !== copyForm.sourceDealerId);
});

const canProceedCopy = computed(() => {
    return copyForm.sourceDealerId && copyForm.targetDealerId && copyForm.sourceDealerId !== copyForm.targetDealerId && !copying.value;
});

// Load source template count when source dealer changes
const loadSourceTemplateCount = async () => {
    if (!copyForm.sourceDealerId) {
        sourceTemplateCount.value = 0;
        return;
    }

    loadingSourceCount.value = true;
    try {
        const response = await WhatsAppTemplateService.getTemplates({
            dealer_id: copyForm.sourceDealerId,
            page: 1,
            size: 1 // Only need count, so get minimal data
        });

        if (response.success) {
            sourceTemplateCount.value = response.pagination?.total || 0;
        } else {
            sourceTemplateCount.value = 0;
        }
    } catch (error) {
        console.error('Error loading source template count:', error);
        sourceTemplateCount.value = 0;
    } finally {
        loadingSourceCount.value = false;
    }
};

// Perform copy operation
const copyTemplates = async () => {
    console.log('Form data before validation:', {
        sourceDealerId: copyForm.sourceDealerId,
        targetDealerId: copyForm.targetDealerId,
        overwriteExisting: copyForm.overwriteExisting,
        canProceedCopy: canProceedCopy.value
    });

    if (!canProceedCopy.value) return;

    // Set copying flag immediately to protect form data during confirmation
    copying.value = true;
    copyResult.value = null;

    try {
        // Show confirmation dialog
        const confirmData = {
            source_dealer_id: copyForm.sourceDealerId,
            target_dealer_id: copyForm.targetDealerId,
            overwrite_existing: copyForm.overwriteExisting
        };
        const confirmed = await confirmCopy(confirmData, sourceTemplateCount.value);

        if (!confirmed) {
            // User cancelled - reset copying flag and return
            copying.value = false;
            return;
        }

        console.log('Form data before API call:', {
            source_dealer_id: copyForm.sourceDealerId,
            target_dealer_id: copyForm.targetDealerId,
            overwrite_existing: copyForm.overwriteExisting
        });
        const response = await WhatsAppTemplateService.copyTemplates({
            source_dealer_id: copyForm.sourceDealerId,
            target_dealer_id: copyForm.targetDealerId,
            overwrite_existing: copyForm.overwriteExisting
        });

        if (response.success) {
            copyResult.value = response;

            // Show success message
            const { data } = response;
            const successMessage = `Successfully copied ${data.templates_copied} template(s)${data.templates_skipped > 0 ? ` (${data.templates_skipped} skipped)` : ''}${
                data.templates_overwritten > 0 ? ` (${data.templates_overwritten} overwritten)` : ''
            }`;

            toast.add({
                severity: 'success',
                summary: 'Copy Successful',
                detail: successMessage,
                life: 5000
            });

            // Refresh history and notify parent
            await refreshHistory();
            emit('templates-copied');

            // Reset form after successful copy
            resetForm();
        } else {
            throw new Error(response.message || 'Failed to copy templates');
        }
    } catch (error) {
        console.error('Copy error:', error);
        toast.add({
            severity: 'error',
            summary: 'Copy Failed',
            detail: error.message || 'An error occurred during the copy operation',
            life: 5000
        });
    } finally {
        copying.value = false;
    }
};

// Reset form
const resetForm = () => {
    copyForm.sourceDealerId = '';
    copyForm.targetDealerId = '';
    copyForm.overwriteExisting = false;
    copyResult.value = null;
    sourceTemplateCount.value = 0;
};

// Load copy history
const refreshHistory = async () => {
    loadingHistory.value = false;
    // try {
    //     const response = await WhatsAppTemplateService.getTemplateLogs({
    //         operation: 'COPY',
    //         limit: 10,
    //         offset: 0
    //     });

    //     if (response.success) {
    //         copyHistory.value = response.data || [];
    //     }
    // } catch (error) {
    //     console.error('Error fetching copy history:', error);
    // } finally {
    //     loadingHistory.value = false;
    // }
};

// Utility functions
const formatDate = (dateString) => {
    return formatIndonesiaDateTime(dateString);
};

const getDealerName = (dealerId) => {
    const dealer = dealerOptions.value.find((d) => d.value === dealerId);
    return dealer ? dealer.label : dealerId;
};

const getStatusSeverity = (success) => {
    return success ? 'success' : 'danger';
};

// Watchers
watch(
    () => copyForm.sourceDealerId,
    () => {
        copyForm.targetDealerId = ''; // Reset target when source changes
        loadSourceTemplateCount();
    }
);

watch(
    () => props.visible,
    (newVisible) => {
        if (newVisible && showHistory.value) {
            //refreshHistory();
        }
        if (!newVisible && !copying.value) {
            resetForm();
        }
    }
);

// Lifecycle
onMounted(() => {
    if (props.visible && showHistory.value) {
        //refreshHistory();
    }
});
</script>

<template>
    <Sidebar :visible="visible" position="right" :style="{ width: '450px' }" @update:visible="$emit('update:visible', $event)" header="Copy WhatsApp Templates" :modal="false">
        <div class="flex flex-col gap-4 h-full">
            <!-- Copy Operation Section -->
            <Card>
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-copy text-primary"></i>
                        <span>Copy Templates</span>
                    </div>
                </template>
                <template #content>
                    <div class="space-y-4">
                        <!-- Source Dealer -->
                        <div class="field">
                            <label for="source-dealer" class="block text-sm font-medium mb-2"> Source Dealer <span class="text-red-500">*</span> </label>
                            <Dropdown
                                id="source-dealer"
                                v-model="copyForm.sourceDealerId"
                                :options="validDealers"
                                option-label="label"
                                option-value="value"
                                placeholder="Select source dealer"
                                class="w-full"
                                :loading="dealersLoading"
                                :disabled="copying"
                                appendTo="self"
                                @click.stop
                            />

                            <!-- Source Template Count -->
                            <div v-if="copyForm.sourceDealerId" class="mt-2">
                                <div v-if="loadingSourceCount" class="flex items-center gap-2">
                                    <ProgressSpinner style="width: 16px; height: 16px" />
                                    <small class="text-gray-600">Loading template count...</small>
                                </div>
                                <div v-else class="flex items-center gap-2">
                                    <i class="pi pi-info-circle text-blue-500"></i>
                                    <small class="text-blue-600"> {{ sourceTemplateCount }} template(s) found </small>
                                </div>
                            </div>
                        </div>

                        <!-- Target Dealer -->
                        <div class="field">
                            <label for="target-dealer" class="block text-sm font-medium mb-2"> Target Dealer <span class="text-red-500">*</span> </label>
                            <Dropdown
                                id="target-dealer"
                                v-model="copyForm.targetDealerId"
                                :options="targetDealerOptions"
                                option-label="label"
                                option-value="value"
                                placeholder="Select target dealer"
                                class="w-full"
                                :loading="dealersLoading"
                                :disabled="copying || !copyForm.sourceDealerId"
                                appendTo="self"
                                @click.stop
                            />
                        </div>

                        <!-- Overwrite Option -->
                        <div class="flex items-center gap-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                            <Checkbox v-model="copyForm.overwriteExisting" inputId="overwrite-checkbox" :binary="true" :disabled="copying" />
                            <div class="flex-1">
                                <label for="overwrite-checkbox" class="text-sm font-medium text-orange-800 cursor-pointer"> Overwrite existing templates </label>
                                <p class="text-xs text-orange-600 mt-1">If checked, existing templates with the same target and type will be overwritten. If unchecked, duplicates will be skipped.</p>
                            </div>
                        </div>

                        <!-- Copy Instructions -->
                        <div class="p-3 bg-blue-50 rounded-lg border border-blue-200">
                            <div class="text-xs text-blue-800">
                                <strong>Copy Process:</strong><br />
                                • All templates from the source dealer will be copied<br />
                                • Templates are matched by reminder target and type<br />
                                • Dealer-specific templates will be assigned to the target dealer<br />
                                • A complete audit log will be created for the operation
                            </div>
                        </div>

                        <!-- Copy Button -->
                        <Button @click="copyTemplates" :disabled="!canProceedCopy || sourceTemplateCount === 0" :loading="copying" label="Copy Templates" icon="pi pi-copy" class="w-full" severity="success" />
                    </div>
                </template>
            </Card>

            <!-- Copy Result -->
            <Card v-if="copyResult">
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-check-circle text-success"></i>
                        <span>Copy Result</span>
                    </div>
                </template>
                <template #content>
                    <div class="space-y-2">
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">Status:</span>
                            <Tag :value="copyResult.success ? 'SUCCESS' : 'FAILED'" :severity="getStatusSeverity(copyResult.success)" />
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">Templates Found:</span>
                            <span class="text-sm">{{ copyResult.data?.templates_found || 0 }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">Templates Copied:</span>
                            <span class="text-sm text-green-600">{{ copyResult.data?.templates_copied || 0 }}</span>
                        </div>
                        <div class="flex justify-between" v-if="copyResult.data?.templates_skipped > 0">
                            <span class="text-sm font-medium">Templates Skipped:</span>
                            <span class="text-sm text-gray-600">{{ copyResult.data?.templates_skipped || 0 }}</span>
                        </div>
                        <div class="flex justify-between" v-if="copyResult.data?.templates_overwritten > 0">
                            <span class="text-sm font-medium">Templates Overwritten:</span>
                            <span class="text-sm text-orange-600">{{ copyResult.data?.templates_overwritten || 0 }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">Overwrite Mode:</span>
                            <Tag :value="copyResult.data?.overwrite_existing ? 'Enabled' : 'Disabled'" :severity="copyResult.data?.overwrite_existing ? 'warning' : 'info'" class="text-xs" />
                        </div>

                        <!-- Show errors if any -->
                        <div v-if="copyResult.data?.errors && copyResult.data.errors.length > 0" class="mt-3">
                            <Message v-for="(error, index) in copyResult.data.errors" :key="index" severity="error" :closable="false" class="text-sm">
                                {{ error }}
                            </Message>
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Copy History -->
            <!-- <Card v-if="showHistory">
                <template #title>
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-history text-secondary"></i>
                            <span>Recent Copy Operations</span>
                        </div>
                        <Button @click="refreshHistory" icon="pi pi-refresh" size="small" text />
                    </div>
                </template>
                <template #content>
                    <div v-if="loadingHistory" class="text-center py-4">
                        <ProgressSpinner style="width: 30px; height: 30px" />
                    </div>
                    <div v-else-if="copyHistory.length === 0" class="text-center py-4 text-gray-500 text-sm">No recent copy operations</div>
                    <div v-else class="space-y-2 max-h-60 overflow-y-auto">
                        <div v-for="log in copyHistory" :key="log.id" class="p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                            <div class="flex justify-between items-start">
                                <div class="flex-1 min-w-0">
                                    <div class="text-sm font-medium text-gray-900">{{ getDealerName(log.source_dealer_id) }} → {{ getDealerName(log.target_dealer_id) }}</div>
                                    <div class="text-xs text-gray-500 mt-1">
                                        {{ formatDate(log.operation_timestamp) }}
                                    </div>
                                </div>
                                <Tag value="COPY" severity="info" class="ml-2 text-xs" />
                            </div>
                            <div v-if="log.operation_notes" class="text-xs text-gray-600 mt-2">
                                {{ log.operation_notes }}
                            </div>
                        </div>
                    </div>
                </template>
            </Card> -->
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

.space-y-2 > * + * {
    margin-top: 0.5rem;
}

.p-sidebar {
    background: var(--p-surface-0);
}
</style>
