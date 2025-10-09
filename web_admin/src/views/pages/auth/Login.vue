<script setup>
import FloatingConfigurator from '@/components/FloatingConfigurator.vue';
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const toast = useToast();
const authStore = useAuthStore();

const loading = ref(false);
const form = reactive({
    email: '',
    password: ''
});

const errors = reactive({
    email: '',
    password: '',
    general: ''
});

const clearErrors = () => {
    errors.email = '';
    errors.password = '';
    errors.general = '';
};

const validateForm = () => {
    clearErrors();
    let isValid = true;

    if (!form.email) {
        errors.email = 'Email is required';
        isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(form.email)) {
        errors.email = 'Email is invalid';
        isValid = false;
    }

    if (!form.password) {
        errors.password = 'Password is required';
        isValid = false;
    }

    return isValid;
};

const handleLogin = async () => {
    if (!validateForm()) {
        return;
    }

    loading.value = true;
    clearErrors();

    try {
        const result = await authStore.login({
            email: form.email,
            password: form.password
        });

        if (result.success) {
            toast.add({
                severity: 'success',
                summary: 'Success',
                detail: 'Login successful',
                life: 3000
            });
            router.push('/');
        } else {
            errors.general = result.message || 'Login failed';
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: result.message || 'Login failed',
                life: 5000
            });
        }
    } catch (error) {
        console.error('Login error:', error);
        errors.general = 'An unexpected error occurred';
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'An unexpected error occurred',
            life: 5000
        });
    } finally {
        loading.value = false;
    }
};

// Check if user is already authenticated
onMounted(() => {
    authStore.checkAuth();
    if (authStore.isAuthenticated) {
        console.log('User already authenticated, redirecting to dashboard');
        router.push('/');
    }
});
</script>

<template>
    <FloatingConfigurator />
    <div class="login-container">
        <!-- Left Panel - Branding -->
        <div class="brand-panel">
            <div class="brand-content">
                <div class="logo-wrapper">
                    <img src="/assets/images/logo-transparent.png" alt="Logo" class="brand-logo" />
                </div>
                <h1 class="brand-title">Dealer Admin</h1>
                <p class="brand-subtitle"></p>
            </div>
            <div class="brand-overlay"></div>
        </div>

        <!-- Right Panel - Login Form -->
        <div class="form-panel">
            <div class="form-wrapper">
                <div class="form-header">
                    <h2 class="form-title">Welcome back</h2>
                    <p class="form-subtitle">Sign in to your account to continue</p>
                </div>

                <form @submit.prevent="handleLogin" class="login-form">
                    <!-- Email Field -->
                    <div class="form-field">
                        <label for="email1" class="field-label">Email</label>
                        <InputText
                            id="email1"
                            type="email"
                            placeholder="Enter your email"
                            class="field-input"
                            v-model="form.email"
                            :class="{ 'p-invalid': errors.email }"
                            required
                        />
                        <small v-if="errors.email" class="error-message">{{ errors.email }}</small>
                    </div>

                    <!-- Password Field -->
                    <div class="form-field">
                        <label for="password1" class="field-label">Password</label>
                        <Password
                            id="password1"
                            v-model="form.password"
                            placeholder="Enter your password"
                            :toggleMask="true"
                            class="password-field"
                            fluid
                            :feedback="false"
                            :class="{ 'p-invalid': errors.password }"
                            required
                        />
                        <small v-if="errors.password" class="error-message">{{ errors.password }}</small>
                    </div>

                    <!-- General Error -->
                    <div v-if="errors.general" class="general-error">
                        <i class="pi pi-exclamation-circle"></i>
                        <span>{{ errors.general }}</span>
                    </div>

                    <!-- Submit Button -->
                    <Button
                        type="submit"
                        label="Sign In"
                        class="submit-button"
                        :loading="loading"
                        :disabled="loading"
                    />
                </form>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Container Layout */
.login-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    min-height: 100vh;
    overflow: hidden;
}

/* Left Panel - Branding */
.brand-panel {
    position: relative;
    background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 50%, var(--primary-800) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    overflow: hidden;
}

.brand-overlay {
    position: absolute;
    inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    opacity: 0.4;
}

.brand-content {
    position: relative;
    z-index: 1;
    text-align: center;
    color: white;
}

.logo-wrapper {
    margin-bottom: 2rem;
}

.brand-logo {
    width: 180px;
    height: auto;
    filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.2));
}

.brand-title {
    font-size: 3rem;
    font-weight: 700;
    margin: 0 0 1rem 0;
    letter-spacing: -0.02em;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.brand-subtitle {
    font-size: 1.125rem;
    font-weight: 400;
    opacity: 0.95;
    margin: 0;
}

/* Right Panel - Form */
.form-panel {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    background: var(--surface-0);
}

.form-wrapper {
    width: 100%;
    max-width: 420px;
}

.form-header {
    margin-bottom: 2.5rem;
}

.form-title {
    font-size: 2rem;
    font-weight: 600;
    color: var(--surface-900);
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.01em;
}

.form-subtitle {
    font-size: 0.9375rem;
    color: var(--surface-600);
    margin: 0;
    font-weight: 400;
}

/* Form Fields */
.login-form {
    display: flex;
    flex-direction: column;
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
    letter-spacing: 0.01em;
}

.field-input :deep(.p-inputtext) {
    padding: 0.875rem 1rem;
    font-size: 0.9375rem;
    border-radius: 8px;
    border: 1.5px solid var(--surface-300);
    transition: all 0.2s ease;
    background: var(--surface-0);
}

.field-input :deep(.p-inputtext:hover) {
    border-color: var(--surface-400);
}

.field-input :deep(.p-inputtext:focus) {
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px rgba(var(--primary-500-rgb), 0.1);
    outline: none;
}

.password-field :deep(.p-password-overlay) {
    border-radius: 8px;
}

.error-message {
    color: var(--red-600);
    font-size: 0.8125rem;
    margin-top: 0.25rem;
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.error-message::before {
    content: '⚠';
    font-size: 0.75rem;
}

/* General Error */
.general-error {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.875rem 1rem;
    background: rgba(var(--red-500-rgb), 0.1);
    border: 1px solid var(--red-300);
    border-radius: 8px;
    color: var(--red-700);
    font-size: 0.875rem;
    margin-top: -0.5rem;
}

.general-error i {
    font-size: 1.125rem;
    color: var(--red-600);
}

/* Submit Button */
.submit-button {
    margin-top: 0.5rem;
    padding: 0.875rem 1.5rem;
    font-size: 0.9375rem;
    font-weight: 600;
    border-radius: 8px;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.submit-button:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.submit-button:active:not(:disabled) {
    transform: translateY(0);
}

/* Invalid State */
.p-invalid :deep(.p-inputtext) {
    border-color: var(--red-500);
}

.p-invalid :deep(.p-inputtext:focus) {
    box-shadow: 0 0 0 3px rgba(var(--red-500-rgb), 0.1);
}

/* Dark Mode */
@media (prefers-color-scheme: dark) {
    .form-panel {
        background: var(--surface-900);
    }

    .form-title {
        color: var(--surface-0);
    }

    .form-subtitle {
        color: var(--surface-400);
    }

    .field-label {
        color: var(--surface-300);
    }

    .field-input :deep(.p-inputtext) {
        background: var(--surface-800);
        border-color: var(--surface-700);
        color: var(--surface-0);
    }

    .field-input :deep(.p-inputtext:hover) {
        border-color: var(--surface-600);
    }
}

/* Responsive Design */
@media (max-width: 1024px) {
    .login-container {
        grid-template-columns: 1fr;
    }

    .brand-panel {
        display: none;
    }

    .form-panel {
        padding: 2rem 1.5rem;
    }

    .form-wrapper {
        max-width: 480px;
    }
}

@media (max-width: 640px) {
    .form-panel {
        padding: 1.5rem 1rem;
    }

    .form-title {
        font-size: 1.75rem;
    }

    .brand-title {
        font-size: 2.5rem;
    }
}
</style>
