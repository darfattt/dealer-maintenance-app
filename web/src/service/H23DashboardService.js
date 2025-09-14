import api from './ApiService';

export class H23DashboardService {
    /**
     * Get total unit entry statistics for work orders
     * @param {string} dealerId - The dealer ID
     * @param {string} dateFrom - Start date in YYYY-MM-DD format
     * @param {string} dateTo - End date in YYYY-MM-DD format
     * @returns {Promise<Object>} Unit entry statistics including count and trend data
     */
    async getTotalUnitEntry(dealerId, dateFrom, dateTo) {
        try {
            const params = new URLSearchParams();
            if (dealerId) params.append('dealer_id', dealerId);
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);

            const url = `/v1/h23-dashboard/work-order/total-unit-entry?${params.toString()}`;
            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching total unit entry data:', error);
            throw error;
        }
    }

    /**
     * Get work order revenue statistics
     * @param {string} dealerId - The dealer ID
     * @param {string} dateFrom - Start date in YYYY-MM-DD format
     * @param {string} dateTo - End date in YYYY-MM-DD format
     * @returns {Promise<Object>} Revenue statistics including total revenue and records count
     */
    async getWorkOrderRevenue(dealerId, dateFrom, dateTo) {
        try {
            const params = new URLSearchParams();
            if (dealerId) params.append('dealer_id', dealerId);
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);

            const url = `/v1/h23-dashboard/work-order/revenue?${params.toString()}`;
            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching work order revenue data:', error);
            throw error;
        }
    }

    /**
     * Get work order status counts for chart display
     * @param {string} dealerId - The dealer ID
     * @param {string} dateFrom - Start date in YYYY-MM-DD format
     * @param {string} dateTo - End date in YYYY-MM-DD format
     * @returns {Promise<Object>} Status count data grouped by status labels
     */
    async getWorkOrderStatusCounts(dealerId, dateFrom, dateTo) {
        try {
            const params = new URLSearchParams();
            if (dealerId) params.append('dealer_id', dealerId);
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);

            const url = `/v1/h23-dashboard/work-order/status-counts?${params.toString()}`;
            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching work order status counts:', error);
            throw error;
        }
    }

    /**
     * Get NJB (Nota Jasa Bengkel) payment statistics
     * @param {string} dealerId - The dealer ID
     * @param {string} dateFrom - Start date in YYYY-MM-DD format
     * @param {string} dateTo - End date in YYYY-MM-DD format
     * @returns {Promise<Object>} NJB statistics including total amount and records count
     */
    async getNJBStatistics(dealerId, dateFrom, dateTo) {
        try {
            const params = new URLSearchParams();
            if (dealerId) params.append('dealer_id', dealerId);
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);

            const url = `/v1/h23-dashboard/pembayaran/njb-statistics?${params.toString()}`;
            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching NJB statistics:', error);
            throw error;
        }
    }

    /**
     * Get NSC (Nota Suku Cadang) payment statistics
     * @param {string} dealerId - The dealer ID
     * @param {string} dateFrom - Start date in YYYY-MM-DD format
     * @param {string} dateTo - End date in YYYY-MM-DD format
     * @returns {Promise<Object>} NSC statistics including total amount and records count
     */
    async getNSCStatistics(dealerId, dateFrom, dateTo) {
        try {
            const params = new URLSearchParams();
            if (dealerId) params.append('dealer_id', dealerId);
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);

            const url = `/v1/h23-dashboard/pembayaran/nsc-statistics?${params.toString()}`;
            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching NSC statistics:', error);
            throw error;
        }
    }

    /**
     * Get HLO (Harga Laim Order) payment statistics
     * @param {string} dealerId - The dealer ID
     * @param {string} dateFrom - Start date in YYYY-MM-DD format
     * @param {string} dateTo - End date in YYYY-MM-DD format
     * @returns {Promise<Object>} HLO statistics including document counts, parts, and records
     */
    async getHLOStatistics(dealerId, dateFrom, dateTo) {
        try {
            const params = new URLSearchParams();
            if (dealerId) params.append('dealer_id', dealerId);
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);

            const url = `/v1/h23-dashboard/pembayaran/hlo-statistics?${params.toString()}`;
            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching HLO statistics:', error);
            throw error;
        }
    }
}

export default new H23DashboardService();
