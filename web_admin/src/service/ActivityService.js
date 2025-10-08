import api from './ApiService';

/**
 * Activity Service - API calls for system activity logs
 */
class ActivityService {
    /**
     * Get today's login activities from Account Service
     * @returns {Promise} Response with login activities
     */
    async getLoginActivities() {
        try {
            const response = await api.get('/v1/audit/login-activities/today');
            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            console.error('Error fetching login activities:', error);
            return {
                success: false,
                message: error.response?.data?.detail || 'Failed to fetch login activities',
                error
            };
        }
    }

    /**
     * Get today's API request logs from Customer Service
     * @returns {Promise} Response with API logs
     */
    async getApiLogs() {
        try {
            const response = await api.get('/v1/api-logs/today');
            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            console.error('Error fetching API logs:', error);
            return {
                success: false,
                message: error.response?.data?.detail || 'Failed to fetch API logs',
                error
            };
        }
    }

    /**
     * Get today's Google Review scrape activities from Customer Service
     * @returns {Promise} Response with Google Review activities
     */
    async getGoogleReviewActivities() {
        try {
            const response = await api.get('/v1/trackers/google-reviews/today');
            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            console.error('Error fetching Google Review activities:', error);
            return {
                success: false,
                message: error.response?.data?.detail || 'Failed to fetch Google Review activities',
                error
            };
        }
    }

    /**
     * Get today's Customer Satisfaction upload trackers from Customer Service
     * @returns {Promise} Response with upload trackers
     */
    async getCustomerSatisfactionUploads() {
        try {
            const response = await api.get('/v1/trackers/customer-satisfaction/today');
            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            console.error('Error fetching Customer Satisfaction uploads:', error);
            return {
                success: false,
                message: error.response?.data?.detail || 'Failed to fetch Customer Satisfaction uploads',
                error
            };
        }
    }
}

export default new ActivityService();
