import api from './ApiService';

export class WhatsAppTemplateService {
    /**
     * Get paginated list of WhatsApp templates with optional filtering
     * @param {Object} options - Query options
     * @param {string} options.dealer_id - Filter by dealer ID (empty string for global templates)
     * @param {string} options.reminder_target - Filter by reminder target (exact match)
     * @param {string} options.template - Search in template content (contains, case-insensitive)
     * @param {number} options.page - Page number (1-based, default: 1)
     * @param {number} options.size - Page size (1-100, default: 10)
     * @returns {Promise<Object>} Paginated templates response
     */
    async getTemplates(options = {}) {
        try {
            const { dealer_id = null, reminder_target = null, template = null, page = 1, size = 10 } = options;

            const params = new URLSearchParams();
            if (dealer_id !== null) params.append('dealer_id', dealer_id);
            if (reminder_target) params.append('reminder_target', reminder_target);
            if (template) params.append('template', template);
            params.append('page', page.toString());
            params.append('size', size.toString());

            const url = `/v1/whatsapp-templates?${params.toString()}`;
            const response = await api.get(url);

            return response.data;
        } catch (error) {
            console.error('Error fetching WhatsApp templates:', error);
            throw error;
        }
    }

    /**
     * Update a WhatsApp template by ID
     * @param {string} templateId - Template UUID
     * @param {Object} updateData - Update data
     * @param {string} updateData.template - Template content (required, max 2000 chars)
     * @param {string} updateData.reminder_target - Reminder target (required, max 50 chars)
     * @param {string} updateData.reminder_type - Reminder type (required, max 100 chars)
     * @returns {Promise<Object>} Update response
     */
    async updateTemplate(templateId, updateData) {
        try {
            const url = `/v1/whatsapp-templates/${templateId}`;
            const response = await api.put(url, updateData);

            return response.data;
        } catch (error) {
            console.error('Error updating WhatsApp template:', error);
            throw error;
        }
    }

    /**
     * Delete a WhatsApp template by ID
     * @param {string} templateId - Template UUID
     * @returns {Promise<Object>} Delete response
     */
    async deleteTemplate(templateId) {
        try {
            const url = `/v1/whatsapp-templates/${templateId}`;
            const response = await api.delete(url);

            return response.data;
        } catch (error) {
            console.error('Error deleting WhatsApp template:', error);
            throw error;
        }
    }

    /**
     * Copy templates from source dealer to target dealer
     * @param {Object} copyData - Copy operation data
     * @param {string} copyData.source_dealer_id - Source dealer ID (required, max 50 chars)
     * @param {string} copyData.target_dealer_id - Target dealer ID (required, max 50 chars, must be different from source)
     * @param {boolean} copyData.overwrite_existing - Whether to overwrite existing templates (default: false)
     * @returns {Promise<Object>} Copy operation response
     */
    async copyTemplates(copyData) {
        try {
            const url = `/v1/whatsapp-templates/copy`;
            const response = await api.post(url, copyData);

            return response.data;
        } catch (error) {
            console.error('Error copying WhatsApp templates:', error);
            throw error;
        }
    }

    /**
     * Get template audit logs with optional filtering
     * @param {Object} options - Query options
     * @param {string} options.template_id - Filter by specific template UUID
     * @param {string} options.dealer_id - Filter by dealer ID (includes source/target dealer for copy operations)
     * @param {string} options.operation - Filter by operation type (CREATE, UPDATE, DELETE, COPY)
     * @param {string} options.user_email_filter - Filter by user who performed the operation
     * @param {number} options.limit - Maximum number of records (1-100, default: 50)
     * @param {number} options.offset - Number of records to skip (default: 0)
     * @returns {Promise<Object>} Template logs response
     */
    async getTemplateLogs(options = {}) {
        try {
            const { template_id = null, dealer_id = null, operation = null, user_email_filter = null, limit = 50, offset = 0 } = options;

            const params = new URLSearchParams();
            if (template_id) params.append('template_id', template_id);
            if (dealer_id) params.append('dealer_id', dealer_id);
            if (operation) params.append('operation', operation);
            if (user_email_filter) params.append('user_email_filter', user_email_filter);
            params.append('limit', Math.min(100, Math.max(1, limit)).toString());
            params.append('offset', Math.max(0, offset).toString());

            const url = `/v1/whatsapp-templates/logs?${params.toString()}`;
            const response = await api.get(url);

            return response.data;
        } catch (error) {
            console.error('Error fetching template logs:', error);
            throw error;
        }
    }

    /**
     * Get reminder target options for dropdowns
     * Note: This uses the existing CustomerService endpoint
     * @returns {Promise<Object>} Reminder target options response
     */
    async getReminderTargetOptions() {
        try {
            // Import CustomerService to reuse existing endpoint
            const CustomerServiceModule = await import('./CustomerService.js');
            const customerService = CustomerServiceModule.default || new CustomerServiceModule.CustomerService();
            return await customerService.getReminderTargets();
        } catch (error) {
            console.error('Error fetching reminder target options:', error);
            // Fallback options based on the enum values
            return {
                success: true,
                data: [
                    { label: 'All Targets', value: '' },
                    { label: 'KPB 1', value: 'KPB-1' },
                    { label: 'KPB 2', value: 'KPB-2' },
                    { label: 'KPB 3', value: 'KPB-3' },
                    { label: 'KPB 4', value: 'KPB-4' },
                    { label: 'Non KPB', value: 'Non KPB' },
                    { label: 'Booking Servis', value: 'Booking Servis' },
                    { label: 'Ultah Konsumen', value: 'Ultah Konsumen' },
                    { label: 'Selesai Servis', value: 'Selesai Servis' }
                ]
            };
        }
    }

    /**
     * Get template statistics (if needed for dashboard widgets)
     * @param {string} dealerId - Optional dealer ID filter
     * @returns {Promise<Object>} Template statistics
     */
    async getTemplateStatistics(dealerId = null) {
        try {
            // This could be implemented as a separate endpoint if needed
            // For now, we can derive statistics from the getTemplates call
            const templates = await this.getTemplates({
                dealer_id: dealerId,
                size: 1000 // Get all templates for statistics
            });

            const stats = {
                total_templates: templates.pagination?.total || 0,
                dealer_specific: 0,
                global_templates: 0,
                by_reminder_target: {}
            };

            if (templates.data) {
                templates.data.forEach((template) => {
                    if (template.dealer_id) {
                        stats.dealer_specific++;
                    } else {
                        stats.global_templates++;
                    }

                    const target = template.reminder_target;
                    stats.by_reminder_target[target] = (stats.by_reminder_target[target] || 0) + 1;
                });
            }

            return { success: true, data: stats };
        } catch (error) {
            console.error('Error fetching template statistics:', error);
            throw error;
        }
    }
}

export default new WhatsAppTemplateService();
