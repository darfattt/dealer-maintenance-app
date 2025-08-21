<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import Card from 'primevue/card';
import ProgressSpinner from 'primevue/progressspinner';

const authStore = useAuthStore();

// Loading state
const loading = ref(true);
const iframeError = ref(false);

// TODO: Future enhancement - use dealer-specific workspace IDs
// Currently hardcoded workspace ID: 550e8400-e29b-41d4-a716-446655440000
// Future: const workspaceId = getWorkspaceByDealerId(authStore.userDealerId);
const WORKSPACE_ID = '550e8400-e29b-41d4-a716-446655440000';

// Construct sentiment analysis URL
const sentimentUrl = `https://sentiment.hegira.co.id/?workspace=${WORKSPACE_ID}`;

// Handle iframe load events
const onIframeLoad = () => {
    loading.value = false;
    iframeError.value = false;
};

const onIframeError = () => {
    loading.value = false;
    iframeError.value = true;
};

// Initialize component
onMounted(() => {
    // Set a timeout to hide loading if iframe doesn't load quickly
    setTimeout(() => {
        if (loading.value) {
            loading.value = false;
        }
    }, 10000); // 10 seconds timeout
});
</script>

<template>
    <div class="space-y-6">
        <!-- Header -->
        <div class="flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-surface-900 mb-2">Sentiment Analysis</h1>
                <p class="text-surface-600">Analyze customer sentiment and feedback patterns</p>
            </div>
        </div>

        <!-- Content Card -->
        <Card>
            <template #content>
                <!-- Loading State -->
                <div v-if="loading" class="flex flex-col items-center justify-center py-12">
                    <ProgressSpinner style="width: 50px; height: 50px;" strokeWidth="4" />
                    <p class="mt-4 text-surface-600">Loading Sentiment Analysis Tool...</p>
                </div>

                <!-- Error State -->
                <div v-else-if="iframeError" class="flex flex-col items-center justify-center py-12">
                    <i class="pi pi-exclamation-triangle text-4xl text-red-500 mb-4"></i>
                    <h3 class="text-lg font-semibold text-surface-900 mb-2">Unable to Load Sentiment Analysis</h3>
                    <p class="text-surface-600 text-center mb-4">
                        The sentiment analysis tool could not be loaded. Please check your internet connection and try again.
                    </p>
                    <button 
                        class="p-button p-button-primary"
                        @click="window.location.reload()"
                    >
                        Retry
                    </button>
                </div>

                <!-- Iframe Content -->
                <div v-else class="relative w-full" style="height: calc(100vh - 200px); min-height: 600px;">
                    <iframe
                        :src="sentimentUrl"
                        class="w-full h-full border-0 rounded-lg shadow-sm"
                        frameborder="0"
                        allowfullscreen
                        @load="onIframeLoad"
                        @error="onIframeError"
                        title="Sentiment Analysis Tool"
                    />
                </div>
            </template>
        </Card>
    </div>
</template>

<style scoped>
/* Custom styles for the sentiment analysis page */

/* Section spacing */
.space-y-6 > * + * {
    margin-top: 1.5rem;
}

/* Card hover effects */
:deep(.p-card) {
    transition: box-shadow 0.2s ease;
    min-height: 600px;
}

:deep(.p-card:hover) {
    box-shadow: 0 4px 25px 0 rgba(0, 0, 0, 0.1);
}

/* Iframe responsiveness */
iframe {
    background-color: #f8f9fa;
}

/* Loading and error states */
.flex.flex-col.items-center.justify-center {
    min-height: 400px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .relative.w-full {
        height: calc(100vh - 250px) !important;
        min-height: 500px !important;
    }
}

@media (max-width: 480px) {
    .relative.w-full {
        height: calc(100vh - 280px) !important;
        min-height: 400px !important;
    }
}
</style>