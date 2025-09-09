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
    <div class="flex items-center justify-center min-h-screen min-w-[100vw] overflow-hidden">
        <div class="flex flex-col items-center justify-center">
            <div style="border-radius: 56px; padding: 0.3rem; background: linear-gradient(180deg, var(--primary-color) 10%, rgba(33, 150, 243, 0) 30%)">
                <div class="w-full bg-surface-0 dark:bg-surface-900 py-20 px-8 sm:px-20" style="border-radius: 53px">
                    <div class="text-center mb-8">
                        <img src="/assets/images/logo-transparent.png" alt="Logo" class="mb-8 w-16 shrink-0 mx-auto" />
                        <div class="text-surface-900 dark:text-surface-0 text-3xl font-medium mb-4">Welcome Back!</div>
                        <span class="text-muted-color font-medium">Sign in to continue</span>
                    </div>

                    <div>
                        <form @submit.prevent="handleLogin">
                            <label for="email1" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2">Email</label>
                            <InputText id="email1" type="email" placeholder="Email address" class="w-full md:w-[30rem] mb-2" v-model="form.email" :class="{ 'p-invalid': errors.email }" required />
                            <small v-if="errors.email" class="p-error block mb-6">{{ errors.email }}</small>
                            <div v-else class="mb-6"></div>

                            <label for="password1" class="block text-surface-900 dark:text-surface-0 font-medium text-xl mb-2">Password</label>
                            <Password id="password1" v-model="form.password" placeholder="Password" :toggleMask="true" class="mb-2" fluid :feedback="false" :class="{ 'p-invalid': errors.password }" required />
                            <small v-if="errors.password" class="p-error block mb-4">{{ errors.password }}</small>
                            <div v-else class="mb-4"></div>

                            <div v-if="errors.general" class="mb-4">
                                <small class="p-error">{{ errors.general }}</small>
                            </div>

                            <!-- <div class="flex items-center justify-between mt-2 mb-8 gap-8">
                                - <div class="flex items-center">
                                    <span class="font-medium no-underline ml-2 text-right cursor-pointer text-primary">Forgot password?</span>
                                </div> -
                            </div> -->

                            <Button type="submit" label="Sign In" class="w-full" :loading="loading" :disabled="loading" />
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.pi-eye {
    transform: scale(1.6);
    margin-right: 1rem;
}

.pi-eye-slash {
    transform: scale(1.6);
    margin-right: 1rem;
}

.p-error {
    color: var(--red-500);
    font-size: 0.875rem;
}

.p-invalid {
    border-color: var(--red-500);
}
</style>
