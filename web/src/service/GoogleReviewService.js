import api from './ApiService';

export class GoogleReviewService {
    /**
     * Get paginated Google reviews for a dealer with filtering
     * @param {string} dealerId - The dealer ID
     * @param {Object} options - Query options
     * @param {number} options.page - Page number (1-based)
     * @param {number} options.per_page - Number of items per page
     * @param {string} options.published_from - Start date in ISO format
     * @param {string} options.published_to - End date in ISO format
     * @param {string} options.reviewer_name - Filter by reviewer name (partial match)
     * @param {string} options.text_search - Search in review text
     * @param {number} options.stars - Filter by star rating (1-5)
     * @param {string} options.sort_by - Field to sort by
     * @param {string} options.sort_order - Sort order (asc/desc)
     * @returns {Promise<Object>} Paginated review details
     */
    async getReviewsForDealer(dealerId, options = {}) {
        try {
            const {
                page = 1,
                per_page = 10,
                published_from = null,
                published_to = null,
                reviewer_name = null,
                text_search = null,
                stars = null,
                sort_by = 'published_date',
                sort_order = 'desc'
            } = options;

            const params = new URLSearchParams();
            params.append('page', page.toString());
            params.append('per_page', per_page.toString());
            params.append('sort_by', sort_by);
            params.append('sort_order', sort_order);

            if (published_from) params.append('published_from', published_from);
            if (published_to) params.append('published_to', published_to);
            if (reviewer_name) params.append('reviewer_name', reviewer_name);
            if (text_search) params.append('text_search', text_search);
            if (stars) params.append('stars', stars.toString());

            const response = await api.get(`/v1/google-reviews/reviews/${dealerId}?${params.toString()}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching Google reviews:', error);
            throw error;
        }
    }

    /**
     * Get review statistics for a dealer
     * @param {string} dealerId - The dealer ID
     * @returns {Promise<Object>} Review statistics including business info and counts
     */
    async getReviewStatistics(dealerId) {
        try {
            const response = await api.get(`/v1/google-reviews/statistics/${dealerId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching review statistics:', error);
            throw error;
        }
    }

    /**
     * Get sentiment analysis statistics for a dealer
     * @param {string} dealerId - The dealer ID
     * @returns {Promise<Object>} Sentiment statistics with distribution and averages
     */
    async getSentimentStatistics(dealerId) {
        try {
            const response = await api.get(`/v1/google-reviews/sentiment-statistics/${dealerId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching sentiment statistics:', error);
            throw error;
        }
    }

    /**
     * Get recent reviews for a dealer
     * @param {string} dealerId - The dealer ID
     * @param {number} limit - Number of recent reviews to return (default: 5, max: 20)
     * @returns {Promise<Object>} Recent reviews data
     */
    async getRecentReviews(dealerId, limit = 5) {
        try {
            const params = new URLSearchParams();
            params.append('limit', limit.toString());

            const response = await api.get(`/v1/google-reviews/recent/${dealerId}?${params.toString()}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching recent reviews:', error);
            throw error;
        }
    }

    /**
     * Scrape Google Reviews for a dealer
     * @param {Object} options - Scraping options
     * @param {string} options.dealer_id - The dealer ID
     * @param {number} options.max_reviews - Maximum number of reviews to fetch (1-50)
     * @param {string} options.language - Language code for reviews (e.g., 'id', 'en')
     * @param {boolean} options.auto_analyze_sentiment - Auto analyze sentiment after scraping
     * @returns {Promise<Object>} Scraping results
     */
    async scrapeReviews(options = {}) {
        try {
            const {
                dealer_id,
                max_reviews = 10,
                language = 'id',
                auto_analyze_sentiment = true
            } = options;

            const requestData = {
                dealer_id,
                max_reviews,
                language,
                auto_analyze_sentiment
            };

            const response = await api.post('/v1/google-reviews/scrape-reviews', requestData);
            return response.data;
        } catch (error) {
            console.error('Error scraping Google reviews:', error);
            throw error;
        }
    }

    /**
     * Analyze sentiment for Google Reviews
     * @param {Object} options - Analysis options
     * @param {string} options.dealer_id - The dealer ID
     * @param {number} options.limit - Maximum number of reviews to analyze (1-200)
     * @param {number} options.batch_size - Size of processing batches (1-50)
     * @returns {Promise<Object>} Sentiment analysis results
     */
    async analyzeSentiment(options = {}) {
        try {
            const {
                dealer_id,
                limit = 50,
                batch_size = 10
            } = options;

            const requestData = {
                dealer_id,
                limit,
                batch_size
            };

            const response = await api.post('/v1/google-reviews/analyze-sentiment', requestData);
            return response.data;
        } catch (error) {
            console.error('Error analyzing review sentiment:', error);
            throw error;
        }
    }

    /**
     * Legacy method for backward compatibility
     * @deprecated Use analyzeSentiment instead
     */
    async analyzeReviewsSentiment(dealerId, options = {}) {
        return this.analyzeSentiment({
            dealer_id: dealerId,
            ...options
        });
    }

    /**
     * Check if dealer has Google Reviews data
     * @param {string} dealerId - The dealer ID
     * @returns {Promise<Object>} Data availability status
     */
    async checkDealerHasReviews(dealerId) {
        try {
            const response = await api.get(`/v1/google-reviews/dealers/${dealerId}/has-reviews`);
            return response.data;
        } catch (error) {
            console.error('Error checking dealer reviews:', error);
            throw error;
        }
    }

    /**
     * Get Google Review service health status
     * @returns {Promise<Object>} Health status
     */
    async getHealthStatus() {
        try {
            const response = await api.get('/v1/google-reviews/health');
            return response.data;
        } catch (error) {
            console.error('Error getting health status:', error);
            throw error;
        }
    }

    /**
     * Get Google Business Profile for a dealer
     * @param {string} dealerId - The dealer ID
     * @returns {Promise<Object>} Complete business profile data
     */
    async getDealerProfile(dealerId) {
        try {
            const response = await api.get(`/v1/google-reviews/profile/${dealerId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching dealer profile:', error);
            throw error;
        }
    }

    /**
     * Get monthly review totals for current year using optimized backend API
     * @param {string} dealerId - The dealer ID
     * @param {number} year - Year to get data for (default: current year)
     * @returns {Promise<Object>} Monthly review totals from Jan to Dec
     */
    async getMonthlyReviewTotals(dealerId, year = null) {
        try {
            const params = new URLSearchParams();
            if (year) {
                params.append('year', year.toString());
            }

            const response = await api.get(`/v1/google-reviews/monthly-totals/${dealerId}?${params.toString()}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching monthly review totals:', error);
            throw error;
        }
    }

    /**
     * Get scraping history with pagination
     * @param {Object} options - Query options
     * @param {string} options.dealer_id - Optional dealer ID to filter by
     * @param {number} options.page - Page number (1-based)
     * @param {number} options.per_page - Items per page
     * @returns {Promise<Object>} Scraping history data
     */
    async getScrapeHistory(options = {}) {
        try {
            const {
                dealer_id = null,
                page = 1,
                per_page = 20
            } = options;

            const params = new URLSearchParams();
            params.append('page', page.toString());
            params.append('per_page', per_page.toString());

            if (dealer_id) {
                params.append('dealer_id', dealer_id);
            }

            const response = await api.get(`/v1/google-reviews/scrape-history?${params.toString()}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching scrape history:', error);
            throw error;
        }
    }

    /**
     * Get list of dealers available for scraping
     * @returns {Promise<Object>} Dealer options data
     */
    async getDealerOptions() {
        try {
            const response = await api.get('/v1/google-reviews/dealer-options');
            return response.data;
        } catch (error) {
            console.error('Error fetching dealer options:', error);
            throw error;
        }
    }

    /**
     * Get latest scrape information for a dealer
     * @param {string} dealerId - The dealer ID
     * @returns {Promise<Object>} Latest scrape info including sentiment analysis progress
     */
    async getLatestScrapeInfo(dealerId) {
        try {
            const response = await api.get(`/v1/google-reviews/dealers/${dealerId}/latest-scrape-info`);
            return response.data;
        } catch (error) {
            console.error('Error fetching latest scrape info:', error);
            throw error;
        }
    }

    /**
     * Get scrape tracker details by tracker ID
     * @param {string} trackerId - The tracker ID
     * @returns {Promise<Object>} Scrape tracker details with progress information
     */
    async getScrapeTracker(trackerId) {
        try {
            const response = await api.get(`/v1/google-reviews/scrape-tracker/${trackerId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching scrape tracker:', error);
            throw error;
        }
    }
}

// Export default instance
export default new GoogleReviewService();