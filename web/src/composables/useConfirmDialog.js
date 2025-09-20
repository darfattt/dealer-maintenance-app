import { useConfirm } from 'primevue/useconfirm';

export function useConfirmDialog() {
    const confirm = useConfirm();

    /**
     * Show a confirmation dialog for template deletion
     * @param {Object} template - The template object to delete
     * @param {string} template.id - Template ID
     * @param {string} template.reminder_target - Template reminder target
     * @param {string} template.reminder_type - Template reminder type
     * @returns {Promise<boolean>} True if confirmed, false if cancelled
     */
    const confirmDelete = (template) => {
        return new Promise((resolve) => {
            confirm.require({
                message: `Are you sure you want to delete this template?\n\nTarget: ${template.reminder_target}\nType: ${template.reminder_type}\n\nThis action cannot be undone.`,
                header: 'Delete Template Confirmation',
                icon: 'pi pi-exclamation-triangle',
                rejectLabel: 'Cancel',
                acceptLabel: 'Delete',
                acceptClass: 'p-button-danger',
                accept: () => resolve(true),
                reject: () => resolve(false)
            });
        });
    };

    /**
     * Show a confirmation dialog for template copy operation
     * @param {Object} copyData - The copy operation data
     * @param {string} copyData.source_dealer_id - Source dealer ID
     * @param {string} copyData.target_dealer_id - Target dealer ID
     * @param {boolean} copyData.overwrite_existing - Whether to overwrite existing templates
     * @param {number} templateCount - Number of templates to be copied
     * @returns {Promise<boolean>} True if confirmed, false if cancelled
     */
    const confirmCopy = (copyData, templateCount = 0) => {
        const overwriteText = copyData.overwrite_existing ? '\n\nExisting templates in the target dealer will be OVERWRITTEN.' : '\n\nExisting templates in the target dealer will be skipped.';

        return new Promise((resolve) => {
            confirm.require({
                message: `Are you sure you want to copy ${templateCount} template(s) from dealer "${copyData.source_dealer_id}" to dealer "${copyData.target_dealer_id}"?${overwriteText}`,
                header: 'Copy Templates Confirmation',
                icon: 'pi pi-question-circle',
                rejectLabel: 'Cancel',
                acceptLabel: 'Copy Templates',
                acceptClass: 'p-button-success',
                accept: () => resolve(true),
                reject: () => resolve(false)
            });
        });
    };

    /**
     * Show a confirmation dialog for leaving unsaved changes
     * @returns {Promise<boolean>} True if confirmed to leave, false if cancelled
     */
    const confirmUnsavedChanges = () => {
        return new Promise((resolve) => {
            confirm.require({
                message: 'You have unsaved changes. Are you sure you want to leave without saving?',
                header: 'Unsaved Changes',
                icon: 'pi pi-exclamation-triangle',
                rejectLabel: 'Stay',
                acceptLabel: 'Leave',
                acceptClass: 'p-button-secondary',
                accept: () => resolve(true),
                reject: () => resolve(false)
            });
        });
    };

    /**
     * Show a confirmation dialog for bulk operations
     * @param {string} operation - The operation name (e.g., "delete", "update")
     * @param {number} count - Number of items to be affected
     * @param {string} additionalInfo - Additional information about the operation
     * @returns {Promise<boolean>} True if confirmed, false if cancelled
     */
    const confirmBulkOperation = (operation, count, additionalInfo = '') => {
        const operationText = operation.charAt(0).toUpperCase() + operation.slice(1);
        const message = `Are you sure you want to ${operation} ${count} template(s)?${additionalInfo ? '\n\n' + additionalInfo : ''}\n\nThis action cannot be undone.`;

        return new Promise((resolve) => {
            confirm.require({
                message,
                header: `${operationText} Multiple Templates`,
                icon: 'pi pi-exclamation-triangle',
                rejectLabel: 'Cancel',
                acceptLabel: operationText,
                acceptClass: operation === 'delete' ? 'p-button-danger' : 'p-button-success',
                accept: () => resolve(true),
                reject: () => resolve(false)
            });
        });
    };

    /**
     * Show a success confirmation dialog
     * @param {string} title - Dialog title
     * @param {string} message - Success message
     * @returns {Promise<void>}
     */
    const showSuccess = (title, message) => {
        return new Promise((resolve) => {
            confirm.require({
                message,
                header: title,
                icon: 'pi pi-check-circle',
                rejectLabel: '',
                acceptLabel: 'OK',
                acceptClass: 'p-button-success',
                accept: () => resolve(),
                reject: () => resolve() // Same as accept for info dialogs
            });
        });
    };

    /**
     * Show an error dialog
     * @param {string} title - Dialog title
     * @param {string} message - Error message
     * @returns {Promise<void>}
     */
    const showError = (title, message) => {
        return new Promise((resolve) => {
            confirm.require({
                message,
                header: title,
                icon: 'pi pi-times-circle',
                rejectLabel: '',
                acceptLabel: 'OK',
                acceptClass: 'p-button-danger',
                accept: () => resolve(),
                reject: () => resolve() // Same as accept for info dialogs
            });
        });
    };

    /**
     * Show a custom confirmation dialog
     * @param {Object} options - Dialog options
     * @param {string} options.message - Dialog message
     * @param {string} options.header - Dialog header
     * @param {string} options.icon - Dialog icon
     * @param {string} options.acceptLabel - Accept button label
     * @param {string} options.rejectLabel - Reject button label
     * @param {string} options.acceptClass - Accept button CSS class
     * @returns {Promise<boolean>} True if confirmed, false if cancelled
     */
    const showCustomConfirm = (options) => {
        const { message, header = 'Confirmation', icon = 'pi pi-question-circle', acceptLabel = 'Yes', rejectLabel = 'No', acceptClass = 'p-button-primary' } = options;

        return new Promise((resolve) => {
            confirm.require({
                message,
                header,
                icon,
                rejectLabel,
                acceptLabel,
                acceptClass,
                accept: () => resolve(true),
                reject: () => resolve(false)
            });
        });
    };

    return {
        confirmDelete,
        confirmCopy,
        confirmUnsavedChanges,
        confirmBulkOperation,
        showSuccess,
        showError,
        showCustomConfirm
    };
}
