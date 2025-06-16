<template>
  <div class="layout-menu-container">
    <ul class="layout-menu">
      <li class="menu-item">
        <router-link to="/" class="p-ripple">
          <i class="pi pi-home"></i>
          <span>Home</span>
          <Ripple />
        </router-link>
        <ul class="layout-submenu">
          <li>
            <router-link to="/" class="p-ripple">
              <i class="pi pi-fw pi-chart-line"></i>
              <span>Dashboard</span>
              <Ripple />
            </router-link>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<script setup>
import Ripple from 'primevue/ripple'
</script>

<style lang="scss" scoped>
.layout-menu-container {
  padding: 0.5rem 0;
}

.layout-menu {
  margin: 0;
  padding: 0;
  list-style-type: none;

  .menu-item {
    > a {
      color: var(--text-color);
      display: flex;
      align-items: center;
      position: relative;
      outline: 0 none;
      cursor: pointer;
      padding: 1rem;
      border: none;
      width: 100%;
      border-radius: 12px;
      overflow: hidden;
      user-select: none;
      margin: 0.25rem 1rem;
      width: calc(100% - 2rem);

      .layout-menuitem-icon {
        margin-right: 0.5rem;
      }

      .layout-menuitem-text {
        line-height: 1;
      }

      &.router-link-active {
        font-weight: 700;
        color: var(--primary-color);
      }

      &:hover {
        background-color: var(--surface-hover);
      }

      &:focus {
        box-shadow: var(--focus-ring);
      }

      i {
        margin-right: 0.5rem;
        font-size: 1rem;
      }
    }
  }

  .layout-submenu {
    margin: 0;
    list-style: none;
    padding: 0;
    padding-left: 1rem;

    > li {
      > a {
        color: var(--text-color-secondary);
        display: flex;
        align-items: center;
        position: relative;
        outline: 0 none;
        cursor: pointer;
        padding: 0.75rem 1rem;
        border: none;
        width: 100%;
        border-radius: 12px;
        overflow: hidden;
        user-select: none;
        margin: 0.25rem 1rem;
        width: calc(100% - 2rem);

        &.router-link-active {
          font-weight: 700;
          color: var(--primary-color);
        }

        &:hover {
          background-color: var(--surface-hover);
        }

        &:focus {
          box-shadow: var(--focus-ring);
        }

        i {
          margin-right: 0.5rem;
          font-size: 0.875rem;
        }
      }
    }
  }
}
</style>
