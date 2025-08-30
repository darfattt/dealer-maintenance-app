<template>
    <Sidebar 
        :visible="visible" 
        position="right" 
        :style="{ width: '400px' }"
        @update:visible="$emit('update:visible', $event)"
        header="Upload Customer Satisfaction"
        :modal="false"
    >
        <div class="flex flex-col gap-4 h-full">
            <!-- File Upload Section -->
            <Card>
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-upload text-primary"></i>
                        <span>Upload File</span>
                    </div>
                </template>
                <template #content>
                    <div class="space-y-4">
                        <!-- File Upload Component -->
                        <FileUpload
                            mode="basic"
                            :auto="false"
                            accept=".xlsx,.xls,.csv"
                            :maxFileSize="10000000"
                            chooseLabel="Choose File"
                            chooseIcon="pi pi-file"
                            @select="onFileSelect"
                            class="w-full"
                        />
                        
                        <!-- File Info -->
                        <div v-if="selectedFile" class="p-3 bg-gray-50 rounded-lg border">
                            <div class="flex items-center gap-2 text-sm">
                                <i class="pi pi-file-excel text-green-600"></i>
                                <span class="font-medium">{{ selectedFile.name }}</span>
                            </div>
                            <div class="text-xs text-gray-600 mt-1">
                                Size: {{ formatFileSize(selectedFile.size) }}
                            </div>
                        </div>
                        
                        <!-- Override Option -->
                        <div class="flex items-center gap-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                            <Checkbox 
                                v-model="overrideExisting" 
                                inputId="override-checkbox" 
                                :binary="true"
                            />
                            <div class="flex-1">
                                <label for="override-checkbox" class="text-sm font-medium text-orange-800 cursor-pointer">
                                    Override existing records
                                </label>
                                <!-- <p class="text-xs text-orange-600 mt-1">
                                    Replace records with same No Tiket. If unchecked, duplicates will be skipped.
                                </p> -->
                            </div>
                        </div>
                        
                        <!-- Reformat Dates Option -->
                        <!-- <div class="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                            <Checkbox 
                                v-model="reformatDates" 
                                inputId="reformat-checkbox" 
                                :binary="true"
                            />
                            <div class="flex-1">
                                <label for="reformat-checkbox" class="text-sm font-medium text-blue-800 cursor-pointer">
                                    Reformat tanggal_rating to Indonesian format
                                </label>
                                <p class="text-xs text-blue-600 mt-1">
                                    Convert dates like "24-12-2024" or "2024-12-24" to "24 Desember 2024". Invalid formats will still be rejected.
                                </p>
                            </div>
                        </div> -->
                        
                        <!-- Upload Instructions -->
                        <div class="p-3 bg-blue-50 rounded-lg border border-blue-200">
                            <div class="text-xs text-blue-800">
                                <strong>File Format:</strong> Excel (.xlsx, .xls) or CSV<br>
                                <strong>Max Size:</strong> 10MB<br>
                                <strong>Required Columns:</strong> No Tiket, Nama Konsumen, No AHASS<br>
                                <strong>Duplicate Key:</strong> No Tiket (used for override detection)
                            </div>
                        </div>
                        
                        <!-- Upload Button -->
                        <Button 
                            @click="uploadFile"
                            :disabled="!selectedFile || uploading"
                            :loading="uploading"
                            label="Upload File"
                            icon="pi pi-upload"
                            class="w-full"
                            severity="success"
                        />
                    </div>
                </template>
            </Card>
            
            <!-- Upload Progress -->
            <Card v-if="uploadResult">
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-info-circle text-info"></i>
                        <span>Upload Result</span>
                    </div>
                </template>
                <template #content>
                    <div class="space-y-2">
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">Status:</span>
                            <Tag 
                                :value="uploadResult.data?.upload_status || 'UNKNOWN'"
                                :severity="getStatusSeverity(uploadResult.data?.upload_status)"
                            />
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">Total Records:</span>
                            <span class="text-sm">{{ uploadResult.data?.total_records || 0 }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">Successful:</span>
                            <span class="text-sm text-green-600">{{ uploadResult.data?.successful_records || 0 }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm font-medium">Failed:</span>
                            <span class="text-sm text-red-600">{{ uploadResult.data?.failed_records || 0 }}</span>
                        </div>
                        <div v-if="uploadResult.data?.replaced_records !== undefined" class="flex justify-between">
                            <span class="text-sm font-medium">Replaced:</span>
                            <span class="text-sm text-orange-600">{{ uploadResult.data?.replaced_records || 0 }}</span>
                        </div>
                        <div v-if="uploadResult.data?.skipped_records !== undefined" class="flex justify-between">
                            <span class="text-sm font-medium">Skipped:</span>
                            <span class="text-sm text-gray-600">{{ uploadResult.data?.skipped_records || 0 }}</span>
                        </div>
                        <div v-if="uploadResult.data?.success_rate" class="flex justify-between">
                            <span class="text-sm font-medium">Success Rate:</span>
                            <span class="text-sm">{{ uploadResult.data.success_rate }}%</span>
                        </div>
                        <div v-if="uploadResult.data?.override_enabled !== undefined" class="flex justify-between">
                            <span class="text-sm font-medium">Override Mode:</span>
                            <Tag 
                                :value="uploadResult.data.override_enabled ? 'Enabled' : 'Disabled'"
                                :severity="uploadResult.data.override_enabled ? 'warning' : 'info'"
                                class="text-xs"
                            />
                        </div>
                    </div>
                </template>
            </Card>
            
            <!-- Upload History -->
            <Card v-if="showHistory">
                <template #title>
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-history text-secondary"></i>
                            <span>Recent Uploads</span>
                        </div>
                        <Button 
                            @click="refreshHistory"
                            icon="pi pi-refresh"
                            size="small"
                            text
                        />
                    </div>
                </template>
                <template #content>
                    <div v-if="loadingHistory" class="text-center py-4">
                        <ProgressSpinner style="width: 30px; height: 30px" />
                    </div>
                    <div v-else-if="uploadHistory.length === 0" class="text-center py-4 text-gray-500 text-sm">
                        No recent uploads
                    </div>
                    <div v-else class="space-y-2 max-h-60 overflow-y-auto">
                        <div 
                            v-for="upload in uploadHistory" 
                            :key="upload.id"
                            class="p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                        >
                            <div class="flex justify-between items-start">
                                <div class="flex-1 min-w-0">
                                    <div class="text-sm font-medium text-gray-900 truncate">
                                        {{ upload.file_name }}
                                    </div>
                                    <div class="text-xs text-gray-500 mt-1">
                                        {{ formatDate(upload.upload_date) }}
                                    </div>
                                </div>
                                <Tag 
                                    :value="upload.upload_status"
                                    :severity="getStatusSeverity(upload.upload_status)"
                                    class="ml-2"
                                />
                            </div>
                            <div class="text-xs text-gray-600 mt-2">
                                {{ upload.successful_records }}/{{ upload.total_records }} records
                            </div>
                        </div>
                    </div>
                </template>
            </Card>
        </div>
    </Sidebar>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import Sidebar from 'primevue/sidebar';
import Card from 'primevue/card';
import Button from 'primevue/button';
import FileUpload from 'primevue/fileupload';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';
import Checkbox from 'primevue/checkbox';
import CustomerService from '@/service/CustomerService';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['update:visible', 'upload-success']);

const toast = useToast();

// Upload state
const selectedFile = ref(null);
const uploading = ref(false);
const uploadResult = ref(null);
const overrideExisting = ref(false);
const reformatDates = ref(false);

// History state
const showHistory = ref(true);
const loadingHistory = ref(false);
const uploadHistory = ref([]);

// File selection
const onFileSelect = (event) => {
    selectedFile.value = event.files[0];
    uploadResult.value = null;
    // Reset override option when new file is selected
    // overrideExisting.value = false; // Uncomment if you want to reset on file change
};

// File upload
const uploadFile = async () => {
    if (!selectedFile.value) {
        toast.add({
            severity: 'warn',
            summary: 'Warning',
            detail: 'Please select a file first',
            life: 3000
        });
        return;
    }
    
    uploading.value = true;
    uploadResult.value = null;
    
    try {
        const result = await CustomerService.uploadCustomerSatisfactionFile(
            selectedFile.value, 
            overrideExisting.value,
            reformatDates.value
        );
        
        if (result.success) {
            uploadResult.value = result;
            toast.add({
                severity: 'success',
                summary: 'Success',
                detail: result.message,
                life: 5000
            });
            
            // Refresh history and emit success event
            await refreshHistory();
            emit('upload-success');
            
            // Clear selected file
            selectedFile.value = null;
        } else {
            toast.add({
                severity: 'error',
                summary: 'Upload Failed',
                detail: result.message,
                life: 5000
            });
        }
    } catch (error) {
        console.error('Upload error:', error);
        toast.add({
            severity: 'error',
            summary: 'Upload Error',
            detail: error.response?.data?.detail || 'An error occurred during upload',
            life: 5000
        });
    } finally {
        uploading.value = false;
    }
};

// Upload history
const refreshHistory = async () => {
    loadingHistory.value = true;
    try {
        const result = await CustomerService.getCustomerSatisfactionUploadTrackers({
            page: 1,
            page_size: 5
        });
        
        if (result.success) {
            uploadHistory.value = result.data?.trackers || [];
        }
    } catch (error) {
        console.error('Error fetching upload history:', error);
    } finally {
        loadingHistory.value = false;
    }
};

// Utilities
const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('id-ID', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return 'Invalid Date';
    }
};

const getStatusSeverity = (status) => {
    switch (status) {
        case 'COMPLETED':
            return 'success';
        case 'FAILED':
            return 'danger';
        case 'PROCESSING':
            return 'info';
        default:
            return 'secondary';
    }
};

// Watch visibility to load history when sidebar opens
watch(() => props.visible, (newVisible) => {
    if (newVisible && showHistory.value) {
        refreshHistory();
    }
});

// Load history on mount
onMounted(() => {
    if (props.visible && showHistory.value) {
        refreshHistory();
    }
});
</script>

<style scoped>
.p-sidebar {
    background: var(--p-surface-0);
}
</style>