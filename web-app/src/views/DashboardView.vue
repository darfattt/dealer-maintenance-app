<template>
  <div class="grid">
    <div class="col-12">
      <div class="card">
        <h5>Dashboard</h5>
        <p>Welcome to the Dealer Dashboard! This is a clean, minimal implementation using Sakai PrimeVue.</p>
        
        <!-- User Info Card -->
        <div class="grid">
          <div class="col-12 md:col-6 lg:col-3">
            <div class="surface-0 shadow-2 p-3 border-1 border-50 border-round">
              <div class="flex justify-content-between mb-3">
                <div>
                  <span class="block text-500 font-medium mb-3">Welcome</span>
                  <div class="text-900 font-medium text-xl">{{ authStore.userName }}</div>
                </div>
                <div class="flex align-items-center justify-content-center bg-blue-100 border-round" style="width: 2.5rem; height: 2.5rem">
                  <i class="pi pi-user text-blue-500 text-xl"></i>
                </div>
              </div>
              <span class="text-green-500 font-medium">{{ authStore.userRole }}</span>
              <span class="text-500"> role</span>
            </div>
          </div>

          <div class="col-12 md:col-6 lg:col-3">
            <div class="surface-0 shadow-2 p-3 border-1 border-50 border-round">
              <div class="flex justify-content-between mb-3">
                <div>
                  <span class="block text-500 font-medium mb-3">Status</span>
                  <div class="text-900 font-medium text-xl">Active</div>
                </div>
                <div class="flex align-items-center justify-content-center bg-green-100 border-round" style="width: 2.5rem; height: 2.5rem">
                  <i class="pi pi-check-circle text-green-500 text-xl"></i>
                </div>
              </div>
              <span class="text-green-500 font-medium">Online</span>
              <span class="text-500"> session</span>
            </div>
          </div>

          <div class="col-12 md:col-6 lg:col-3">
            <div class="surface-0 shadow-2 p-3 border-1 border-50 border-round">
              <div class="flex justify-content-between mb-3">
                <div>
                  <span class="block text-500 font-medium mb-3">Services</span>
                  <div class="text-900 font-medium text-xl">Available</div>
                </div>
                <div class="flex align-items-center justify-content-center bg-cyan-100 border-round" style="width: 2.5rem; height: 2.5rem">
                  <i class="pi pi-server text-cyan-500 text-xl"></i>
                </div>
              </div>
              <span class="text-green-500 font-medium">All systems</span>
              <span class="text-500"> operational</span>
            </div>
          </div>

          <div class="col-12 md:col-6 lg:col-3">
            <div class="surface-0 shadow-2 p-3 border-1 border-50 border-round">
              <div class="flex justify-content-between mb-3">
                <div>
                  <span class="block text-500 font-medium mb-3">Version</span>
                  <div class="text-900 font-medium text-xl">v1.0.0</div>
                </div>
                <div class="flex align-items-center justify-content-center bg-purple-100 border-round" style="width: 2.5rem; height: 2.5rem">
                  <i class="pi pi-code text-purple-500 text-xl"></i>
                </div>
              </div>
              <span class="text-green-500 font-medium">Latest</span>
              <span class="text-500"> release</span>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="mt-5">
          <h6>Quick Actions</h6>
          <div class="flex flex-wrap gap-3">
            <Button 
              label="View Analytics" 
              icon="pi pi-chart-line" 
              class="p-button-outlined"
              @click="openAnalytics"
            />
            <Button 
              label="Admin Panel" 
              icon="pi pi-cog" 
              class="p-button-outlined"
              @click="openAdminPanel"
            />
            <Button 
              label="API Documentation" 
              icon="pi pi-book" 
              class="p-button-outlined"
              @click="openApiDocs"
            />
          </div>
        </div>

        <!-- System Information -->
        <div class="mt-5">
          <h6>System Information</h6>
          <div class="surface-100 p-3 border-round">
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="text-500 mb-2">Backend Services</div>
                <div class="text-900">
                  <i class="pi pi-circle-fill text-green-500 mr-2"></i>
                  Account Service (Port 8100)
                </div>
                <div class="text-900">
                  <i class="pi pi-circle-fill text-green-500 mr-2"></i>
                  API Gateway (Port 8080)
                </div>
                <div class="text-900">
                  <i class="pi pi-circle-fill text-green-500 mr-2"></i>
                  Main Backend (Port 8000)
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="text-500 mb-2">Frontend Applications</div>
                <div class="text-900">
                  <i class="pi pi-circle-fill text-blue-500 mr-2"></i>
                  Web App (Port 3000)
                </div>
                <div class="text-900">
                  <i class="pi pi-circle-fill text-green-500 mr-2"></i>
                  Analytics Dashboard (Port 8501)
                </div>
                <div class="text-900">
                  <i class="pi pi-circle-fill text-green-500 mr-2"></i>
                  Admin Panel (Port 8502)
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const openAnalytics = () => {
  window.open('http://localhost:8501', '_blank')
}

const openAdminPanel = () => {
  window.open('http://localhost:8502', '_blank')
}

const openApiDocs = () => {
  window.open('http://localhost:8000/docs', '_blank')
}
</script>
