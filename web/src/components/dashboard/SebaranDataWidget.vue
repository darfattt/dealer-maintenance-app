<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import Card from 'primevue/card';
import Message from 'primevue/message';

// Use a simpler approach without dynamic imports
const initLeaflet = async () => {
    if (typeof window === 'undefined') return null;

    try {
        // Load Leaflet using script tag approach
        if (!window.L) {
            // Create script tag for Leaflet
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
            script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
            script.crossOrigin = '';

            // Create CSS link
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
            link.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
            link.crossOrigin = '';

            // Add to head
            document.head.appendChild(link);
            document.head.appendChild(script);

            // Wait for script to load
            await new Promise((resolve, reject) => {
                script.onload = resolve;
                script.onerror = reject;
            });
        }

        console.log('Leaflet loaded from CDN:', !!window.L);
        return window.L;
    } catch (error) {
        console.error('Error loading Leaflet from CDN:', error);
        throw new Error('Failed to load Leaflet: ' + error.message);
    }
};

// Props from parent dashboard
const props = defineProps({
    dealerId: {
        type: String,
        default: '12284'
    },
    dateFrom: {
        type: String,
        required: true
    },
    dateTo: {
        type: String,
        required: true
    }
});

// Reactive data
const loading = ref(false);
const error = ref('');
const mapContainer = ref(null);
const map = ref(null);
const markers = ref([]);
const regionData = ref([]);

// West Java cities data with coordinates
const westJavaCities = [
    { name: 'Arcamanik', lat: -6.9175, lng: 107.6537, percentage: 30, color: '#10B981' },
    { name: 'Astanaanyar', lat: -6.9147, lng: 107.5794, percentage: 15, color: '#F59E0B' },
    { name: 'Bandung Kidul', lat: -6.9389, lng: 107.6194, percentage: 3, color: '#EF4444' },
    { name: 'Andir', lat: -6.9147, lng: 107.5794, percentage: 5, color: '#3B82F6' },
    { name: 'Others', lat: -6.8781, lng: 107.6298, percentage: 2, color: '#6B7280' }
];

// Methods
const fetchSebaranData = async () => {
    if (!props.dealerId || !props.dateFrom || !props.dateTo) {
        error.value = 'Missing required parameters';
        return;
    }

    loading.value = true;
    error.value = '';

    try {
        console.log('Starting to fetch sebaran data...');

        // Initialize Leaflet first
        const L = await initLeaflet();
        console.log('Leaflet initialized:', !!L);

        if (!L) {
            throw new Error('Leaflet failed to load');
        }

        // Use the West Java cities data
        regionData.value = westJavaCities;
        console.log('Region data set:', regionData.value.length, 'regions');

        await nextTick();
        console.log('Next tick completed, initializing map...');
        await initializeMap(L);

    } catch (err) {
        console.error('Error fetching sebaran data:', err);
        error.value = 'Failed to fetch distribution data: ' + err.message;
    } finally {
        loading.value = false;
    }
};

const initializeMap = async (L) => {
    console.log('initializeMap called');
    console.log('mapContainer.value:', !!mapContainer.value);
    console.log('L available:', !!L);
    console.log('L.map function:', typeof L?.map);

    if (!mapContainer.value) {
        console.log('Map container not available');
        error.value = 'Map container not available';
        return;
    }

    if (!L || typeof L.map !== 'function') {
        console.log('Leaflet not properly loaded');
        error.value = 'Leaflet library not properly loaded';
        return;
    }

    try {
        console.log('Starting map initialization...');

        // Destroy existing map if it exists
        if (map.value) {
            console.log('Removing existing map');
            map.value.remove();
            map.value = null;
        }

        // Clear existing markers
        markers.value = [];

        console.log('Creating new map instance...');
        // Initialize map centered on West Java (Bandung area)
        map.value = L.map(mapContainer.value, {
            center: [-6.9175, 107.6191],
            zoom: 11,
            zoomControl: true,
            scrollWheelZoom: true
        });

        console.log('Map instance created, adding tile layer...');
        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(map.value);

        console.log('Tile layer added, adding markers...');
        // Add markers for each region
        regionData.value.forEach((region, index) => {
            console.log(`Adding marker ${index + 1}:`, region.name);
            const markerSize = Math.max(8, region.percentage * 0.8); // Scale marker size

            const marker = L.circleMarker([region.lat, region.lng], {
                radius: markerSize,
                fillColor: region.color,
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map.value);

            marker.bindPopup(`
                <div style="text-align: center; padding: 5px;">
                    <strong style="font-size: 14px;">${region.name}</strong><br>
                    <span style="color: ${region.color}; font-weight: bold; font-size: 16px;">${region.percentage}%</span>
                </div>
            `);

            markers.value.push(marker);
        });

        console.log('Map initialized successfully with', markers.value.length, 'markers');
    } catch (error) {
        console.error('Error initializing map:', error);
        error.value = 'Failed to initialize map: ' + error.message;
    }
};

// Watch for prop changes
watch([() => props.dealerId, () => props.dateFrom, () => props.dateTo], () => {
    fetchSebaranData();
}, { deep: true });

// Lifecycle
onMounted(() => {
    fetchSebaranData();
});

onUnmounted(() => {
    // Clean up map instance
    if (map.value) {
        map.value.remove();
        map.value = null;
    }
    markers.value = [];
});
</script>

<template>
    <Card class="h-full">
        <template #title>
            <div class="flex justify-between items-center">
                <span class="text-sm font-bold uppercase">SEBARAN DATA PROSPECT</span>
            </div>
        </template>
        
        <template #content>
            <!-- Error Message -->
            <Message v-if="error" severity="warn" :closable="false" class="mb-4">
                {{ error }}
            </Message>

            <!-- Map and Legend Container -->
            <div v-if="!loading" class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <!-- Map -->
                <div class="lg:col-span-2">
                    <div
                        ref="mapContainer"
                        class="h-64 w-full rounded-lg border border-surface-200 relative"
                        style="min-height: 300px;"
                    >
                        <!-- Error overlay -->
                        <div v-if="error" class="absolute inset-0 flex items-center justify-center bg-surface-50 rounded-lg">
                            <div class="text-center p-4">
                                <i class="pi pi-exclamation-triangle text-4xl text-orange-500 mb-2"></i>
                                <p class="text-sm font-medium text-surface-700 mb-1">Map Loading Issue</p>
                                <p class="text-xs text-surface-500">{{ error }}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Legend -->
                <div class="lg:col-span-1 flex flex-col justify-center">
                    <div class="space-y-3">
                        <div
                            v-for="(region, index) in regionData"
                            :key="index"
                            class="flex items-center justify-between p-2 rounded border border-surface-200"
                        >
                            <div class="flex items-center space-x-2">
                                <div
                                    class="w-4 h-4 rounded-full border-2 border-white"
                                    :style="{ backgroundColor: region.color }"
                                ></div>
                                <span class="text-xs font-medium">{{ region.name }}</span>
                            </div>
                            <div class="text-right">
                                <div 
                                    class="font-bold text-sm px-2 py-1 rounded text-white"
                                    :style="{ backgroundColor: region.color }"
                                >
                                    {{ region.percentage }}%
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-8">
                <i class="pi pi-spin pi-spinner text-2xl text-primary mb-2"></i>
                <p class="text-muted-color text-sm">Loading map...</p>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* Leaflet map styling */
:deep(.leaflet-container) {
    height: 100%;
    width: 100%;
    border-radius: 0.5rem;
}

:deep(.leaflet-popup-content-wrapper) {
    border-radius: 0.375rem;
}

:deep(.leaflet-popup-content) {
    margin: 8px 12px;
    font-size: 0.875rem;
}

/* Custom marker styling */
:deep(.leaflet-marker-icon) {
    border-radius: 50%;
}
</style>
