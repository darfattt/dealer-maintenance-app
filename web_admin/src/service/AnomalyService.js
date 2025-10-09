import api from './ApiService';

/**
 * Anomaly Service - API calls for integration anomalies
 * Handles WhatsApp failures and Google Scrape failures
 */
class AnomalyService {
    /**
     * Get WhatsApp integration anomalies with pagination and filters
     * @param {number} page - Page number (1-based)
     * @param {number} perPage - Items per page
     * @param {Object} filters - Filter parameters
     * @param {string} filters.dealer_id - Dealer ID filter
     * @param {string} filters.date_from - Start date filter (YYYY-MM-DD)
     * @param {string} filters.date_to - End date filter (YYYY-MM-DD)
     * @param {string} filters.whatsapp_status - WhatsApp status filter
     * @param {string} filters.request_type - Request type filter (VALIDATION/REMINDER/ALL)
     * @returns {Promise} Response with paginated WhatsApp anomalies
     */
    async getWhatsAppAnomalies(page = 1, perPage = 50, filters = {}) {
        try {
            const params = {
                page,
                per_page: perPage,
                ...filters
            };

            // Remove undefined/null values
            Object.keys(params).forEach(key => {
                if (params[key] === undefined || params[key] === null || params[key] === '') {
                    delete params[key];
                }
            });

            const response = await api.get('/v1/whatsapp-anomalies', { params });
            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            console.error('Error fetching WhatsApp anomalies:', error);
            return {
                success: false,
                message: error.response?.data?.detail || 'Failed to fetch WhatsApp anomalies',
                error
            };
        }
    }

    /**
     * Get WhatsApp anomaly summary statistics
     * @param {Object} filters - Filter parameters
     * @param {string} filters.dealer_id - Dealer ID filter
     * @param {string} filters.date_from - Start date filter (YYYY-MM-DD)
     * @param {string} filters.date_to - End date filter (YYYY-MM-DD)
     * @returns {Promise} Response with WhatsApp anomaly summary
     */
    async getWhatsAppAnomalySummary(filters = {}) {
        try {
            const params = { ...filters };

            // Remove undefined/null values
            Object.keys(params).forEach(key => {
                if (params[key] === undefined || params[key] === null || params[key] === '') {
                    delete params[key];
                }
            });

            const response = await api.get('/v1/whatsapp-anomalies/summary', { params });
            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            console.error('Error fetching WhatsApp anomaly summary:', error);
            return {
                success: false,
                message: error.response?.data?.detail || 'Failed to fetch WhatsApp anomaly summary',
                error
            };
        }
    }

    /**
     * Get Google scrape anomalies with pagination and filters
     * @param {number} page - Page number (1-based)
     * @param {number} perPage - Items per page
     * @param {Object} filters - Filter parameters
     * @param {string} filters.dealer_id - Dealer ID filter
     * @param {string} filters.date_from - Start date filter (YYYY-MM-DD)
     * @param {string} filters.date_to - End date filter (YYYY-MM-DD)
     * @param {string} filters.scrape_status - Scrape status filter (FAILED/PARTIAL)
     * @returns {Promise} Response with paginated Google scrape anomalies
     */
    async getGoogleScrapeAnomalies(page = 1, perPage = 50, filters = {}) {
        try {
            const params = {
                page,
                per_page: perPage,
                ...filters
            };

            // Remove undefined/null values
            Object.keys(params).forEach(key => {
                if (params[key] === undefined || params[key] === null || params[key] === '') {
                    delete params[key];
                }
            });

            const response = await api.get('/v1/google-scrape-anomalies', { params });
            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            console.error('Error fetching Google scrape anomalies:', error);
            return {
                success: false,
                message: error.response?.data?.detail || 'Failed to fetch Google scrape anomalies',
                error
            };
        }
    }

    /**
     * Get Google scrape anomaly summary statistics
     * @param {Object} filters - Filter parameters
     * @param {string} filters.dealer_id - Dealer ID filter
     * @param {string} filters.date_from - Start date filter (YYYY-MM-DD)
     * @param {string} filters.date_to - End date filter (YYYY-MM-DD)
     * @returns {Promise} Response with Google scrape anomaly summary
     */
    async getGoogleScrapeAnomalySummary(filters = {}) {
        try {
            const params = { ...filters };

            // Remove undefined/null values
            Object.keys(params).forEach(key => {
                if (params[key] === undefined || params[key] === null || params[key] === '') {
                    delete params[key];
                }
            });

            const response = await api.get('/v1/google-scrape-anomalies/summary', { params });
            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            console.error('Error fetching Google scrape anomaly summary:', error);
            return {
                success: false,
                message: error.response?.data?.detail || 'Failed to fetch Google scrape anomaly summary',
                error
            };
        }
    }
}

export default new AnomalyService();
