<template>
  <div class="layout-topbar">
    <router-link to="/" class="layout-topbar-logo">
      <img src="/logo.svg" alt="logo" />
      <span>Dealer Dashboard</span>
    </router-link>

    <button
      class="p-link layout-menu-button layout-topbar-button"
      @click="onMenuToggle"
    >
      <i class="pi pi-bars"></i>
    </button>

    <button
      class="p-link layout-topbar-menu-button layout-topbar-button"
      @click="onTopBarMenuButton"
    >
      <i class="pi pi-ellipsis-v"></i>
    </button>

    <div class="layout-topbar-menu" :class="topbarMenuClasses">
      <button @click="onTopBarMenuButton" class="p-link layout-topbar-button">
        <i class="pi pi-calendar"></i>
        <span>Calendar</span>
      </button>
      <button @click="onTopBarMenuButton" class="p-link layout-topbar-button">
        <i class="pi pi-user"></i>
        <span>Profile</span>
      </button>
      <button @click="onTopBarMenuButton" class="p-link layout-topbar-button">
        <i class="pi pi-cog"></i>
        <span>Settings</span>
      </button>
      <button @click="handleLogout" class="p-link layout-topbar-button">
        <i class="pi pi-sign-out"></i>
        <span>Logout</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()

const topbarMenuActive = ref(false)

const topbarMenuClasses = computed(() => ({
  'layout-topbar-menu-mobile-active': topbarMenuActive.value
}))

const onMenuToggle = () => {
  // This would typically emit an event to the parent to toggle sidebar
  // For now, we'll implement a simple toggle
  const sidebar = document.querySelector('.layout-sidebar')
  if (sidebar) {
    sidebar.classList.toggle('active')
  }
}

const onTopBarMenuButton = () => {
  topbarMenuActive.value = !topbarMenuActive.value
}

const handleLogout = async () => {
  try {
    const result = await authStore.logout()
    if (result.success) {
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Logged out successfully',
        life: 3000
      })
      router.push('/login')
    }
  } catch (error) {
    console.error('Logout error:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Logout failed',
      life: 5000
    })
  }
}
</script>

<style lang="scss" scoped>
.layout-topbar {
  position: fixed;
  height: 5rem;
  z-index: 997;
  left: 0;
  top: 0;
  width: 100%;
  padding: 0 2rem;
  background-color: var(--surface-card);
  transition: left 0.2s;
  display: flex;
  align-items: center;
  box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.02), 0px 0px 2px rgba(0, 0, 0, 0.05), 0px 1px 4px rgba(0, 0, 0, 0.08);
}

.layout-topbar-logo {
  display: flex;
  align-items: center;
  color: var(--surface-900);
  font-size: 1.5rem;
  font-weight: 500;
  width: 300px;
  border-radius: 12px;

  img {
    height: 2.5rem;
    margin-right: 0.5rem;
  }

  &:focus {
    box-shadow: var(--focus-ring);
  }
}

.layout-menu-button {
  display: none;
}

.layout-topbar-button {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  position: relative;
  color: var(--text-color-secondary);
  border-radius: 50%;
  width: 3rem;
  height: 3rem;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    color: var(--text-color);
    background-color: var(--surface-hover);
  }

  &:focus {
    box-shadow: var(--focus-ring);
  }

  i {
    font-size: 1.5rem;
  }

  span {
    font-size: 1rem;
    margin-left: 0.5rem;
  }
}

.layout-topbar-menu {
  margin: 0 0 0 auto;
  padding: 0;
  list-style: none;
  display: flex;

  .layout-topbar-button {
    margin-left: 1rem;
  }
}

.layout-topbar-menu-button {
  display: none;
}

@media (max-width: 991.98px) {
  .layout-topbar {
    justify-content: space-between;
  }

  .layout-topbar-logo {
    width: auto;
    order: 2;
  }

  .layout-menu-button {
    display: inline-flex;
    margin-right: 1rem;
    order: 1;
  }

  .layout-topbar-menu-button {
    display: inline-flex;
    order: 3;
  }

  .layout-topbar-menu {
    margin-left: 0;
    position: absolute;
    flex-direction: column;
    background-color: var(--surface-overlay);
    box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.02), 0px 0px 2px rgba(0, 0, 0, 0.05), 0px 1px 4px rgba(0, 0, 0, 0.08);
    border-radius: 12px;
    padding: 1rem;
    right: 2rem;
    top: 5rem;
    min-width: 15rem;
    display: none;
    -webkit-animation: scalein 0.15s linear;
    animation: scalein 0.15s linear;

    &.layout-topbar-menu-mobile-active {
      display: flex;
    }

    .layout-topbar-button {
      margin-left: 0;
      display: flex;
      width: 100%;
      height: auto;
      justify-content: flex-start;
      border-radius: 12px;
      padding: 1rem;

      i {
        font-size: 1rem;
        margin-right: 0.5rem;
      }

      span {
        font-weight: medium;
      }
    }
  }
}
</style>
