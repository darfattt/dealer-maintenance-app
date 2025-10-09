<script setup>
import { ref } from 'vue';
import AppMenuItem from './AppMenuItem.vue';

const model = ref([
    {
        label: 'Dealer Management',
        items: [
            {
                label: 'Register New Dealer',
                icon: 'pi pi-fw pi-plus-circle',
                to: '/dealer-management/register'
            },
            {
                label: 'Dealers',
                icon: 'pi pi-fw pi-building',
                to: '/dealer-management'
            },
        ]
    },
    {
        label: 'Monitoring',
        items: [
            {
                label: 'System Logs',
                icon: 'pi pi-fw pi-chart-bar',
                to: '/system-logs/summary'
            },
            {
                label: 'Activities',
                icon: 'pi pi-fw pi-list',
                to: '/system-logs/activities'
            },
            {
                label: 'Anomalies',
                icon: 'pi pi-fw pi-exclamation-triangle',
                to: '/anomalies'
            }
        ]
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
