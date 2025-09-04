import { ref, computed, onMounted } from 'vue';
import CustomerService from '@/service/CustomerService';

// Global reactive state for dealers (shared across components)
const dealers = ref([]);
const loading = ref(false);
const error = ref(null);
let isInitialized = false;

export function useDealers() {
    /**
     * Load active dealers from API and format for dropdown
     */
    const loadDealers = async () => {
        if (loading.value) return; // Prevent multiple simultaneous loads

        loading.value = true;
        error.value = null;

        try {
            const response = await CustomerService.getActiveDealers();

            if (response.success && response.data) {
                // Format dealers for dropdown with existing pattern: "Dealer Name (dealer_id)"
                dealers.value = response.data.map((dealer) => ({
                    label: `${dealer.dealer_name} (${dealer.dealer_id})`,
                    value: dealer.dealer_id
                }));
                console.log(`Loaded ${dealers.value.length} active dealers`);
            } else {
                throw new Error(response.message || 'Failed to load dealers');
            }
        } catch (err) {
            console.error('Error loading dealers:', err);
            error.value = err.message || 'Failed to load active dealers';
            // Fallback to empty array on error
            dealers.value = [];
        } finally {
            loading.value = false;
        }
    };

    /**
     * Initialize dealers on first use
     */
    const initializeDealers = async () => {
        if (!isInitialized) {
            isInitialized = true;
            await loadDealers();
        }
    };

    /**
     * Computed property for dealer options (reactive)
     */
    const dealerOptions = computed(() => dealers.value);

    /**
     * Computed property to check if dealers are available
     */
    const hasDealers = computed(() => dealers.value.length > 0);

    /**
     * Computed property for loading state
     */
    const isLoading = computed(() => loading.value);

    /**
     * Computed property for error state
     */
    const hasError = computed(() => error.value !== null);

    /**
     * Get error message
     */
    const errorMessage = computed(() => error.value);

    /**
     * Refresh dealers data
     */
    const refreshDealers = async () => {
        await loadDealers();
    };

    // Auto-initialize when composable is used
    onMounted(() => {
        initializeDealers();
    });

    return {
        // Data
        dealerOptions,
        isLoading,
        hasError,
        errorMessage,
        hasDealers,

        // Methods
        loadDealers,
        refreshDealers,
        initializeDealers
    };
}
