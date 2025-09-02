/**
 * Date formatting utilities with Indonesia timezone support
 * All functions automatically convert dates to Asia/Jakarta timezone (UTC+7)
 */

/**
 * Format date in Indonesia timezone with Indonesia locale (dd/mm/yyyy)
 * @param {string|Date} dateString - The date to format
 * @returns {string} Formatted date string or '-' if invalid
 */
export const formatIndonesiaDate = (dateString) => {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '-';
        
        return new Intl.DateTimeFormat('id-ID', {
            timeZone: 'Asia/Jakarta',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }).format(date);
    } catch (error) {
        console.warn('Error formatting date:', error);
        return '-';
    }
};

/**
 * Format date and time in Indonesia timezone with Indonesia locale (dd/mm/yyyy, hh:mm)
 * @param {string|Date} dateString - The date to format
 * @returns {string} Formatted datetime string or '-' if invalid
 */
export const formatIndonesiaDateTime = (dateString) => {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '-';
        
        return new Intl.DateTimeFormat('id-ID', {
            timeZone: 'Asia/Jakarta',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        }).format(date);
    } catch (error) {
        console.warn('Error formatting datetime:', error);
        return '-';
    }
};

/**
 * Format time only in Indonesia timezone (hh:mm:ss)
 * @param {string|Date} dateString - The date/time to format
 * @returns {string} Formatted time string or '-' if invalid
 */
export const formatIndonesiaTime = (dateString) => {
    if (!dateString) return '-';
    
    try {
        let date;
        
        // Handle time-only strings with microseconds (e.g., "14:30:00.123456")
        if (typeof dateString === 'string' && /^\d{1,2}:\d{2}:\d{2}\.\d{1,6}$/.test(dateString.trim())) {
            // For microsecond precision timestamps already in Indonesian timezone, just strip microseconds
            const [timePart] = dateString.trim().split('.');
            return timePart; // Return the time part without microseconds (already formatted as hh:mm:ss)
            
        } else if (typeof dateString === 'string' && /^\d{1,2}:\d{2}(:\d{2})?$/.test(dateString.trim())) {
            // Handle simple time-only strings (e.g., "14:30:00", "14:30") - keep as is
            const today = new Date();
            const [hours, minutes, seconds = '0'] = dateString.trim().split(':');
            date = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 
                           parseInt(hours, 10), parseInt(minutes, 10), parseInt(seconds, 10));
        } else {
            // Handle full datetime strings or Date objects
            date = new Date(dateString);
        }
        
        if (isNaN(date.getTime())) {
            console.warn('Invalid date provided to formatIndonesiaTime:', dateString);
            return '-';
        }
        
        return new Intl.DateTimeFormat('id-ID', {
            timeZone: 'Asia/Jakarta',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        }).format(date);
    } catch (error) {
        console.warn('Error formatting time:', error, 'Input:', dateString);
        return '-';
    }
};

/**
 * Format relative time (e.g., "2 hours ago", "Yesterday") in Indonesia timezone
 * @param {string|Date} dateString - The date to format
 * @returns {string} Relative time string or formatted date if too old
 */
export const formatRelativeTime = (dateString) => {
    if (!dateString) return 'Unknown date';
    
    try {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffHours < 1) {
        return 'Just now';
    } else if (diffHours < 24) {
        return `${diffHours} hours ago`;
    } else if (diffDays === 1) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else {
        return date.toLocaleDateString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    } catch (error) {
        console.warn('Error formatting relative time:', error);
        return formatIndonesiaDateTime(dateString);
    }
};

/**
 * Format date for API requests (YYYY-MM-DD) in Indonesia timezone
 * @param {Date} date - The date object to format
 * @returns {string} Formatted date string for API or empty string if invalid
 */
export const formatDateForAPI = (date) => {
    if (!date || !(date instanceof Date)) return '';
    
    try {
        if (isNaN(date.getTime())) return '';
        
        // Convert to Indonesia timezone and format as YYYY-MM-DD
        const jakartaDate = new Date(date.toLocaleString('en-US', { timeZone: 'Asia/Jakarta' }));
        
        const year = jakartaDate.getFullYear();
        const month = String(jakartaDate.getMonth() + 1).padStart(2, '0');
        const day = String(jakartaDate.getDate()).padStart(2, '0');
        
        return `${year}-${month}-${day}`;
    } catch (error) {
        console.warn('Error formatting date for API:', error);
        return '';
    }
};

/**
 * Get current date range for the current month in Indonesia timezone
 * @returns {Object} Object with firstDay and lastDay Date objects
 */
export const getCurrentMonthIndonesia = () => {
    try {
        // Get current date in Indonesia timezone
        const nowInJakarta = new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Jakarta' }));
        
        const firstDay = new Date(nowInJakarta.getFullYear(), nowInJakarta.getMonth(), 1);
        const lastDay = new Date(nowInJakarta.getFullYear(), nowInJakarta.getMonth() + 1, 0);
        
        return { firstDay, lastDay };
    } catch (error) {
        console.warn('Error getting current month in Indonesia:', error);
        // Fallback to local timezone
        const now = new Date();
        return {
            firstDay: new Date(now.getFullYear(), now.getMonth(), 1),
            lastDay: new Date(now.getFullYear(), now.getMonth() + 1, 0)
        };
    }
};