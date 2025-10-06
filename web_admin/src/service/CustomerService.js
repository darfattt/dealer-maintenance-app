import api from './ApiService';

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
            const params = new URLSearchParams();
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);

            const queryString = params.toString();
            const url = `/v1/customer/dealer/${dealerId}/stats${queryString ? `?${queryString}` : ''}`;

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching customer stats:', error);
            throw error;
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
            const { page = 1, pageSize = 10, dateFrom = null, dateTo = null } = options;

            const params = new URLSearchParams();
            params.append('page', page.toString());
            params.append('page_size', pageSize.toString());
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);

            const url = `/v1/customer/dealer/${dealerId}/requests?${params.toString()}`;

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching customer requests:', error);
            throw error;
        }
    }

    /**
     * Get a specific customer validation request by ID
     * @param {string} requestId - The request ID
     * @returns {Promise<Object>} Customer request details
     */
    async getRequestById(requestId) {
        try {
            const response = await api.get(`/api/v1/customer/request/${requestId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching customer request:', error);
            throw error;
        }
    }

    /**
     * Test WhatsApp configuration for a dealer
     * @param {string} dealerId - The dealer ID
     * @returns {Promise<Object>} Test result
     */
    async testWhatsAppConfig(dealerId) {
        try {
            const response = await api.post(`/v1/customer/dealer/${dealerId}/test-whatsapp`);
            return response.data;
        } catch (error) {
            console.error('Error testing WhatsApp config:', error);
            throw error;
        }
    }

    // ===== CUSTOMER REMINDER METHODS =====

    /**
     * Get customer reminder statistics for a dealer
     * @param {string} dateFrom - Start date in YYYY-MM-DD format
     * @param {string} dateTo - End date in YYYY-MM-DD format
     * @param {string} dealerId - Dealer ID (optional, SUPER_ADMIN can specify dealer)
     * @param {string} reminderTarget - Reminder target filter (optional)
     * @returns {Promise<Object>} Reminder statistics including sent/failed counts and type breakdown
     */
    async getReminderStats(dateFrom = null, dateTo = null, dealerId = null, reminderTarget = null) {
        try {
            const params = new URLSearchParams();
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);
            if (dealerId) params.append('dealer_id', dealerId);
            if (reminderTarget) params.append('reminder_target', reminderTarget);

            const queryString = params.toString();
            const url = `/v1/reminder/stats${queryString ? `?${queryString}` : ''}`;

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching reminder stats:', error);
            throw error;
        }
    }

    /**
     * Get paginated customer reminder requests for a dealer
     * @param {Object} options - Query options
     * @param {number} options.page - Page number (1-based)
     * @param {number} options.pageSize - Number of items per page
     * @param {string} options.dateFrom - Start date in YYYY-MM-DD format
     * @param {string} options.dateTo - End date in YYYY-MM-DD format
     * @param {string} options.reminderTarget - Filter by reminder target
     * @param {string} options.dealerId - Dealer ID (optional, SUPER_ADMIN can specify dealer)
     * @returns {Promise<Object>} Paginated list of reminder requests
     */
    async getReminderRequests(options = {}) {
        try {
            const { page = 1, pageSize = 10, dateFrom = null, dateTo = null, reminderTarget = null, dealerId = null } = options;

            const params = new URLSearchParams();
            params.append('page', page.toString());
            params.append('page_size', pageSize.toString());
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);
            if (reminderTarget) params.append('reminder_target', reminderTarget);
            if (dealerId) params.append('dealer_id', dealerId);

            const url = `/v1/reminder/reminders?${params.toString()}`;

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching reminder requests:', error);
            throw error;
        }
    }

    /**
     * Get available reminder types
     * @returns {Promise<Object>} List of available reminder types
     */
    async getReminderTypes() {
        try {
            const response = await api.get('/v1/reminder/types');
            return response.data;
        } catch (error) {
            console.error('Error fetching reminder types:', error);
            throw error;
        }
    }

    /**
     * Get a specific customer reminder request by ID
     * @param {string} reminderId - The reminder ID
     * @returns {Promise<Object>} Reminder request details
     */
    async getReminderById(reminderId) {
        try {
            const response = await api.get(`/v1/reminder/${reminderId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching reminder request:', error);
            throw error;
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
            const response = await api.post('/v1/reminder/create', reminderData);
            return response.data;
        } catch (error) {
            console.error('Error creating reminder:', error);
            throw error;
        }
    }

    /**
     * Get available reminder targets for dropdown
     * @returns {Promise<Object>} Reminder targets response
     */
    async getReminderTargets() {
        try {
            const response = await api.get('/v1/reminder/targets');
            return response.data;
        } catch (error) {
            console.error('Error fetching reminder targets:', error);
            // Return fallback data to prevent frontend crashes
            return {
                success: false,
                data: [
                    { label: 'All Targets', value: '' },
                    { label: 'KPB 1', value: 'KPB-1' },
                    { label: 'KPB 2', value: 'KPB-2' },
                    { label: 'KPB 3', value: 'KPB-3' },
                    { label: 'KPB 4', value: 'KPB-4' },
                    { label: 'Non KPB', value: 'Non KPB' },
                    { label: 'Booking Service', value: 'Booking Service' },
                    { label: 'Ultah Konsumen', value: 'Ultah Konsumen' }
                ]
            };
        }
    }

    /**
     * Test WhatsApp configuration for reminder sending for authenticated dealer
     * @returns {Promise<Object>} Test result
     */
    async testReminderWhatsAppConfig() {
        try {
            const response = await api.post('/v1/reminder/test-whatsapp');
            return response.data;
        } catch (error) {
            console.error('Error testing reminder WhatsApp config:', error);
            throw error;
        }
    }

    /**
     * Get reminder type and WhatsApp status cross-tabulation statistics
     * @param {string} dateFrom - Start date in YYYY-MM-DD format
     * @param {string} dateTo - End date in YYYY-MM-DD format
     * @param {string} dealerId - Dealer ID (optional, SUPER_ADMIN can specify dealer)
     * @param {string} reminderTarget - Reminder target filter (optional)
     * @returns {Promise<Object>} Cross-tabulation statistics grouped by reminder_type and whatsapp_status
     */
    async getReminderTypeWhatsAppStatusStats(dateFrom = null, dateTo = null, dealerId = null, reminderTarget = null) {
        try {
            const params = new URLSearchParams();
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);
            if (dealerId) params.append('dealer_id', dealerId);
            if (reminderTarget) params.append('reminder_target', reminderTarget);

            const queryString = params.toString();
            const url = `/v1/reminder/reminder-type-whatsapp-status-stats${queryString ? `?${queryString}` : ''}`;

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching reminder type whatsapp status stats:', error);
            throw error;
        }
    }

    /**
     * Get vehicle type statistics
     * @param {string} dateFrom - Start date in YYYY-MM-DD format
     * @param {string} dateTo - End date in YYYY-MM-DD format
     * @param {string} dealerId - Dealer ID (optional, SUPER_ADMIN can specify dealer)
     * @param {string} reminderTarget - Reminder target filter (optional)
     * @returns {Promise<Object>} Statistics grouped by tipe_unit (vehicle type)
     */
    async getTipeUnitStats(dateFrom = null, dateTo = null, dealerId = null, reminderTarget = null) {
        try {
            const params = new URLSearchParams();
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);
            if (dealerId) params.append('dealer_id', dealerId);
            if (reminderTarget) params.append('reminder_target', reminderTarget);

            const queryString = params.toString();
            const url = `/v1/reminder/tipe-unit-stats${queryString ? `?${queryString}` : ''}`;

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching tipe unit stats:', error);
            throw error;
        }
    }

    // ===== CUSTOMER SATISFACTION METHODS =====

    /**
     * Get customer satisfaction records with filtering and pagination
     * @param {Object} options - Query options
     * @param {string} options.periode_utk_suspend - Filter by periode untuk suspend
     * @param {string} options.submit_review_date - Filter by submit review date
     * @param {string} options.no_ahass - Filter by No AHASS
     * @param {string} options.date_from - Start date in YYYY-MM-DD format
     * @param {string} options.date_to - End date in YYYY-MM-DD format
     * @param {number} options.page - Page number (1-based)
     * @param {number} options.page_size - Number of items per page
     * @returns {Promise<Object>} Paginated satisfaction records
     */
    async getCustomerSatisfactionRecords(options = {}) {
        try {
            const { periode_utk_suspend = null, submit_review_date = null, no_ahass = null, date_from = null, date_to = null, page = 1, page_size = 10 } = options;

            const params = new URLSearchParams();
            params.append('page', page.toString());
            params.append('page_size', page_size.toString());
            if (periode_utk_suspend) params.append('periode_utk_suspend', periode_utk_suspend);
            if (submit_review_date) params.append('submit_review_date', submit_review_date);
            if (no_ahass) params.append('no_ahass', no_ahass);
            if (date_from) params.append('date_from', date_from);
            if (date_to) params.append('date_to', date_to);

            const url = `/v1/customer-satisfaction/records?${params.toString()}`;

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching customer satisfaction records:', error);
            throw error;
        }
    }

    /**
     * Get customer satisfaction statistics
     * @param {Object} options - Filter options
     * @param {string} options.periode_utk_suspend - Filter by periode untuk suspend
     * @param {string} options.submit_review_date - Filter by submit review date
     * @param {string} options.no_ahass - Filter by No AHASS
     * @param {string} options.date_from - Start date in YYYY-MM-DD format
     * @param {string} options.date_to - End date in YYYY-MM-DD format
     * @returns {Promise<Object>} Statistics data
     */
    async getCustomerSatisfactionStatistics(options = {}) {
        try {
            const { periode_utk_suspend = null, submit_review_date = null, no_ahass = null, date_from = null, date_to = null } = options;

            const params = new URLSearchParams();
            if (periode_utk_suspend) params.append('periode_utk_suspend', periode_utk_suspend);
            if (submit_review_date) params.append('submit_review_date', submit_review_date);
            if (no_ahass) params.append('no_ahass', no_ahass);
            if (date_from) params.append('date_from', date_from);
            if (date_to) params.append('date_to', date_to);

            const queryString = params.toString();
            const url = `/v1/customer-satisfaction/statistics${queryString ? `?${queryString}` : ''}`;

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching customer satisfaction statistics:', error);
            throw error;
        }
    }

    /**
     * Upload customer satisfaction file (Excel or CSV)
     * @param {File} file - The file to upload
     * @param {boolean} overrideExisting - Whether to override existing records with same no_tiket
     * @param {boolean} reformatDates - Whether to reformat tanggal_rating to Indonesian format
     * @returns {Promise<Object>} Upload result
     */
    async uploadCustomerSatisfactionFile(file, overrideExisting = false, reformatDates = false) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('override_existing', overrideExisting.toString());
            formData.append('reformat_tanggal_rating', reformatDates.toString());

            const response = await api.post('/v1/customer-satisfaction/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            return response.data;
        } catch (error) {
            console.error('Error uploading customer satisfaction file:', error);
            throw error;
        }
    }

    /**
     * Get customer satisfaction upload trackers
     * @param {Object} options - Query options
     * @param {number} options.page - Page number (1-based)
     * @param {number} options.page_size - Number of items per page
     * @param {string} options.status - Filter by upload status
     * @returns {Promise<Object>} Paginated upload trackers
     */
    async getCustomerSatisfactionUploadTrackers(options = {}) {
        try {
            const { page = 1, page_size = 10, status = null } = options;

            const params = new URLSearchParams();
            params.append('page', page.toString());
            params.append('page_size', page_size.toString());
            if (status) params.append('status', status);

            const url = `/v1/customer-satisfaction/uploads?${params.toString()}`;

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching upload trackers:', error);
            throw error;
        }
    }

    /**
     * Get upload tracker by ID
     * @param {string} trackerId - Upload tracker ID
     * @returns {Promise<Object>} Upload tracker details
     */
    async getCustomerSatisfactionUploadTracker(trackerId) {
        try {
            const response = await api.get(`/v1/customer-satisfaction/uploads/${trackerId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching upload tracker:', error);
            throw error;
        }
    }

    /**
     * Get latest upload information for quick display
     * @returns {Promise<Object>} Latest upload information
     */
    async getLatestUploadInfo() {
        try {
            const response = await api.get('/v1/customer-satisfaction/uploads/latest');
            return response.data;
        } catch (error) {
            console.error('Error fetching latest upload info:', error);
            throw error;
        }
    }

    /**
     * Get latest upload information (simplified - by created_date only)
     * @returns {Promise<Object>} Latest upload date information
     */
    async getLatestUploadInfoSimple() {
        try {
            const response = await api.get('/v1/customer-satisfaction/latest-upload-simple');
            return response.data;
        } catch (error) {
            console.error('Error fetching latest upload info simple:', error);
            throw error;
        }
    }

    /**
     * Get top indikasi keluhan (complaint indicators) with filtering
     * @param {Object} options - Filter options
     * @param {string} options.periode_utk_suspend - Filter by periode untuk suspend
     * @param {string} options.submit_review_date - Filter by submit review date
     * @param {string} options.no_ahass - Filter by No AHASS
     * @param {string} options.date_from - Start date in YYYY-MM-DD format
     * @param {string} options.date_to - End date in YYYY-MM-DD format
     * @param {number} options.limit - Number of top complaints to return (default 3)
     * @returns {Promise<Object>} Top complaint indicators with counts and percentages
     */
    async getTopIndikasiKeluhan(options = {}) {
        try {
            const { periode_utk_suspend = null, submit_review_date = null, no_ahass = null, date_from = null, date_to = null, limit = 3 } = options;

            const params = new URLSearchParams();
            if (periode_utk_suspend) params.append('periode_utk_suspend', periode_utk_suspend);
            if (submit_review_date) params.append('submit_review_date', submit_review_date);
            if (no_ahass) params.append('no_ahass', no_ahass);
            if (date_from) params.append('date_from', date_from);
            if (date_to) params.append('date_to', date_to);
            params.append('limit', limit.toString());

            const queryString = params.toString();
            const url = `/v1/customer-satisfaction/top-complaints${queryString ? `?${queryString}` : ''}`;

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching top indikasi keluhan:', error);
            throw error;
        }
    }

    /**
     * Get overall customer satisfaction rating with period comparison
     * @param {Object} options - Filter options
     * @param {string} options.periode_utk_suspend - Filter by periode untuk suspend
     * @param {string} options.submit_review_date - Filter by submit review date
     * @param {string} options.no_ahass - Filter by No AHASS
     * @param {string} options.date_from - Start date in YYYY-MM-DD format (uses tanggal_rating field)
     * @param {string} options.date_to - End date in YYYY-MM-DD format (uses tanggal_rating field)
     * @param {boolean} options.compare_previous_period - Whether to compare with previous period (default true)
     * @returns {Promise<Object>} Overall rating with comparison data
     */
    async getOverallRating(options = {}) {
        try {
            const { periode_utk_suspend = null, submit_review_date = null, no_ahass = null, date_from = null, date_to = null, compare_previous_period = true } = options;

            const params = new URLSearchParams();
            if (periode_utk_suspend) params.append('periode_utk_suspend', periode_utk_suspend);
            if (submit_review_date) params.append('submit_review_date', submit_review_date);
            if (no_ahass) params.append('no_ahass', no_ahass);
            if (date_from) params.append('date_from', date_from);
            if (date_to) params.append('date_to', date_to);
            params.append('compare_previous_period', compare_previous_period.toString());

            const queryString = params.toString();
            const url = `/v1/customer-satisfaction/overall-rating${queryString ? `?${queryString}` : ''}`;

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching overall rating:', error);
            throw error;
        }
    }

    /**
     * Get sentiment analysis statistics for customer satisfaction
     * @param {Object} options - Filter options
     * @param {string} options.periode_utk_suspend - Filter by periode untuk suspend
     * @param {string} options.submit_review_date - Filter by submit review date
     * @param {string} options.no_ahass - Filter by No AHASS
     * @param {string} options.date_from - Start date in YYYY-MM-DD format
     * @param {string} options.date_to - End date in YYYY-MM-DD format
     * @returns {Promise<Object>} Sentiment analysis statistics with distribution data
     */
    async getSentimentStatistics(options = {}) {
        try {
            const { periode_utk_suspend = null, submit_review_date = null, no_ahass = null, date_from = null, date_to = null } = options;

            const params = new URLSearchParams();
            if (periode_utk_suspend) params.append('periode_utk_suspend', periode_utk_suspend);
            if (submit_review_date) params.append('submit_review_date', submit_review_date);
            if (no_ahass) params.append('no_ahass', no_ahass);
            if (date_from) params.append('date_from', date_from);
            if (date_to) params.append('date_to', date_to);

            const queryString = params.toString();
            const url = `/v1/customer-satisfaction/sentiment-analysis/statistics${queryString ? `?${queryString}` : ''}`;

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching sentiment statistics:', error);
            throw error;
        }
    }

    /**
     * Get sentiment themes statistics for customer satisfaction data
     * @param {Object} options - Filter options
     * @param {string} options.dealerId - Dealer ID
     * @param {string} options.dateFrom - Start date in YYYY-MM-DD format
     * @param {string} options.dateTo - End date in YYYY-MM-DD format
     * @param {string} options.periode_utk_suspend - Filter by periode untuk suspend
     * @param {string} options.submit_review_date - Filter by submit review date
     * @param {string} options.no_ahass - Filter by No AHASS
     * @returns {Promise<Object>} Sentiment themes statistics with count and percentage data
     */
    async getSentimentThemesStatistics(options = {}) {
        try {
            const { dealerId = null, dateFrom = null, dateTo = null, periode_utk_suspend = null, submit_review_date = null, no_ahass = null } = options;

            const params = new URLSearchParams();
            if (dealerId) params.append('dealer_id', dealerId);
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);
            if (periode_utk_suspend) params.append('periode_utk_suspend', periode_utk_suspend);
            if (submit_review_date) params.append('submit_review_date', submit_review_date);
            if (no_ahass) params.append('no_ahass', no_ahass);

            const queryString = params.toString();
            const url = `/v1/customer-satisfaction/sentiment-themes/statistics${queryString ? `?${queryString}` : ''}`;

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching sentiment themes statistics:', error);
            throw error;
        }
    }

    /**
     * Process sentiment analysis for customer satisfaction records synchronously
     * @param {Object} options - Analysis options
     * @param {number} options.limit - Maximum number of records to analyze (1-100)
     * @param {string} options.upload_batch_id - Optional filter by upload batch ID
     * @returns {Promise<Object>} Sentiment analysis results (immediate processing)
     */
    async processSentimentAnalysisSync(options = {}) {
        try {
            const {
                limit = 50,
                upload_batch_id = null
            } = options;

            const params = new URLSearchParams();
            params.append('limit', limit.toString());
            if (upload_batch_id) {
                params.append('upload_batch_id', upload_batch_id);
            }

            const response = await api.post(`/v1/customer-satisfaction/sentiment-analysis/process-sync?${params.toString()}`);
            return response.data;
        } catch (error) {
            console.error('Error processing sentiment analysis (sync):', error);
            throw error;
        }
    }

    /**
     * Get all active dealers for dropdown options
     * @returns {Promise<Object>} Active dealers list with formatted labels
     */
    async getActiveDealers() {
        try {
            const response = await api.get('/v1/admin/dealers/active');
            return response.data;
        } catch (error) {
            console.error('Error fetching active dealers:', error);
            throw error;
        }
    }
}

export default new CustomerService();
