<template>
  <div class="surface-ground flex align-items-center justify-content-center min-h-screen min-w-screen overflow-hidden">
    <div class="flex flex-column align-items-center justify-content-center">
      <div style="border-radius: 56px; padding: 0.3rem; background: linear-gradient(180deg, var(--primary-color) 10%, rgba(33, 150, 243, 0) 30%)">
        <div class="w-full surface-card py-8 px-5 sm:px-8" style="border-radius: 53px">
          <div class="text-center mb-5">
            <div class="text-900 text-3xl font-medium mb-3">Welcome Back</div>
            <span class="text-600 font-medium">Sign in to continue</span>
          </div>

          <div>
            <form @submit.prevent="handleLogin">
              <label for="email" class="block text-900 text-xl font-medium mb-2">Email</label>
              <InputText
                id="email"
                v-model="form.email"
                type="email"
                placeholder="Email address"
                class="w-full md:w-30rem mb-5"
                style="padding: 1rem"
                :class="{ 'p-invalid': errors.email }"
                required
              />
              <small v-if="errors.email" class="p-error">{{ errors.email }}</small>

              <label for="password" class="block text-900 font-medium text-xl mb-2">Password</label>
              <Password
                id="password"
                v-model="form.password"
                placeholder="Password"
                :toggleMask="true"
                class="w-full mb-3"
                inputClass="w-full"
                inputStyle="padding: 1rem"
                :class="{ 'p-invalid': errors.password }"
                :feedback="false"
                required
              />
              <small v-if="errors.password" class="p-error">{{ errors.password }}</small>

              <div v-if="errors.general" class="mb-3">
                <small class="p-error">{{ errors.general }}</small>
              </div>

              <Button
                type="submit"
                label="Sign In"
                class="w-full p-3 text-xl"
                :loading="loading"
                :disabled="loading"
              />
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()

const loading = ref(false)
const form = reactive({
  email: '',
  password: ''
})

const errors = reactive({
  email: '',
  password: '',
  general: ''
})

const clearErrors = () => {
  errors.email = ''
  errors.password = ''
  errors.general = ''
}

const validateForm = () => {
  clearErrors()
  let isValid = true

  if (!form.email) {
    errors.email = 'Email is required'
    isValid = false
  } else if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.email = 'Email is invalid'
    isValid = false
  }

  if (!form.password) {
    errors.password = 'Password is required'
    isValid = false
  }

  return isValid
}

const handleLogin = async () => {
  if (!validateForm()) {
    return
  }

  loading.value = true
  clearErrors()

  try {
    const result = await authStore.login({
      email: form.email,
      password: form.password
    })

    if (result.success) {
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Login successful',
        life: 3000
      })
      router.push('/')
    } else {
      errors.general = result.message || 'Login failed'
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: result.message || 'Login failed',
        life: 5000
      })
    }
  } catch (error) {
    console.error('Login error:', error)
    errors.general = 'An unexpected error occurred'
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'An unexpected error occurred',
      life: 5000
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.p-error {
  color: var(--red-500);
  font-size: 0.875rem;
}

.p-invalid {
  border-color: var(--red-500);
}
</style>
