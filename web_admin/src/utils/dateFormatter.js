/**
 * Date formatting utilities for Indonesia timezone (WIB - GMT+7)
 */

/**
 * Convert UTC date to Indonesia time (WIB - GMT+7)
 * @param {string|Date} utcDate - UTC date string or Date object
 * @returns {Date} Date object in Indonesia timezone
 */
export function convertToIndonesiaTime(utcDate) {
    if (!utcDate) return null;

    const date = new Date(utcDate);
    if (isNaN(date.getTime())) return null;

    // Convert to WIB (GMT+7)
    const indonesiaTime = new Date(date.getTime() + (7 * 60 * 60 * 1000));
    return indonesiaTime;
}

/**
 * Format date to Indonesia format: "8 Okt 2025, 14:30 WIB"
 * @param {string|Date} utcDate - UTC date string or Date object
 * @returns {string} Formatted date string
 */
export function formatToIndonesiaTime(utcDate) {
    if (!utcDate) return '-';

    const date = new Date(utcDate);
    if (isNaN(date.getTime())) return '-';

    const months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
        'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'
    ];

    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${day} ${month} ${year}, ${hours}:${minutes} WIB`;
}

/**
 * Format date to full Indonesia format: "Senin, 8 Oktober 2025, 14:30:45 WIB"
 * @param {string|Date} utcDate - UTC date string or Date object
 * @returns {string} Formatted date string
 */
export function formatToFullIndonesiaTime(utcDate) {
    if (!utcDate) return '-';

    const date = new Date(utcDate);
    if (isNaN(date.getTime())) return '-';

    const days = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
    const months = [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ];

    const dayName = days[date.getDay()];
    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${dayName}, ${day} ${month} ${year}, ${hours}:${minutes}:${seconds} WIB`;
}

/**
 * Format date to relative time: "2 minutes ago", "1 hour ago"
 * @param {string|Date} utcDate - UTC date string or Date object
 * @returns {string} Relative time string
 */
export function formatRelativeTime(utcDate) {
    if (!utcDate) return '-';

    const date = new Date(utcDate);
    if (isNaN(date.getTime())) return '-';

    const now = new Date();
    const diffMs = now - date;
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSeconds < 60) {
        return `${diffSeconds} detik yang lalu`;
    } else if (diffMinutes < 60) {
        return `${diffMinutes} menit yang lalu`;
    } else if (diffHours < 24) {
        return `${diffHours} jam yang lalu`;
    } else if (diffDays < 7) {
        return `${diffDays} hari yang lalu`;
    } else {
        return formatToIndonesiaTime(utcDate);
    }
}

/**
 * Format date to time only: "14:30:45"
 * @param {string|Date} utcDate - UTC date string or Date object
 * @returns {string} Time string
 */
export function formatTimeOnly(utcDate) {
    if (!utcDate) return '-';

    const date = new Date(utcDate);
    if (isNaN(date.getTime())) return '-';

    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${hours}:${minutes}:${seconds}`;
}

/**
 * Format date to date only: "8 Oktober 2025"
 * @param {string|Date} utcDate - UTC date string or Date object
 * @returns {string} Date string
 */
export function formatDateOnly(utcDate) {
    if (!utcDate) return '-';

    const date = new Date(utcDate);
    if (isNaN(date.getTime())) return '-';

    const months = [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ];

    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();

    return `${day} ${month} ${year}`;
}

/**
 * Get current Indonesia time
 * @returns {Date} Current date in Indonesia timezone
 */
export function getCurrentIndonesiaTime() {
    return convertToIndonesiaTime(new Date());
}

/**
 * Format duration in seconds to human readable format
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration
 */
export function formatDuration(seconds) {
    if (!seconds || seconds < 0) return '-';

    if (seconds < 60) {
        return `${seconds} detik`;
    } else if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return remainingSeconds > 0
            ? `${minutes} menit ${remainingSeconds} detik`
            : `${minutes} menit`;
    } else {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return minutes > 0
            ? `${hours} jam ${minutes} menit`
            : `${hours} jam`;
    }
}

/**
 * Format file size to human readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
export function formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 B';

    const units = ['B', 'KB', 'MB', 'GB'];
    const k = 1024;
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${units[i]}`;
}
