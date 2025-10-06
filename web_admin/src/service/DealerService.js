import ApiService from './ApiService';

/**
 * Dealer Service for Admin Portal (SYSTEM_ADMIN only)
 * Handles all dealer management operations
 */
class DealerService {
    /**
     * Get all dealers with pagination and filtering
     * @param {Object} params - Query parameters
     * @param {number} params.page - Page number (1-indexed)
     * @param {number} params.page_size - Items per page
     * @param {string} params.search - Search term for dealer ID or name
     * @param {boolean} params.is_active - Filter by active status
     * @returns {Promise} API response
     */
    async getAllDealers(params = {}) {
        try {
            const queryParams = new URLSearchParams();

            if (params.page) queryParams.append('page', params.page);
            if (params.page_size) queryParams.append('page_size', params.page_size);
            if (params.search) queryParams.append('search', params.search);
            if (params.is_active !== undefined && params.is_active !== null) {
                queryParams.append('is_active', params.is_active);
            }

            const response = await ApiService.get(`/v1/admin/dealers?${queryParams.toString()}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching dealers:', error);
            throw error;
        }
    }

    /**
     * Get single dealer by ID
     * @param {string} dealerId - Dealer ID
     * @returns {Promise} API response with dealer details
     */
    async getDealerById(dealerId) {
        try {
            const response = await ApiService.get(`/v1/admin/dealers/${dealerId}`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching dealer ${dealerId}:`, error);
            throw error;
        }
    }

    /**
     * Update dealer information
     * @param {string} dealerId - Dealer ID
     * @param {Object} data - Update data
     * @param {string} data.dealer_name - Dealer name
     * @param {string} data.api_key - API key
     * @param {string} data.api_token - API token
     * @param {string} data.secret_key - Secret key
     * @param {boolean} data.is_active - Active status
     * @returns {Promise} API response with updated dealer
     */
    async updateDealer(dealerId, data) {
        try {
            const response = await ApiService.put(`/v1/admin/dealers/${dealerId}`, data);
            return response.data;
        } catch (error) {
            console.error(`Error updating dealer ${dealerId}:`, error);
            throw error;
        }
    }

    /**
     * Toggle dealer active/inactive status
     * @param {string} dealerId - Dealer ID
     * @param {boolean} isActive - New active status
     * @returns {Promise} API response with updated dealer
     */
    async toggleDealerStatus(dealerId, isActive) {
        try {
            const response = await ApiService.patch(
                `/v1/admin/dealers/${dealerId}/status`,
                { is_active: isActive }
            );
            return response.data;
        } catch (error) {
            console.error(`Error toggling dealer status ${dealerId}:`, error);
            throw error;
        }
    }
}

export default new DealerService();
