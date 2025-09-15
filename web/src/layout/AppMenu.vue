<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';

import AppMenuItem from './AppMenuItem.vue';

const authStore = useAuthStore();

// Check if user is DEALER_USER role
const isDealerUser = computed(() => {
    return authStore.userRole === 'DEALER_ADMIN';
});

const model = ref([
    {
        label: 'Home',
        items: [
            // Hide Dashboard items for DEALER_USER role
            ...(!isDealerUser.value
                ? [
                      { label: 'H1 (Work In Progress)', icon: 'pi pi-fw pi-chart-bar' },
                      { label: 'H23', icon: 'pi pi-fw pi-chart-line', to: '/h23-dashboard' }
                  ]
                : [])
        ]
    },
    {
        label: 'Customer',
        items: [
            { label: 'Customer Validation Request', icon: 'pi pi-fw pi-users', to: '/customer-validation' },
            { label: 'Customer Reminder Request', icon: 'pi pi-fw pi-bell', to: '/customer-reminders' },
            { label: 'Customer Satisfaction', icon: 'pi pi-fw pi-star', to: '/customer-satisfaction' }
        ]
    },
    {
        label: 'AHASS',
        items: [{ label: 'Sentiment Analysis', icon: 'pi pi-fw pi-chart-line', to: '/sentiment-analysis' }]
    }
]);
</script>

<template>
    <ul class="layout-menu">
        <template v-for="(item, i) in model" :key="item">
            <app-menu-item v-if="!item.separator" :item="item" :index="i"></app-menu-item>
            <li v-if="item.separator" class="menu-separator"></li>
        </template>
    </ul>
</template>

<style lang="scss" scoped></style>
