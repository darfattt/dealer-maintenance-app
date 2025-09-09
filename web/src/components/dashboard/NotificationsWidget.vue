<script setup>
import { ref } from 'vue';

const menu = ref(null);

const items = ref([
    { label: 'Add New', icon: 'pi pi-fw pi-plus' },
    { label: 'Remove', icon: 'pi pi-fw pi-trash' }
]);
</script>

<template>
    <div class="card">
        <div class="flex items-center justify-between mb-6">
            <div class="font-semibold text-xl">Notifications</div>
            <div>
                <Button icon="pi pi-ellipsis-v" class="p-button-text p-button-plain p-button-rounded" @click="$refs.menu.toggle($event)"></Button>
                <Menu ref="menu" popup :model="items" class="!min-w-40"></Menu>
            </div>
        </div>

        <span class="block text-muted-color font-medium mb-4">TODAY</span>
        <ul class="p-0 mx-0 mt-0 mb-6 list-none">
            <li class="flex items-center justify-between py-2 border-b border-surface">
                <div class="flex items-center flex-1">
                    <div class="w-10 h-10 flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-full mr-3 shrink-0">
                        <i class="pi pi-dollar text-lg text-blue-500"></i>
                    </div>
                    <div class="flex-1">
                        <div class="text-surface-900 dark:text-surface-0 font-medium text-sm">Richard Jones</div>
                        <div class="text-surface-700 dark:text-surface-100 text-xs">Blue t-shirt purchase</div>
                    </div>
                </div>
                <div class="text-primary font-bold text-sm">$79.00</div>
            </li>
            <li class="flex items-center justify-between py-2">
                <div class="flex items-center flex-1">
                    <div class="w-10 h-10 flex items-center justify-center bg-orange-100 dark:bg-orange-400/10 rounded-full mr-3 shrink-0">
                        <i class="pi pi-download text-lg text-orange-500"></i>
                    </div>
                    <div class="flex-1">
                        <div class="text-surface-900 dark:text-surface-0 font-medium text-sm">Withdrawal Request</div>
                        <div class="text-surface-700 dark:text-surface-100 text-xs">Initiated withdrawal</div>
                    </div>
                </div>
                <div class="text-primary font-bold text-sm">$2,500.00</div>
            </li>
        </ul>

        <span class="block text-muted-color font-medium mb-4">YESTERDAY</span>
        <ul class="p-0 m-0 list-none mb-6">
            <li class="flex items-center justify-between py-2 border-b border-surface">
                <div class="flex items-center flex-1">
                    <div class="w-10 h-10 flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-full mr-3 shrink-0">
                        <i class="pi pi-dollar text-lg text-blue-500"></i>
                    </div>
                    <div class="flex-1">
                        <div class="text-surface-900 dark:text-surface-0 font-medium text-sm">Keyser Wick</div>
                        <div class="text-surface-700 dark:text-surface-100 text-xs">Black jacket purchase</div>
                    </div>
                </div>
                <div class="text-primary font-bold text-sm">$59.00</div>
            </li>
            <li class="flex items-center justify-between py-2 border-b border-surface">
                <div class="flex items-center flex-1">
                    <div class="w-10 h-10 flex items-center justify-center bg-pink-100 dark:bg-pink-400/10 rounded-full mr-3 shrink-0">
                        <i class="pi pi-question text-lg text-pink-500"></i>
                    </div>
                    <div class="flex-1">
                        <div class="text-surface-900 dark:text-surface-0 font-medium text-sm">Jane Davis</div>
                        <div class="text-surface-700 dark:text-surface-100 text-xs">Product question posted</div>
                    </div>
                </div>
                <div class="text-surface-500 dark:text-surface-400 text-xs font-medium">1 question</div>
            </li>
        </ul>
        <span class="block text-muted-color font-medium mb-4">LAST WEEK</span>
        <ul class="p-0 m-0 list-none">
            <li class="flex items-center justify-between py-2 border-b border-surface">
                <div class="flex items-center flex-1">
                    <div class="w-10 h-10 flex items-center justify-center bg-green-100 dark:bg-green-400/10 rounded-full mr-3 shrink-0">
                        <i class="pi pi-arrow-up text-lg text-green-500"></i>
                    </div>
                    <div class="flex-1">
                        <div class="text-surface-900 dark:text-surface-0 font-medium text-sm">Revenue Growth</div>
                        <div class="text-surface-700 dark:text-surface-100 text-xs">Monthly increase</div>
                    </div>
                </div>
                <div class="text-green-600 font-bold text-sm">+25%</div>
            </li>
            <li class="flex items-center justify-between py-2 border-b border-surface">
                <div class="flex items-center flex-1">
                    <div class="w-10 h-10 flex items-center justify-center bg-purple-100 dark:bg-purple-400/10 rounded-full mr-3 shrink-0">
                        <i class="pi pi-heart text-lg text-purple-500"></i>
                    </div>
                    <div class="flex-1">
                        <div class="text-surface-900 dark:text-surface-0 font-medium text-sm">Wishlist Items</div>
                        <div class="text-surface-700 dark:text-surface-100 text-xs">Products added</div>
                    </div>
                </div>
                <div class="text-purple-600 font-bold text-sm">12 items</div>
            </li>
        </ul>
    </div>
</template>
