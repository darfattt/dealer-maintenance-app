import api from './ApiService';

/**
 * Service for dealer-related API calls
 */
class DealerService {
    /**
     * Get dealer by ID
     * @param {string} dealerId - The dealer ID
     * @returns {Promise<Object>} Dealer information
     */
    async getDealerById(dealerId) {
        try {
            const response = await api.get(`/v1/admin/dealers/${dealerId}`);
            return response.data.data; // Returns dealer object with dealer_name, dealer_id, etc.
        } catch (error) {
            console.error('Error fetching dealer by ID:', error);
            throw error;
        }
    }

    /**
     * Get list of all dealers
     * @param {Object} params - Query parameters (page, page_size, search, is_active)
     * @returns {Promise<Object>} List of dealers with pagination
     */
    async getDealers(params = {}) {
        try {
            const response = await api.get('/v1/admin/dealers', { params });
            return response.data;
        } catch (error) {
            console.error('Error fetching dealers:', error);
            throw error;
        }
    }

    /**
     * Update dealer information
     * @param {string} dealerId - The dealer ID
     * @param {Object} dealerData - Updated dealer data
     * @returns {Promise<Object>} Updated dealer information
     */
    async updateDealer(dealerId, dealerData) {
        try {
            const response = await api.put(`/v1/admin/dealers/${dealerId}`, dealerData);
            return response.data;
        } catch (error) {
            console.error('Error updating dealer:', error);
            throw error;
        }
    }

    /**
     * Update dealer status (active/inactive)
     * @param {string} dealerId - The dealer ID
     * @param {boolean} isActive - Active status
     * @returns {Promise<Object>} Updated dealer status
     */
    async updateDealerStatus(dealerId, isActive) {
        try {
            const response = await api.patch(`/v1/admin/dealers/${dealerId}/status`, { is_active: isActive });
            return response.data;
        } catch (error) {
            console.error('Error updating dealer status:', error);
            throw error;
        }
    }
}

export default new DealerService();
