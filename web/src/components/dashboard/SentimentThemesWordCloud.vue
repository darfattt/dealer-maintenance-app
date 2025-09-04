<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import Card from 'primevue/card';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';
import CustomerService from '@/service/CustomerService';
import { useAuthStore } from '@/stores/auth';

// Props
const props = defineProps({
    dateFrom: {
        type: String,
        required: true
    },
    dateTo: {
        type: String,
        required: true
    },
    dealerId: {
        type: String,
        default: null
    },
    loading: {
        type: Boolean,
        default: false
    },
    searchTrigger: {
        type: Number,
        default: 0
    }
});

// Auth store for role-based logic
const authStore = useAuthStore();

// Reactive data
const themesLoading = ref(false);
const themesError = ref('');
const themesData = ref([]);
const wordCloudSvg = ref(null);

// Computed properties for themes data
const totalThemesMentions = computed(() => {
    return themesData.value.reduce((sum, theme) => sum + theme.count, 0);
});

const averageThemesMentions = computed(() => {
    if (themesData.value.length === 0) return 0;
    return Math.round(totalThemesMentions.value / themesData.value.length);
});

// Custom word cloud positioning algorithm
const positionedWords = computed(() => {
    if (themesData.value.length === 0) return [];

    const svgWidth = 600;
    const svgHeight = 400;
    const centerX = svgWidth / 2;
    const centerY = svgHeight / 2;
    const padding = 10; // Padding from edges

    // Calculate font sizes
    const values = themesData.value.map((t) => t.count);
    const minCount = Math.min(...values);
    const maxCount = Math.max(...values);
    const minFontSize = 14;
    const maxFontSize = 42;

    // Enhanced color palette for better visual appeal
    const colors = ['#0891b2', '#059669', '#dc2626', '#7c3aed', '#ea580c', '#0d9488', '#be185d'];

    const words = themesData.value.map((theme, index) => {
        // Calculate font size with better distribution
        let fontSize = minFontSize;
        if (maxCount > minCount) {
            const ratio = (theme.count - minCount) / (maxCount - minCount);
            // Use square root for better size distribution
            const adjustedRatio = Math.sqrt(ratio);
            fontSize = minFontSize + adjustedRatio * (maxFontSize - minFontSize);
        }

        return {
            text: theme.theme,
            count: theme.count,
            fontSize: Math.round(fontSize),
            color: colors[index % colors.length],
            placed: false,
            x: 0,
            y: 0
        };
    });

    // Enhanced positioning algorithm
    const positions = [];
    const gridSize = 15;
    const occupied = new Set();

    // Sort words by count (largest first) for better placement
    words.sort((a, b) => b.count - a.count);

    words.forEach((word, index) => {
        let placed = false;
        let attempts = 0;
        const maxAttempts = 200;

        // Start with center for first/largest word
        if (index === 0) {
            word.x = centerX;
            word.y = centerY;
            word.placed = true;
            positions.push(word);

            // Mark center area as occupied
            const textWidth = word.text.length * (word.fontSize * 0.6);
            const textHeight = word.fontSize;
            const gridX = Math.floor(centerX / gridSize);
            const gridY = Math.floor(centerY / gridSize);
            const gridCells = Math.ceil(textWidth / gridSize);
            const gridRows = Math.ceil(textHeight / gridSize);

            for (let gx = gridX - gridCells; gx <= gridX + gridCells; gx++) {
                for (let gy = gridY - gridRows; gy <= gridY + gridRows; gy++) {
                    occupied.add(`${gx},${gy}`);
                }
            }
            return;
        }

        // Use spiral pattern for other words
        while (!placed && attempts < maxAttempts) {
            const angle = attempts * 0.3;
            const radius = Math.sqrt(attempts) * 12;

            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);

            // Better text size estimation
            const textWidth = word.text.length * (word.fontSize * 0.55);
            const textHeight = word.fontSize * 1.2;

            // Check bounds with padding
            if (x - textWidth / 2 > padding && x + textWidth / 2 < svgWidth - padding && y - textHeight / 2 > padding && y + textHeight / 2 < svgHeight - padding) {
                // Enhanced collision detection
                const gridX = Math.floor(x / gridSize);
                const gridY = Math.floor(y / gridSize);
                const gridCells = Math.ceil(textWidth / gridSize) + 1;
                const gridRows = Math.ceil(textHeight / gridSize) + 1;

                let collision = false;
                for (let gx = gridX - gridCells; gx <= gridX + gridCells; gx++) {
                    for (let gy = gridY - gridRows; gy <= gridY + gridRows; gy++) {
                        if (occupied.has(`${gx},${gy}`)) {
                            collision = true;
                            break;
                        }
                    }
                    if (collision) break;
                }

                if (!collision) {
                    // Mark grid cells as occupied
                    for (let gx = gridX - gridCells; gx <= gridX + gridCells; gx++) {
                        for (let gy = gridY - gridRows; gy <= gridY + gridRows; gy++) {
                            occupied.add(`${gx},${gy}`);
                        }
                    }

                    word.x = Math.round(x);
                    word.y = Math.round(y);
                    word.placed = true;
                    placed = true;
                    positions.push(word);
                }
            }

            attempts++;
        }

        // Enhanced fallback positioning with bounds checking
        if (!placed) {
            let fallbackAttempts = 0;
            while (!placed && fallbackAttempts < 50) {
                const x = padding + Math.random() * (svgWidth - 2 * padding);
                const y = padding + Math.random() * (svgHeight - 2 * padding);

                const textWidth = word.text.length * (word.fontSize * 0.55);
                const textHeight = word.fontSize * 1.2;

                if (x - textWidth / 2 > padding && x + textWidth / 2 < svgWidth - padding && y - textHeight / 2 > padding && y + textHeight / 2 < svgHeight - padding) {
                    word.x = Math.round(x);
                    word.y = Math.round(y);
                    word.placed = true;
                    positions.push(word);
                    placed = true;
                }
                fallbackAttempts++;
            }
        }
    });

    return positions;
});

// Load sentiment themes data
const loadThemesData = async () => {
    if (!props.dateFrom || !props.dateTo) {
        themesError.value = 'Date range is required for loading themes data';
        return;
    }

    themesLoading.value = true;
    themesError.value = '';
    themesData.value = []; // Clear previous data

    try {
        // Prepare API filters
        const apiFilters = {
            dateFrom: props.dateFrom,
            dateTo: props.dateTo
        };

        // Use dealerId prop or fall back to auth store logic
        if (props.dealerId) {
            apiFilters.no_ahass = props.dealerId;
        } else if (authStore.userRole === 'DEALER_USER' && authStore.userDealerId) {
            apiFilters.no_ahass = authStore.userDealerId;
        }

        const response = await CustomerService.getSentimentThemesStatistics(apiFilters);

        if (response.success && response.data && response.data.themes) {
            const themes = response.data.themes;
            if (themes.length > 0) {
                themesData.value = themes.slice(0, 20); // Limit to top 20 themes for better visualization
            } else {
                themesError.value = 'No sentiment themes found for the selected period';
            }
        } else {
            throw new Error(response.message || 'Failed to fetch themes data');
        }
    } catch (err) {
        console.error('Error loading sentiment themes:', err);
        themesError.value = 'Failed to load sentiment themes data. Please try again later.';
        themesData.value = [];
    } finally {
        themesLoading.value = false;
    }
};

// Watch for prop changes
watch(
    [() => props.dateFrom, () => props.dateTo, () => props.dealerId, () => props.searchTrigger],
    () => {
        if (props.dateFrom && props.dateTo) {
           loadThemesData();
        }
    },
    { deep: true }
);

// Initialize on mount
onMounted(() => {
    if (props.dateFrom && props.dateTo) {
        loadThemesData();
    }
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100">Themes</h3>
                <ProgressSpinner v-if="loading || themesLoading" style="width: 20px; height: 20px" strokeWidth="4" />
            </div>
        </template>

        <template #content>
            <!-- Error Message -->
            <!-- <Message v-if="themesError && !themesLoading" severity="warn" :closable="false" class="mb-4">
                {{ themesError }}
            </Message> -->

            <!-- Word Cloud Container -->
            <div class="word-cloud-container" style="height: 200px">
                <!-- Custom Word Cloud -->
                <div v-if="!themesLoading && !loading && themesData.length > 0" class="w-full h-full relative overflow-hidden">
                    <svg ref="wordCloudSvg" class="w-full h-full" viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg">
                        <text
                            v-for="(word, index) in positionedWords"
                            :key="index"
                            :x="word.x"
                            :y="word.y"
                            :font-size="word.fontSize"
                            :fill="word.color"
                            text-anchor="middle"
                            dominant-baseline="middle"
                            class="word-cloud-text"
                            font-family="Inter, system-ui, -apple-system, sans-serif"
                            font-weight="600"
                            :title="`${word.text}: ${word.count} mentions`"
                            :style="`--index: ${index}`"
                        >
                            {{ word.text }}
                        </text>
                    </svg>
                </div>

                <!-- Loading State -->
                <div v-else-if="themesLoading || loading" class="flex flex-col items-center justify-center h-full">
                    <ProgressSpinner style="width: 50px; height: 50px" strokeWidth="4" />
                    <p class="text-muted-color text-sm mt-4">Loading sentiment themes...</p>
                </div>

                <!-- Empty State -->
                <div v-else class="flex flex-col items-center justify-center h-full">
                    <i class="pi pi-cloud text-4xl text-muted-color mb-4"></i>
                    <p class="text-muted-color text-sm">No sentiment themes available</p>
                </div>
            </div>

            <!-- Summary Stats 
            <div v-if="!themesLoading && !loading && themesData.length > 0" class="mt-4 pt-4 border-t border-surface-200 dark:border-surface-700">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div>
                        <div class="text-2xl font-bold text-primary-600">{{ themesData.length }}</div>
                        <div class="text-xs text-muted-color">Total Themes</div>
                    </div>
                    <div>
                        <div class="text-2xl font-bold text-primary-600">{{ totalThemesMentions }}</div>
                        <div class="text-xs text-muted-color">Total Mentions</div>
                    </div>
                    <div v-if="themesData[0]">
                        <div class="text-2xl font-bold text-primary-600">{{ themesData[0].count }}</div>
                        <div class="text-xs text-muted-color">Top Theme</div>
                    </div>
                    <div>
                        <div class="text-2xl font-bold text-primary-600">{{ averageThemesMentions }}</div>
                        <div class="text-xs text-muted-color">Avg per Theme</div>
                    </div>
                </div>
            </div>
        -->
        </template>
    </Card>
</template>

<style scoped>
/* Word cloud styling */
.word-cloud-text {
    cursor: pointer;
    transition:
        opacity 0.2s ease,
        transform 0.2s ease;
}

.word-cloud-text:hover {
    opacity: 0.8;
    transform: scale(1.1);
}

/* Word cloud container */
.word-cloud-container {
    background: linear-gradient(135deg, var(--surface-50) 0%, var(--surface-100) 100%);
    border-radius: 12px;
    border: 1px solid var(--surface-200);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

:root.dark .word-cloud-container {
    background: linear-gradient(135deg, var(--surface-800) 0%, var(--surface-900) 100%);
    border-color: var(--surface-700);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* Responsive word cloud */
@media (max-width: 768px) {
    .word-cloud-text {
        font-size: 0.9em !important;
    }

    .word-cloud-container {
        height: 300px !important;
    }
}

/* Animation for word cloud loading */
@keyframes fadeInScale {
    from {
        opacity: 0;
        transform: scale(0.8);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.word-cloud-text {
    animation: fadeInScale 0.5s ease-out forwards;
    animation-delay: calc(var(--index, 0) * 0.05s);
}

/* Theme-aware styling */
.text-muted-color {
    color: var(--text-color-secondary);
    transition: color 0.3s ease;
}

/* Border styling */
.border-t {
    border-top: 1px solid;
}

.border-surface-200 {
    border-color: var(--surface-200);
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
    .border-surface-700 {
        border-color: var(--surface-700);
    }
}

/* Grid and layout */
.grid {
    display: grid;
}

.grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
}

@media (min-width: 768px) {
    .md\:grid-cols-4 {
        grid-template-columns: repeat(4, minmax(0, 1fr));
    }
}

.gap-4 {
    gap: 1rem;
}

.text-center {
    text-align: center;
}

.mt-4 {
    margin-top: 1rem;
}

.pt-4 {
    padding-top: 1rem;
}

.mb-4 {
    margin-bottom: 1rem;
}

/* Flex utilities */
.flex {
    display: flex;
}

.flex-col {
    flex-direction: column;
}

.items-center {
    align-items: center;
}

.justify-center {
    justify-content: center;
}

.justify-between {
    justify-content: space-between;
}

.h-full {
    height: 100%;
}

.w-full {
    width: 100%;
}

.relative {
    position: relative;
}

.overflow-hidden {
    overflow: hidden;
}
</style>
