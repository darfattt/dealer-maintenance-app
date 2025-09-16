<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import Card from 'primevue/card';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';
import CustomerService from '@/service/CustomerService';

// Props from parent
const props = defineProps({
    dealerId: {
        type: String,
        default: null
    },
    dateFrom: {
        type: String,
        required: true
    },
    dateTo: {
        type: String,
        required: true
    },
    reminderTarget: {
        type: String,
        default: null
    }
});

// Reactive data
const loading = ref(false);
const error = ref('');
const topUnits = ref([]);

// Computed properties
const effectiveDealerId = computed(() => {
    return props.dealerId || '12284';
});

// Methods
const fetchTipeUnitData = async () => {
    if (!props.dateFrom || !props.dateTo) {
        error.value = 'Missing required date parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        // Call the tipe unit stats API
        const response = await CustomerService.getTipeUnitStats(props.dateFrom, props.dateTo, effectiveDealerId.value, props.reminderTarget);

        if (response.success && response.data) {
            // Convert API response to top 5 units with percentages
            const unitEntries = Object.entries(response.data);
            const totalUnits = unitEntries.reduce((sum, [, count]) => sum + count, 0);

            // Sort by count descending and take top 5
            const sortedUnits = unitEntries.sort(([, a], [, b]) => b - a).slice(0, 5);

            topUnits.value = sortedUnits.map(([unitName, count], index) => {
                const percentage = totalUnits > 0 ? ((count / totalUnits) * 100).toFixed(1) : 0;

                return {
                    id: index + 1,
                    rank: index + 1,
                    name: unitName === 'Unknown' ? 'Unit Tidak Diketahui' : unitName,
                    image: getUnitImage(unitName),
                    totalUnits: count,
                    percentage: parseFloat(percentage),
                    description: `${count} Units (${percentage}%)`
                };
            });
        } else {
            throw new Error(response.message || 'Failed to fetch data');
        }
    } catch (err) {
        console.error('Error fetching tipe unit data:', err);
        error.value = 'Error API';
    } finally {
        loading.value = false;
    }
};

// Get unit image based on unit name
const getUnitImage = (unitName) => {
    // Define unit images mapping
    const unitImages = {
        'VARIO 125 CBS ISS': '/demo/images/avatar/motorcycle-vario.svg',
        'Beat Street': '/demo/images/avatar/motorcycle-beat.svg',
        'PCX 160': '/demo/images/avatar/motorcycle-pcx.svg',
        'Scoopy Sporty': '/demo/images/avatar/motorcycle-scoopy.svg',
        'ADV 160': '/demo/images/avatar/motorcycle-adv.svg'
    };

    // Return specific image or default motorcycle icon
    return unitImages[unitName] || '/demo/images/avatar/motorcycle.svg';
};

// Get rank color based on position
const getRankColor = (rank) => {
    switch (rank) {
        case 1:
            return 'text-yellow-500'; // Gold
        case 2:
            return 'text-gray-400'; // Silver
        case 3:
            return 'text-orange-600'; // Bronze
        default:
            return 'text-surface-500'; // Default
    }
};

// Get percentage color based on value
const getPercentageColor = (percentage) => {
    if (percentage >= 30) return 'text-green-600';
    if (percentage >= 20) return 'text-blue-600';
    if (percentage >= 10) return 'text-orange-600';
    return 'text-surface-600';
};

// Watch for prop changes
watch(
    [() => props.dealerId, () => props.dateFrom, () => props.dateTo, () => props.reminderTarget],
    () => {
        fetchTipeUnitData();
    },
    { immediate: false }
);

// Lifecycle
onMounted(() => {
    fetchTipeUnitData();
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <h3 class="text-lg font-semibold text-surface-900">JENIS UNIT</h3>
                <!-- Loading indicator -->
                <ProgressSpinner v-if="loading" style="width: 20px; height: 20px" strokeWidth="4" />
            </div>
        </template>

        <template #content>
            <!-- Error Message -->
            <Message v-if="error && !loading" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Top Units List -->
            <div v-if="!loading && topUnits.length > 0" class="space-y-4">
                <div v-for="unit in topUnits" :key="unit.id" class="flex items-center space-x-4 p-3 rounded-lg border border-surface-200 hover:bg-surface-50 transition-colors">
                    <!-- Rank Badge -->
                    <div class="flex-shrink-0">
                        <div class="w-8 h-8 flex items-center justify-center rounded-full bg-surface-100">
                            <span :class="['font-bold text-sm', getRankColor(unit.rank)]">
                                {{ unit.rank }}
                            </span>
                        </div>
                    </div>

                    <!-- Unit Image -->
                    <div class="flex-shrink-0">
                        <img :src="unit.image" :alt="unit.name" class="w-12 h-12 object-cover rounded-lg border-2 border-surface-200" @error="$event.target.src = '/assets/images/motor.png'" />
                    </div>

                    <!-- Unit Details -->
                    <div class="flex-grow min-w-0">
                        <h4 class="font-bold text-base text-surface-900 truncate">{{ unit.name }}</h4>
                        <p class="text-sm text-surface-600">{{ unit.description }}</p>
                    </div>

                    <!-- Percentage Display -->
                    <div class="flex-shrink-0 text-right">
                        <div :class="['text-2xl font-bold', getPercentageColor(unit.percentage)]">{{ unit.percentage }}%</div>
                        <div class="text-xs text-surface-500">{{ unit.totalUnits }} units</div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <ProgressSpinner style="width: 50px; height: 50px" strokeWidth="4" class="mb-4" />
                <p class="text-muted-color text-sm">Loading vehicle types...</p>
            </div>

            <!-- Empty State -->
            <div v-if="!loading && !error && topUnits.length === 0" class="text-center py-8">
                <i class="pi pi-info-circle text-4xl text-muted-color mb-4"></i>
                <p class="text-muted-color text-sm">No vehicle type data available</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* Custom styles for the widget */
.space-y-4 > * + * {
    margin-top: 1rem;
}

/* Layout utilities */
.flex {
    display: flex;
}

.items-center {
    align-items: center;
}

.justify-between {
    justify-content: space-between;
}

.justify-center {
    justify-content: center;
}

.flex-col {
    flex-direction: column;
}

.flex-grow {
    flex-grow: 1;
}

.flex-shrink-0 {
    flex-shrink: 0;
}

.space-x-4 > * + * {
    margin-left: 1rem;
}

.min-w-0 {
    min-width: 0;
}

.w-8 {
    width: 2rem;
}

.h-8 {
    height: 2rem;
}

.w-12 {
    width: 3rem;
}

.h-12 {
    height: 3rem;
}

.text-right {
    text-align: right;
}

.text-center {
    text-align: center;
}

.truncate {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.rounded-lg {
    border-radius: 0.5rem;
}

.rounded-full {
    border-radius: 9999px;
}

.border {
    border-width: 1px;
}

.border-2 {
    border-width: 2px;
}

.border-surface-200 {
    border-color: var(--surface-200);
}

.bg-surface-50 {
    background-color: var(--surface-50);
}

.bg-surface-100 {
    background-color: var(--surface-100);
}

.p-3 {
    padding: 0.75rem;
}

.py-8 {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.mb-4 {
    margin-bottom: 1rem;
}

.transition-colors {
    transition-property: color, background-color, border-color, text-decoration-color, fill, stroke;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    transition-duration: 150ms;
}

.hover\:bg-surface-50:hover {
    background-color: var(--surface-50);
}

/* Text size utilities */
.text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
}

.text-sm {
    font-size: 0.875rem;
    line-height: 1.25rem;
}

.text-base {
    font-size: 1rem;
    line-height: 1.5rem;
}

.text-lg {
    font-size: 1.125rem;
    line-height: 1.75rem;
}

.text-2xl {
    font-size: 1.5rem;
    line-height: 2rem;
}

.text-4xl {
    font-size: 2.25rem;
    line-height: 2.5rem;
}

.font-bold {
    font-weight: 700;
}

.font-semibold {
    font-weight: 600;
}

/* Color utilities */
.text-surface-500 {
    color: var(--surface-500);
}

.text-surface-600 {
    color: var(--surface-600);
}

.text-surface-900 {
    color: var(--surface-900);
}

.text-muted-color {
    color: var(--text-color-secondary);
}

.text-yellow-500 {
    color: rgb(234 179 8);
}

.text-gray-400 {
    color: rgb(156 163 175);
}

.text-orange-600 {
    color: rgb(234 88 12);
}

.text-green-600 {
    color: rgb(22 163 74);
}

.text-blue-600 {
    color: rgb(37 99 235);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .space-x-4 > * + * {
        margin-left: 0.5rem;
    }

    .w-12,
    .h-12 {
        width: 2.5rem;
        height: 2.5rem;
    }

    .text-base {
        font-size: 0.875rem;
    }

    .text-sm {
        font-size: 0.75rem;
    }

    .text-2xl {
        font-size: 1.25rem;
    }

    .p-3 {
        padding: 0.5rem;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .hover\:bg-surface-50:hover {
        background-color: var(--surface-700);
    }

    .border-surface-200 {
        border-color: var(--surface-600);
    }
}
</style>
