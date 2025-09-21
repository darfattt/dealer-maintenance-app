import { ref, computed } from 'vue';

export function useTemplateVariables() {
    /**
     * Available template variables with descriptions
     * Based on the WhatsAppTemplate model format_template method
     */
    const templateVariables = ref([
        {
            variable: '{nama_pelanggan}',
            description: 'Customer name',
            category: 'Customer Information',
            example: 'John Doe'
        },
        {
            variable: '{nomor_telepon_pelanggan}',
            description: 'Customer phone number',
            category: 'Customer Information',
            example: '081234567890'
        },
        {
            variable: '{nomor_polisi}',
            description: 'Vehicle license plate number',
            category: 'Vehicle Information',
            example: 'B 1234 ABC'
        },
        {
            variable: '{tipe_unit}',
            description: 'Vehicle type/model',
            category: 'Vehicle Information',
            example: 'Honda Vario 125'
        },
        {
            variable: '{nomor_mesin}',
            description: 'Engine number',
            category: 'Vehicle Information',
            example: 'JB22E1234567'
        },
        {
            variable: '{tanggal_beli}',
            description: 'Purchase date (automatically formatted)',
            category: 'Date Information',
            example: '15 Januari 2024'
        },
        {
            variable: '{tanggal_expired_kpb}',
            description: 'KPB expiry date (automatically formatted)',
            category: 'Date Information',
            example: '15 Maret 2024'
        },
        {
            variable: '{kode_ahass}',
            description: 'AHASS code',
            category: 'AHASS Information',
            example: '00999'
        },
        {
            variable: '{nama_ahass}',
            description: 'AHASS name',
            category: 'AHASS Information',
            example: 'Daya Adicipta Motora'
        },
        {
            variable: '{alamat_ahass}',
            description: 'AHASS address',
            category: 'AHASS Information',
            example: 'Jl. Cibereum No. 26'
        },
        {
            variable: '{dealer_name}',
            description: 'Dealer name',
            category: 'Dealer Information',
            example: 'Honda Dealer Jakarta'
        }
    ]);

    /**
     * Group variables by category
     */
    const variablesByCategory = computed(() => {
        const categories = {};
        templateVariables.value.forEach((variable) => {
            if (!categories[variable.category]) {
                categories[variable.category] = [];
            }
            categories[variable.category].push(variable);
        });
        return categories;
    });

    /**
     * Get all variable names as a simple array
     */
    const variableNames = computed(() => {
        return templateVariables.value.map((v) => v.variable);
    });

    /**
     * Insert a variable into a textarea at the current cursor position
     * @param {HTMLTextAreaElement} textareaElement - The textarea element
     * @param {string} variable - The variable to insert (e.g., '{nama_pelanggan}')
     */
    const insertVariableIntoTextarea = (textareaElement, variable) => {
        if (!textareaElement || !variable) return;

        const start = textareaElement.selectionStart;
        const end = textareaElement.selectionEnd;
        const currentValue = textareaElement.value;

        // Insert variable at cursor position
        const newValue = currentValue.substring(0, start) + variable + currentValue.substring(end);

        // Update the textarea value
        textareaElement.value = newValue;

        // Set cursor position after the inserted variable
        const newCursorPosition = start + variable.length;
        textareaElement.setSelectionRange(newCursorPosition, newCursorPosition);

        // Focus back to textarea
        textareaElement.focus();

        // Trigger input event to notify Vue of the change
        const event = new Event('input', { bubbles: true });
        textareaElement.dispatchEvent(event);
    };

    /**
     * Validate if a template contains valid variables
     * @param {string} template - The template content
     * @returns {Object} Validation result with isValid and errors
     */
    const validateTemplate = (template) => {
        if (!template) {
            return { isValid: true, errors: [], warnings: [] };
        }

        const errors = [];
        const warnings = [];

        // Find all variables in the template
        const variableRegex = /\{([^}]+)\}/g;
        const foundVariables = [];
        let match;

        while ((match = variableRegex.exec(template)) !== null) {
            foundVariables.push(match[0]);
        }

        // Check if all found variables are valid
        const validVariableNames = variableNames.value;
        foundVariables.forEach((variable) => {
            if (!validVariableNames.includes(variable)) {
                errors.push(`Unknown variable: ${variable}`);
            }
        });

        // Check for common issues
        if (template.includes('{') && template.includes('}')) {
            // Check for unclosed braces
            const openBraces = (template.match(/\{/g) || []).length;
            const closeBraces = (template.match(/\}/g) || []).length;
            if (openBraces !== closeBraces) {
                errors.push('Unmatched braces detected. Make sure all { have corresponding }');
            }
        }

        // Warnings for potentially empty template
        if (template.trim().length === 0) {
            warnings.push('Template is empty');
        }

        return {
            isValid: errors.length === 0,
            errors,
            warnings,
            foundVariables: foundVariables.length
        };
    };

    /**
     * Generate a preview of the template with sample data
     * @param {string} template - The template content
     * @returns {string} Preview with sample data
     */
    const generatePreview = (template) => {
        if (!template) return '';

        let preview = template;

        templateVariables.value.forEach((variable) => {
            const regex = new RegExp(variable.variable.replace(/[{}]/g, '\\$&'), 'g');
            preview = preview.replace(regex, variable.example);
        });

        return preview;
    };

    /**
     * Get variable info by variable name
     * @param {string} variableName - The variable name (e.g., '{nama_pelanggan}')
     * @returns {Object|null} Variable info or null if not found
     */
    const getVariableInfo = (variableName) => {
        return templateVariables.value.find((v) => v.variable === variableName) || null;
    };

    /**
     * Search variables by text
     * @param {string} searchText - Text to search for
     * @returns {Array} Filtered variables
     */
    const searchVariables = (searchText) => {
        if (!searchText) return templateVariables.value;

        const searchLower = searchText.toLowerCase();
        return templateVariables.value.filter((variable) => variable.variable.toLowerCase().includes(searchLower) || variable.description.toLowerCase().includes(searchLower) || variable.category.toLowerCase().includes(searchLower));
    };

    return {
        // Data
        templateVariables,
        variablesByCategory,
        variableNames,

        // Methods
        insertVariableIntoTextarea,
        validateTemplate,
        generatePreview,
        getVariableInfo,
        searchVariables
    };
}
