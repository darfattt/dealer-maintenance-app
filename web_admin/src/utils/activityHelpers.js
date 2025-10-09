/**
 * Activity helpers for activity logs
 */

/**
 * Get PrimeIcon class for activity type
 */
export function getActivityIcon(activityType, action = null) {
    const icons = {
        'LOGIN': 'pi-sign-in',
        'LOGOUT': 'pi-sign-out',
        'LOGIN_FAILED': 'pi-times-circle',
        'API_REQUEST': 'pi-cloud',
        'GOOGLE_REVIEW': 'pi-star',
        'FILE_UPLOAD': 'pi-upload',
        'SUCCESS': 'pi-check-circle',
        'ERROR': 'pi-times-circle',
        'PROCESSING': 'pi-spin pi-spinner'
    };
    return icons[action || activityType] || 'pi-circle';
}

/**
 * Get color class for status
 */
export function getActivityColor(status, success = null) {
    if (success !== null) return success ? 'text-green-500' : 'text-red-500';
    const s = (status || '').toUpperCase();
    if (s.includes('SUCCESS') || s.includes('COMPLETED') || s === 'LOGIN' || s === 'LOGOUT') return 'text-green-500';
    if (s.includes('ERROR') || s.includes('FAILED')) return 'text-red-500';
    if (s.includes('PROCESSING') || s.includes('PENDING')) return 'text-blue-500';
    if (s.includes('PARTIAL') || s.includes('WARNING')) return 'text-orange-500';
    return 'text-gray-500';
}

/**
 * Get background color class
 */
export function getActivityBgColor(status, success = null) {
    if (success !== null) return success ? 'bg-green-50' : 'bg-red-50';
    const s = (status || '').toUpperCase();
    if (s.includes('SUCCESS') || s.includes('COMPLETED') || s === 'LOGIN' || s === 'LOGOUT') return 'bg-green-50';
    if (s.includes('ERROR') || s.includes('FAILED')) return 'bg-red-50';
    if (s.includes('PROCESSING') || s.includes('PENDING')) return 'bg-blue-50';
    if (s.includes('PARTIAL') || s.includes('WARNING')) return 'bg-orange-50';
    return 'bg-gray-50';
}

/**
 * Get PrimeVue Tag severity
 */
export function getStatusSeverity(status, success = null) {
    if (success !== null) return success ? 'success' : 'danger';
    const s = (status || '').toUpperCase();
    if (s.includes('SUCCESS') || s.includes('COMPLETED') || s === 'LOGIN' || s === 'LOGOUT') return 'success';
    if (s.includes('ERROR') || s.includes('FAILED')) return 'danger';
    if (s.includes('PROCESSING') || s.includes('PENDING')) return 'info';
    if (s.includes('PARTIAL') || s.includes('WARNING')) return 'warning';
    return 'secondary';
}

/**
 * Get HTTP method color
 */
export function getHttpMethodColor(method) {
    const colors = { 'GET': 'text-blue-600', 'POST': 'text-green-600', 'PUT': 'text-orange-600', 'DELETE': 'text-red-600' };
    return colors[(method || '').toUpperCase()] || 'text-gray-600';
}

/**
 * Get HTTP status code color
 */
export function getHttpStatusColor(code) {
    if (code >= 200 && code < 300) return 'text-green-600';
    if (code >= 400 && code < 500) return 'text-orange-600';
    if (code >= 500) return 'text-red-600';
    return 'text-gray-600';
}

/**
 * Format dealer info
 */
export function formatDealerInfo(dealerId, dealerName = null) {
    if (!dealerId) return '-';
    return dealerName ? `${dealerName} (${dealerId})` : `Dealer ${dealerId}`;
}
