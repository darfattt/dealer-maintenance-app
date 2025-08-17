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

    // ===== CUSTOMER REMINDER METHODS =====

    /**
     * Get customer reminder statistics for the authenticated dealer
     * @param {string} dateFrom - Start date in YYYY-MM-DD format
     * @param {string} dateTo - End date in YYYY-MM-DD format
     * @returns {Promise<Object>} Reminder statistics including sent/failed counts and type breakdown
     */
    async getReminderStats(dateFrom = null, dateTo = null) {
        try {
            const params = new URLSearchParams()
            if (dateFrom) params.append('date_from', dateFrom)
            if (dateTo) params.append('date_to', dateTo)
            
            const queryString = params.toString()
            const url = `/v1/reminder/stats${queryString ? `?${queryString}` : ''}`
            
            const response = await api.get(url)
            return response.data
        } catch (error) {
            console.error('Error fetching reminder stats:', error)
            throw error
        }
    }

    /**
     * Get paginated customer reminder requests for the authenticated dealer
     * @param {Object} options - Query options
     * @param {number} options.page - Page number (1-based)
     * @param {number} options.pageSize - Number of items per page
     * @param {string} options.dateFrom - Start date in YYYY-MM-DD format
     * @param {string} options.dateTo - End date in YYYY-MM-DD format
     * @param {string} options.reminderType - Filter by reminder type
     * @returns {Promise<Object>} Paginated list of reminder requests
     */
    async getReminderRequests(options = {}) {
        try {
            const {
                page = 1,
                pageSize = 10,
                dateFrom = null,
                dateTo = null,
                reminderType = null
            } = options

            const params = new URLSearchParams()
            params.append('page', page.toString())
            params.append('page_size', pageSize.toString())
            if (dateFrom) params.append('date_from', dateFrom)
            if (dateTo) params.append('date_to', dateTo)
            if (reminderType) params.append('reminder_type', reminderType)
            
            const url = `/v1/reminder/reminders?${params.toString()}`
            
            const response = await api.get(url)
            return response.data
        } catch (error) {
            console.error('Error fetching reminder requests:', error)
            throw error
        }
    }

    /**
     * Get available reminder types
     * @returns {Promise<Object>} List of available reminder types
     */
    async getReminderTypes() {
        try {
            const response = await api.get('/v1/reminder/types')
            return response.data
        } catch (error) {
            console.error('Error fetching reminder types:', error)
            throw error
        }
    }

    /**
     * Get a specific customer reminder request by ID
     * @param {string} reminderId - The reminder ID
     * @returns {Promise<Object>} Reminder request details
     */
    async getReminderById(reminderId) {
        try {
            const response = await api.get(`/v1/reminder/${reminderId}`)
            return response.data
        } catch (error) {
            console.error('Error fetching reminder request:', error)
            throw error
        }
    }

    /**
     * Create a new customer reminder request
     * @param {Object} reminderData - The reminder data
     * @param {string} reminderData.customerName - Customer name
     * @param {string} reminderData.noTelp - Phone number
     * @param {string} reminderData.reminderType - Type of reminder
     * @returns {Promise<Object>} Created reminder response
     */
    async createReminder(reminderData) {
        try {
            const response = await api.post('/v1/reminder/create', reminderData)
            return response.data
        } catch (error) {
            console.error('Error creating reminder:', error)
            throw error
        }
    }

    /**
     * Test WhatsApp configuration for reminder sending for authenticated dealer
     * @returns {Promise<Object>} Test result
     */
    async testReminderWhatsAppConfig() {
        try {
            const response = await api.post('/v1/reminder/test-whatsapp')
            return response.data
        } catch (error) {
            console.error('Error testing reminder WhatsApp config:', error)
            throw error
        }
    }
}

export default new CustomerService()