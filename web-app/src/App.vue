<template>
  <div id="app">
    <Toast />
    <ConfirmDialog />
    
    <!-- Show login page if not authenticated -->
    <LoginView v-if="!authStore.isAuthenticated" />
    
    <!-- Show main layout if authenticated -->
    <div v-else class="layout-wrapper layout-static">
      <AppTopbar />
      <AppSidebar />
      
      <div class="layout-main-container">
        <div class="layout-main">
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import AppTopbar from '@/components/layout/AppTopbar.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'

const authStore = useAuthStore()

onMounted(() => {
  // Check if user is already authenticated on app load
  authStore.checkAuth()
})
</script>

<style lang="scss">
@import '@/assets/styles/layout.scss';
</style>
