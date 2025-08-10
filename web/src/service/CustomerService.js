import api from './ApiService'

export class CustomerService {
    /**
     * Get customer validation statistics for a dealer
     * @param {string} dealerId - The dealer ID
     * @param {string} dateFrom - Start date in YYYY-MM-DD format
     * @param {string} dateTo - End date in YYYY-MM-DD format
     * @returns {Promise<Object>} Statistics data including delivered/failed counts and percentages
     */
    async getCustomerStats(dealerId, dateFrom = null, dateTo = null) {
        try {
            const params = new URLSearchParams()
            if (dateFrom) params.append('date_from', dateFrom)
            if (dateTo) params.append('date_to', dateTo)
            
            const queryString = params.toString()
            const url = `/api/v1/customer/dealer/${dealerId}/stats${queryString ? `?${queryString}` : ''}`
            
            const response = await api.get(url)
            return response.data
        } catch (error) {
            console.error('Error fetching customer stats:', error)
            throw error
        }
    }

    /**
     * Get paginated customer validation requests for a dealer
     * @param {string} dealerId - The dealer ID
     * @param {Object} options - Query options
     * @param {number} options.page - Page number (1-based)
     * @param {number} options.pageSize - Number of items per page
     * @param {string} options.dateFrom - Start date in YYYY-MM-DD format
     * @param {string} options.dateTo - End date in YYYY-MM-DD format
     * @returns {Promise<Object>} Paginated list of customer requests
     */
    async getCustomerRequests(dealerId, options = {}) {
        try {
            const {
                page = 1,
                pageSize = 10,
                dateFrom = null,
                dateTo = null
            } = options

            const params = new URLSearchParams()
            params.append('page', page.toString())
            params.append('page_size', pageSize.toString())
            if (dateFrom) params.append('date_from', dateFrom)
            if (dateTo) params.append('date_to', dateTo)
            
            const url = `/api/v1/customer/dealer/${dealerId}/requests?${params.toString()}`
            
            const response = await api.get(url)
            return response.data
        } catch (error) {
            console.error('Error fetching customer requests:', error)
            throw error
        }
    }

    /**
     * Get a specific customer validation request by ID
     * @param {string} requestId - The request ID
     * @returns {Promise<Object>} Customer request details
     */
    async getRequestById(requestId) {
        try {
            const response = await api.get(`/customer/request/${requestId}`)
            return response.data
        } catch (error) {
            console.error('Error fetching customer request:', error)
            throw error
        }
    }

    /**
     * Test WhatsApp configuration for a dealer
     * @param {string} dealerId - The dealer ID
     * @returns {Promise<Object>} Test result
     */
    async testWhatsAppConfig(dealerId) {
        try {
            const response = await api.post(`/customer/dealer/${dealerId}/test-whatsapp`)
            return response.data
        } catch (error) {
            console.error('Error testing WhatsApp config:', error)
            throw error
        }
    }
}

export default new CustomerService()