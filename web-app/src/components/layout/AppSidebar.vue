<template>
  <div class="layout-sidebar">
    <AppMenu />
  </div>
</template>

<script setup>
import AppMenu from './AppMenu.vue'
</script>

<style lang="scss" scoped>
.layout-sidebar {
  position: fixed;
  width: 300px;
  height: calc(100vh - 5rem);
  z-index: 999;
  overflow-y: auto;
  top: 5rem;
  left: 0;
  background-color: var(--surface-card);
  border-right: 1px solid var(--surface-border);
  transition: transform 0.2s, left 0.2s;
  display: flex;
  flex-direction: column;
}

@media (max-width: 991.98px) {
  .layout-sidebar {
    transform: translateX(-100%);

    &.active {
      transform: translateX(0);
    }
  }
}
</style>
