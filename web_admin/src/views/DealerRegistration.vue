<script setup>
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import Steps from 'primevue/steps';
import Card from 'primevue/card';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import FileUpload from 'primevue/fileupload';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import DealerService from '@/service/DealerService';

const router = useRouter();
const toast = useToast();

// Registration mode: 'single' or 'bulk'
const registrationMode = ref('single');

// Current step (for single registration)
const activeStep = ref(0);
const loading = ref(false);

// Bulk import state
const uploadedFile = ref(null);
const uploadLoading = ref(false);
const uploadResults = ref(null);

// Steps configuration
const steps = ref([
    { label: 'Dealer Info' },
    { label: 'API Config' },
    { label: 'WhatsApp' },
    { label: 'Google Maps' },
    { label: 'Admin User' },
    { label: 'Confirmation' }
]);

// Form data
const formData = reactive({
    // Step 1: Dealer Info
    dealer_id: '',
    dealer_name: '',
    // Step 2: API Config
    api_key: '',
    secret_key: '',
    // Step 3: WhatsApp
    fonnte_api_key: '',
    fonnte_api_url: 'https://api.fonnte.com/send',
    phone_number: '',
    // Step 4: Google Maps
    google_location_url: '',
    // Step 5: Admin User
    admin_email: '',
    admin_full_name: '',
    admin_password: '',
    admin_password_confirm: ''
});

// Validation errors
const errors = reactive({
    dealer_id: '',
    dealer_name: '',
    api_key: '',
    secret_key: '',
    fonnte_api_key: '',
    phone_number: '',
    google_location_url: '',
    admin_email: '',
    admin_full_name: '',
    admin_password: '',
    admin_password_confirm: ''
});

// Clear all errors
const clearErrors = () => {
    Object.keys(errors).forEach(key => {
        errors[key] = '';
    });
};

// Validate Step 1: Dealer Info
const validateStep1 = () => {
    clearErrors();
    let isValid = true;

    if (!formData.dealer_id) {
        errors.dealer_id = 'Dealer ID is required';
        isValid = false;
    } else if (!/^[A-Z0-9]{1,10}$/.test(formData.dealer_id)) {
        errors.dealer_id = 'Dealer ID must be 1-10 uppercase letters or numbers';
        isValid = false;
    }

    if (!formData.dealer_name) {
        errors.dealer_name = 'Dealer name is required';
        isValid = false;
    }

    return isValid;
};

// Validate Step 2: API Config (optional fields, but validate format if provided)
const validateStep2 = () => {
    clearErrors();
    let isValid = true;

    // API Key and Secret Key are optional but if one is provided, both should be
    if (formData.api_key && !formData.secret_key) {
        errors.secret_key = 'Secret key is required when API key is provided';
        isValid = false;
    }

    if (formData.secret_key && !formData.api_key) {
        errors.api_key = 'API key is required when secret key is provided';
        isValid = false;
    }

    return isValid;
};

// Validate Step 3: WhatsApp Config (optional)
const validateStep3 = () => {
    clearErrors();
    let isValid = true;

    // Phone number format validation if provided
    if (formData.phone_number && !/^[0-9]{10,15}$/.test(formData.phone_number)) {
        errors.phone_number = 'Phone number must be 10-15 digits (e.g., 628123456789)';
        isValid = false;
    }

    return isValid;
};

// Validate Step 4: Google Maps (optional)
const validateStep4 = () => {
    clearErrors();
    return true; // All fields are optional
};

// Validate Step 5: Admin User
const validateStep5 = () => {
    clearErrors();
    let isValid = true;

    if (!formData.admin_email) {
        errors.admin_email = 'Email is required';
        isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(formData.admin_email)) {
        errors.admin_email = 'Email is invalid';
        isValid = false;
    }

    if (!formData.admin_full_name) {
        errors.admin_full_name = 'Full name is required';
        isValid = false;
    }

    if (!formData.admin_password) {
        errors.admin_password = 'Password is required';
        isValid = false;
    } else if (formData.admin_password.length < 8) {
        errors.admin_password = 'Password must be at least 8 characters';
        isValid = false;
    } else {
        // Password strength validation
        const hasUpper = /[A-Z]/.test(formData.admin_password);
        const hasLower = /[a-z]/.test(formData.admin_password);
        const hasDigit = /[0-9]/.test(formData.admin_password);

        if (!hasUpper || !hasLower || !hasDigit) {
            errors.admin_password = 'Password must contain uppercase, lowercase, and digit';
            isValid = false;
        }
    }

    if (!formData.admin_password_confirm) {
        errors.admin_password_confirm = 'Please confirm password';
        isValid = false;
    } else if (formData.admin_password !== formData.admin_password_confirm) {
        errors.admin_password_confirm = 'Passwords do not match';
        isValid = false;
    }

    return isValid;
};

// Validate current step
const validateCurrentStep = () => {
    switch (activeStep.value) {
        case 0:
            return validateStep1();
        case 1:
            return validateStep2();
        case 2:
            return validateStep3();
        case 3:
            return validateStep4();
        case 4:
            return validateStep5();
        case 5:
            return true; // Confirmation step, no validation
        default:
            return false;
    }
};

// Navigation
const nextStep = () => {
    if (validateCurrentStep()) {
        if (activeStep.value < steps.value.length - 1) {
            activeStep.value++;
        }
    }
};

const previousStep = () => {
    if (activeStep.value > 0) {
        activeStep.value--;
    }
};

// Check if current step is valid for Next button
const isCurrentStepValid = computed(() => {
    switch (activeStep.value) {
        case 0:
            return formData.dealer_id && formData.dealer_name;
        case 1:
            return true; // Optional step
        case 2:
            return true; // Optional step
        case 3:
            return true; // Optional step
        case 4:
            return formData.admin_email && formData.admin_full_name &&
                   formData.admin_password && formData.admin_password_confirm;
        case 5:
            return true;
        default:
            return false;
    }
});

// Submit registration
const submitRegistration = async () => {
    if (!validateStep5()) {
        activeStep.value = 4; // Go back to admin user step
        return;
    }

    loading.value = true;

    try {
        const registrationData = {
            dealer_id: formData.dealer_id,
            dealer_name: formData.dealer_name,
            api_key: formData.api_key || null,
            secret_key: formData.secret_key || null,
            fonnte_api_key: formData.fonnte_api_key || null,
            fonnte_api_url: formData.fonnte_api_url || 'https://api.fonnte.com/send',
            phone_number: formData.phone_number || null,
            google_location_url: formData.google_location_url || null,
            admin_email: formData.admin_email,
            admin_full_name: formData.admin_full_name,
            admin_password: formData.admin_password
        };

        const result = await DealerService.registerDealer(registrationData);

        if (result.success) {
            toast.add({
                severity: 'success',
                summary: 'Success',
                detail: result.message || 'Dealer registered successfully',
                life: 5000
            });

            // Redirect to dealer management page
            setTimeout(() => {
                router.push('/dealer-management');
            }, 2000);
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: result.message || 'Failed to register dealer',
                life: 5000
            });
        }
    } catch (error) {
        console.error('Registration error:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'An unexpected error occurred',
            life: 5000
        });
    } finally {
        loading.value = false;
    }
};

// Cancel and go back
const cancelRegistration = () => {
    router.push('/dealer-management');
};

// Switch registration mode
const switchMode = (mode) => {
    registrationMode.value = mode;
    // Reset states when switching
    if (mode === 'single') {
        uploadedFile.value = null;
        uploadResults.value = null;
    } else {
        activeStep.value = 0;
    }
};

// Handle file selection
const handleFileSelect = (event) => {
    const file = event.files[0];
    if (!file) return;

    // Validate file type
    const allowedExtensions = ['.xlsx', '.xls', '.csv'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!allowedExtensions.includes(fileExtension)) {
        toast.add({
            severity: 'error',
            summary: 'Invalid File',
            detail: 'Please upload an Excel (.xlsx, .xls) or CSV (.csv) file',
            life: 5000
        });
        return;
    }

    // Validate file size (10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        toast.add({
            severity: 'error',
            summary: 'File Too Large',
            detail: 'File size must not exceed 10MB',
            life: 5000
        });
        return;
    }

    uploadedFile.value = file;
};

// Upload bulk file
const uploadBulkFile = async () => {
    if (!uploadedFile.value) {
        toast.add({
            severity: 'warn',
            summary: 'No File Selected',
            detail: 'Please select an Excel file to upload',
            life: 5000
        });
        return;
    }

    uploadLoading.value = true;
    uploadResults.value = null;

    try {
        const result = await DealerService.bulkRegisterDealers(uploadedFile.value);

        uploadResults.value = result;

        if (result.success) {
            toast.add({
                severity: 'success',
                summary: 'Upload Complete',
                detail: `${result.total_success}/${result.total_processed} dealers registered successfully`,
                life: 5000
            });
        } else {
            toast.add({
                severity: 'warn',
                summary: 'Upload Complete with Errors',
                detail: `${result.total_success} succeeded, ${result.total_failed} failed`,
                life: 5000
            });
        }
    } catch (error) {
        console.error('Bulk upload error:', error);
        toast.add({
            severity: 'error',
            summary: 'Upload Failed',
            detail: error.response?.data?.detail || 'Failed to upload file',
            life: 5000
        });
    } finally {
        uploadLoading.value = false;
    }
};

// Download Excel template
const downloadTemplate = () => {
    // Create template data
    const templateData = [
        {
            dealer_id: 'DLR001',
            dealer_name: 'Example Dealer',
            api_key: 'your_api_key',
            secret_key: 'your_secret_key',
            fonnte_api_key: 'your_fonnte_key',
            fonnte_api_url: 'https://api.fonnte.com/send',
            phone_number: '628123456789',
            google_location_url: 'https://maps.google.com/...',
            admin_email: 'admin@example.com',
            admin_full_name: 'John Doe',
            admin_password: 'Password123'
        }
    ];

    // Convert to CSV format (easier than generating Excel)
    const headers = Object.keys(templateData[0]);
    const csv = [
        headers.join(','),
        templateData.map(row => headers.map(h => row[h]).join(',')).join('\n')
    ].join('\n');

    // Create download link
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'dealer_registration_template.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

// Clear upload results
const clearResults = () => {
    uploadedFile.value = null;
    uploadResults.value = null;
};

// Get status severity for Tag component
const getStatusSeverity = (success) => {
    return success ? 'success' : 'danger';
};
</script>

<template>
    <div class="registration-container">
        <!-- Header -->
        <div class="registration-header">
            <h1 class="header-title">Register New Dealer</h1>
            <p class="header-subtitle">Complete all steps to register a new dealer and create an admin user</p>
        </div>

        <!-- Mode Toggle -->
        <Card class="mode-toggle-card">
            <template #content>
                <div class="mode-toggle">
                    <Button
                        :label="'Single Registration'"
                        :severity="registrationMode === 'single' ? 'primary' : 'secondary'"
                        @click="switchMode('single')"
                        icon="pi pi-user"
                    />
                    <Button
                        :label="'Bulk Import'"
                        :severity="registrationMode === 'bulk' ? 'primary' : 'secondary'"
                        @click="switchMode('bulk')"
                        icon="pi pi-upload"
                    />
                </div>
            </template>
        </Card>

        <!-- Single Registration Mode -->
        <div v-if="registrationMode === 'single'">
            <!-- Steps -->
        <Card class="steps-card">
            <template #content>
                <Steps :model="steps" :activeStep="activeStep" class="custom-steps" />
            </template>
        </Card>

        <!-- Step Content -->
        <Card class="content-card">
            <template #content>
                <!-- Step 1: Dealer Info -->
                <div v-if="activeStep === 0" class="step-content">
                    <h2 class="step-title">Dealer Information</h2>
                    <p class="step-description">Enter the basic information for the new dealer</p>

                    <div class="form-grid">
                        <div class="form-field">
                            <label for="dealer-id" class="field-label">Dealer ID *</label>
                            <InputText
                                id="dealer-id"
                                v-model="formData.dealer_id"
                                placeholder="e.g., DLR001"
                                class="w-full"
                                :class="{ 'p-invalid': errors.dealer_id }"
                            />
                            <small v-if="errors.dealer_id" class="error-message">{{ errors.dealer_id }}</small>
                            <small v-else class="hint-text">Unique identifier (1-10 uppercase letters or numbers)</small>
                        </div>

                        <div class="form-field">
                            <label for="dealer-name" class="field-label">Dealer Name *</label>
                            <InputText
                                id="dealer-name"
                                v-model="formData.dealer_name"
                                placeholder="e.g., ABC Motors"
                                class="w-full"
                                :class="{ 'p-invalid': errors.dealer_name }"
                            />
                            <small v-if="errors.dealer_name" class="error-message">{{ errors.dealer_name }}</small>
                            <small v-else class="hint-text">Official dealer name</small>
                        </div>
                    </div>
                </div>

                <!-- Step 2: API Config -->
                <div v-if="activeStep === 1" class="step-content">
                    <h2 class="step-title">DGI API Configuration</h2>
                    <p class="step-description">Configure dealer integration API credentials (optional)</p>

                    <div class="form-grid">
                        <div class="form-field">
                            <label for="api-key" class="field-label">API Key</label>
                            <Password
                                id="api-key"
                                v-model="formData.api_key"
                                placeholder="Enter API key"
                                class="w-full"
                                :feedback="false"
                                toggleMask
                                :class="{ 'p-invalid': errors.api_key }"
                            />
                            <small v-if="errors.api_key" class="error-message">{{ errors.api_key }}</small>
                            <small v-else class="hint-text">DGI API authentication key</small>
                        </div>

                        <div class="form-field">
                            <label for="secret-key" class="field-label">Secret Key</label>
                            <Password
                                id="secret-key"
                                v-model="formData.secret_key"
                                placeholder="Enter secret key"
                                class="w-full"
                                :feedback="false"
                                toggleMask
                                :class="{ 'p-invalid': errors.secret_key }"
                            />
                            <small v-if="errors.secret_key" class="error-message">{{ errors.secret_key }}</small>
                            <small v-else class="hint-text">DGI API secret key for encryption</small>
                        </div>
                    </div>
                </div>

                <!-- Step 3: WhatsApp Config -->
                <div v-if="activeStep === 2" class="step-content">
                    <h2 class="step-title">WhatsApp Configuration</h2>
                    <p class="step-description">Configure WhatsApp messaging integration (optional)</p>

                    <div class="form-grid">
                        <div class="form-field">
                            <label for="phone-number" class="field-label">Phone Number</label>
                            <InputText
                                id="phone-number"
                                v-model="formData.phone_number"
                                placeholder="e.g., 628123456789"
                                class="w-full"
                                :class="{ 'p-invalid': errors.phone_number }"
                            />
                            <small v-if="errors.phone_number" class="error-message">{{ errors.phone_number }}</small>
                            <small v-else class="hint-text">WhatsApp business number with country code</small>
                        </div>

                        <div class="form-field">
                            <label for="fonnte-api-key" class="field-label">Fonnte API Key</label>
                            <Password
                                id="fonnte-api-key"
                                v-model="formData.fonnte_api_key"
                                placeholder="Enter Fonnte API key"
                                class="w-full"
                                :feedback="false"
                                toggleMask
                            />
                            <small class="hint-text">Fonnte WhatsApp API key</small>
                        </div>

                        <div class="form-field">
                            <label for="fonnte-api-url" class="field-label">Fonnte API URL</label>
                            <InputText
                                id="fonnte-api-url"
                                v-model="formData.fonnte_api_url"
                                placeholder="https://api.fonnte.com/send"
                                class="w-full"
                            />
                            <small class="hint-text">Default: https://api.fonnte.com/send</small>
                        </div>
                    </div>
                </div>

                <!-- Step 4: Google Maps -->
                <div v-if="activeStep === 3" class="step-content">
                    <h2 class="step-title">Google Maps Configuration</h2>
                    <p class="step-description">Configure Google Maps location (optional)</p>

                    <div class="form-grid">
                        <div class="form-field">
                            <label for="google-location" class="field-label">Google Location URL</label>
                            <InputText
                                id="google-location"
                                v-model="formData.google_location_url"
                                placeholder="https://maps.google.com/..."
                                class="w-full"
                            />
                            <small class="hint-text">Google Maps location URL for review scraping</small>
                        </div>
                    </div>
                </div>

                <!-- Step 5: Admin User -->
                <div v-if="activeStep === 4" class="step-content">
                    <h2 class="step-title">Admin User Account</h2>
                    <p class="step-description">Create a dealer admin user account</p>

                    <div class="form-grid">
                        <div class="form-field">
                            <label for="admin-email" class="field-label">Email *</label>
                            <InputText
                                id="admin-email"
                                v-model="formData.admin_email"
                                type="email"
                                placeholder="admin@example.com"
                                class="w-full"
                                :class="{ 'p-invalid': errors.admin_email }"
                            />
                            <small v-if="errors.admin_email" class="error-message">{{ errors.admin_email }}</small>
                            <small v-else class="hint-text">Admin user email address</small>
                        </div>

                        <div class="form-field">
                            <label for="admin-full-name" class="field-label">Full Name *</label>
                            <InputText
                                id="admin-full-name"
                                v-model="formData.admin_full_name"
                                placeholder="John Doe"
                                class="w-full"
                                :class="{ 'p-invalid': errors.admin_full_name }"
                            />
                            <small v-if="errors.admin_full_name" class="error-message">{{ errors.admin_full_name }}</small>
                            <small v-else class="hint-text">Admin user full name</small>
                        </div>

                        <div class="form-field">
                            <label for="admin-password" class="field-label">Password *</label>
                            <Password
                                id="admin-password"
                                v-model="formData.admin_password"
                                placeholder="Enter password"
                                class="w-full"
                                toggleMask
                                :class="{ 'p-invalid': errors.admin_password }"
                            />
                            <small v-if="errors.admin_password" class="error-message">{{ errors.admin_password }}</small>
                            <small v-else class="hint-text">Min 8 characters with uppercase, lowercase, and digit</small>
                        </div>

                        <div class="form-field">
                            <label for="admin-password-confirm" class="field-label">Confirm Password *</label>
                            <Password
                                id="admin-password-confirm"
                                v-model="formData.admin_password_confirm"
                                placeholder="Confirm password"
                                class="w-full"
                                toggleMask
                                :feedback="false"
                                :class="{ 'p-invalid': errors.admin_password_confirm }"
                            />
                            <small v-if="errors.admin_password_confirm" class="error-message">{{ errors.admin_password_confirm }}</small>
                        </div>
                    </div>
                </div>

                <!-- Step 6: Confirmation -->
                <div v-if="activeStep === 5" class="step-content">
                    <h2 class="step-title">Review & Confirm</h2>
                    <p class="step-description">Please review the information before submitting</p>

                    <div class="confirmation-grid">
                        <!-- Dealer Info -->
                        <Card class="confirmation-section">
                            <template #title>
                                <div class="section-header">
                                    <i class="pi pi-building"></i>
                                    <span>Dealer Information</span>
                                </div>
                            </template>
                            <template #content>
                                <div class="info-row">
                                    <span class="info-label">Dealer ID:</span>
                                    <span class="info-value">{{ formData.dealer_id }}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Dealer Name:</span>
                                    <span class="info-value">{{ formData.dealer_name }}</span>
                                </div>
                            </template>
                        </Card>

                        <!-- API Config -->
                        <Card class="confirmation-section">
                            <template #title>
                                <div class="section-header">
                                    <i class="pi pi-key"></i>
                                    <span>API Configuration</span>
                                </div>
                            </template>
                            <template #content>
                                <div class="info-row">
                                    <span class="info-label">API Key:</span>
                                    <span class="info-value">{{ formData.api_key ? '••••••••' : 'Not configured' }}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Secret Key:</span>
                                    <span class="info-value">{{ formData.secret_key ? '••••••••' : 'Not configured' }}</span>
                                </div>
                            </template>
                        </Card>

                        <!-- WhatsApp Config -->
                        <Card class="confirmation-section">
                            <template #title>
                                <div class="section-header">
                                    <i class="pi pi-whatsapp"></i>
                                    <span>WhatsApp Configuration</span>
                                </div>
                            </template>
                            <template #content>
                                <div class="info-row">
                                    <span class="info-label">Phone Number:</span>
                                    <span class="info-value">{{ formData.phone_number || 'Not configured' }}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Fonnte API:</span>
                                    <span class="info-value">{{ formData.fonnte_api_key ? 'Configured' : 'Not configured' }}</span>
                                </div>
                            </template>
                        </Card>

                        <!-- Google Maps -->
                        <Card class="confirmation-section">
                            <template #title>
                                <div class="section-header">
                                    <i class="pi pi-map-marker"></i>
                                    <span>Google Maps</span>
                                </div>
                            </template>
                            <template #content>
                                <div class="info-row">
                                    <span class="info-label">Location URL:</span>
                                    <span class="info-value">{{ formData.google_location_url || 'Not configured' }}</span>
                                </div>
                            </template>
                        </Card>

                        <!-- Admin User -->
                        <Card class="confirmation-section">
                            <template #title>
                                <div class="section-header">
                                    <i class="pi pi-user"></i>
                                    <span>Admin User</span>
                                </div>
                            </template>
                            <template #content>
                                <div class="info-row">
                                    <span class="info-label">Email:</span>
                                    <span class="info-value">{{ formData.admin_email }}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Full Name:</span>
                                    <span class="info-value">{{ formData.admin_full_name }}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Role:</span>
                                    <span class="info-value">DEALER_ADMIN</span>
                                </div>
                            </template>
                        </Card>
                    </div>
                </div>
            </template>
        </Card>

        <!-- Navigation Buttons -->
        <Card class="navigation-card">
            <template #content>
                <div class="navigation-buttons">
                    <Button
                        label="Cancel"
                        icon="pi pi-times"
                        severity="secondary"
                        @click="cancelRegistration"
                        :disabled="loading"
                    />

                    <div class="right-buttons">
                        <Button
                            v-if="activeStep > 0"
                            label="Previous"
                            icon="pi pi-arrow-left"
                            severity="secondary"
                            @click="previousStep"
                            :disabled="loading"
                        />

                        <Button
                            v-if="activeStep < steps.length - 1"
                            label="Next"
                            icon="pi pi-arrow-right"
                            iconPos="right"
                            @click="nextStep"
                            :disabled="!isCurrentStepValid || loading"
                        />

                        <Button
                            v-if="activeStep === steps.length - 1"
                            label="Register Dealer"
                            icon="pi pi-check"
                            @click="submitRegistration"
                            :loading="loading"
                            :disabled="loading"
                        />
                    </div>
                </div>
            </template>
        </Card>
        </div>

        <!-- Bulk Import Mode -->
        <div v-if="registrationMode === 'bulk'">
            <!-- Upload Section -->
            <Card class="upload-card">
                <template #title>
                    <div class="section-header">
                        <i class="pi pi-cloud-upload"></i>
                        <span>Bulk Dealer Registration</span>
                    </div>
                </template>
                <template #content>
                    <div class="upload-section">
                        <div class="upload-instructions">
                            <h3>Instructions:</h3>
                            <ol>
                                <li>Download the CSV template file</li>
                                <li>Fill in dealer information (one row per dealer)</li>
                                <li>Save the file (CSV is recommended, Excel also supported)</li>
                                <li>Upload the file below</li>
                            </ol>

                            <h4>Required Columns:</h4>
                            <ul>
                                <li><strong>dealer_id</strong> - Unique dealer ID (1-10 characters)</li>
                                <li><strong>dealer_name</strong> - Dealer name</li>
                                <li><strong>admin_email</strong> - Admin user email</li>
                                <li><strong>admin_full_name</strong> - Admin user full name</li>
                                <li><strong>admin_password</strong> - Admin user password (min 8 chars)</li>
                            </ul>

                            <h4>Optional Columns:</h4>
                            <p>api_key, secret_key, fonnte_api_key, fonnte_api_url, phone_number, google_location_url</p>

                            <Button
                                label="Download CSV Template"
                                icon="pi pi-download"
                                severity="secondary"
                                @click="downloadTemplate"
                                class="download-btn"
                            />
                        </div>

                        <div class="upload-area">
                            <FileUpload
                                mode="basic"
                                name="file"
                                accept=".xlsx,.xls,.csv"
                                :maxFileSize="10000000"
                                @select="handleFileSelect"
                                :auto="false"
                                chooseLabel="Choose File (Excel or CSV)"
                                class="custom-upload"
                            />

                            <div v-if="uploadedFile" class="selected-file">
                                <i class="pi pi-file-excel"></i>
                                <span>{{ uploadedFile.name }}</span>
                                <span class="file-size">({{ (uploadedFile.size / 1024).toFixed(2) }} KB)</span>
                            </div>

                            <Button
                                label="Upload & Register Dealers"
                                icon="pi pi-upload"
                                @click="uploadBulkFile"
                                :loading="uploadLoading"
                                :disabled="!uploadedFile || uploadLoading"
                                class="upload-btn"
                            />
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Results Section -->
            <Card v-if="uploadResults" class="results-card">
                <template #title>
                    <div class="results-header">
                        <div class="section-header">
                            <i class="pi pi-list"></i>
                            <span>Registration Results</span>
                        </div>
                        <Button
                            label="Clear Results"
                            icon="pi pi-times"
                            severity="secondary"
                            size="small"
                            @click="clearResults"
                        />
                    </div>
                </template>
                <template #content>
                    <!-- Summary -->
                    <div class="results-summary">
                        <div class="summary-item">
                            <span class="summary-label">Total Processed:</span>
                            <span class="summary-value">{{ uploadResults.total_processed }}</span>
                        </div>
                        <div class="summary-item success">
                            <span class="summary-label">Succeeded:</span>
                            <span class="summary-value">{{ uploadResults.total_success }}</span>
                        </div>
                        <div class="summary-item error">
                            <span class="summary-label">Failed:</span>
                            <span class="summary-value">{{ uploadResults.total_failed }}</span>
                        </div>
                    </div>

                    <!-- Detailed Results Table -->
                    <DataTable :value="uploadResults.results" class="results-table" stripedRows>
                        <Column field="dealer_id" header="Dealer ID" style="width: 15%"></Column>
                        <Column header="Status" style="width: 15%">
                            <template #body="slotProps">
                                <Tag
                                    :value="slotProps.data.success ? 'Success' : 'Failed'"
                                    :severity="getStatusSeverity(slotProps.data.success)"
                                />
                            </template>
                        </Column>
                        <Column field="message" header="Message" style="width: 40%"></Column>
                        <Column header="Dealer Name" style="width: 30%">
                            <template #body="slotProps">
                                <span v-if="slotProps.data.dealer">{{ slotProps.data.dealer.dealer_name }}</span>
                                <span v-else class="not-available">N/A</span>
                            </template>
                        </Column>
                    </DataTable>
                </template>
            </Card>

            <!-- Navigation -->
            <Card class="navigation-card">
                <template #content>
                    <div class="navigation-buttons">
                        <Button
                            label="Back to Dealer Management"
                            icon="pi pi-arrow-left"
                            severity="secondary"
                            @click="cancelRegistration"
                        />
                    </div>
                </template>
            </Card>
        </div>
    </div>
</template>

<style scoped>
.registration-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
}

.registration-header {
    margin-bottom: 2rem;
}

.header-title {
    font-size: 2rem;
    font-weight: 600;
    color: var(--surface-900);
    margin: 0 0 0.5rem 0;
}

.header-subtitle {
    font-size: 1rem;
    color: var(--surface-600);
    margin: 0;
}

.mode-toggle-card,
.steps-card,
.content-card,
.navigation-card,
.upload-card,
.results-card {
    margin-bottom: 1.5rem;
}

.mode-toggle {
    display: flex;
    gap: 1rem;
    justify-content: center;
    padding: 0.5rem 0;
}

.mode-toggle .p-button {
    min-width: 180px;
}

.custom-steps {
    padding: 1rem 0;
}

.step-content {
    padding: 1rem 0;
}

.step-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--surface-900);
    margin: 0 0 0.5rem 0;
}

.step-description {
    font-size: 0.9375rem;
    color: var(--surface-600);
    margin: 0 0 2rem 0;
}

.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.form-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.field-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--surface-700);
}

.error-message {
    color: var(--red-600);
    font-size: 0.8125rem;
}

.hint-text {
    color: var(--surface-500);
    font-size: 0.8125rem;
}

.confirmation-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.confirmation-section {
    background: var(--surface-50);
}

.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: var(--primary-500);
    font-size: 1rem;
    font-weight: 600;
}

.section-header i {
    font-size: 1.25rem;
}

.info-row {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--surface-200);
}

.info-row:last-child {
    border-bottom: none;
}

.info-label {
    font-weight: 500;
    color: var(--surface-600);
}

.info-value {
    color: var(--surface-900);
    font-weight: 500;
    word-break: break-all;
}

.navigation-buttons {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
}

.right-buttons {
    display: flex;
    gap: 0.75rem;
}

/* Password field full width */
:deep(.p-password) {
    width: 100%;
}

:deep(.p-password input) {
    width: 100%;
}

/* Bulk Import Styles */
.upload-section {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
}

.upload-instructions h3,
.upload-instructions h4 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--surface-900);
    margin: 1rem 0 0.5rem 0;
}

.upload-instructions h3 {
    margin-top: 0;
}

.upload-instructions ol,
.upload-instructions ul {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
}

.upload-instructions li {
    margin: 0.25rem 0;
    color: var(--surface-700);
}

.upload-instructions p {
    color: var(--surface-600);
    font-size: 0.875rem;
    margin: 0.5rem 0;
}

.download-btn {
    margin-top: 1rem;
}

.upload-area {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
}

.custom-upload {
    width: 100%;
}

.selected-file {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    background: var(--surface-50);
    border: 1px solid var(--surface-200);
    border-radius: 6px;
    color: var(--surface-700);
}

.selected-file i {
    color: var(--green-500);
    font-size: 1.25rem;
}

.file-size {
    color: var(--surface-500);
    font-size: 0.875rem;
    margin-left: auto;
}

.upload-btn {
    width: 100%;
}

.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.results-summary {
    display: flex;
    gap: 2rem;
    padding: 1rem;
    background: var(--surface-50);
    border-radius: 6px;
    margin-bottom: 1.5rem;
}

.summary-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.summary-label {
    font-size: 0.875rem;
    color: var(--surface-600);
}

.summary-value {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--surface-900);
}

.summary-item.success .summary-value {
    color: var(--green-600);
}

.summary-item.error .summary-value {
    color: var(--red-600);
}

.results-table {
    margin-top: 1rem;
}

.not-available {
    color: var(--surface-400);
    font-style: italic;
}

/* Responsive */
@media (max-width: 768px) {
    .registration-container {
        padding: 1rem;
    }

    .form-grid,
    .confirmation-grid {
        grid-template-columns: 1fr;
    }

    .navigation-buttons {
        flex-direction: column;
        gap: 1rem;
    }

    .right-buttons {
        width: 100%;
        flex-direction: column;
    }

    .right-buttons .p-button {
        width: 100%;
    }

    .mode-toggle {
        flex-direction: column;
    }

    .mode-toggle .p-button {
        width: 100%;
    }

    .upload-section {
        grid-template-columns: 1fr;
    }

    .results-summary {
        flex-direction: column;
        gap: 1rem;
    }
}
</style>
