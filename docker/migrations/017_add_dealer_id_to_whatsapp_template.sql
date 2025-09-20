-- Migration: Add dealer_id column to whatsapp_template table
-- This migration adds dealer_id support to enable dealer-specific templates
-- Templates with dealer_id = NULL will be treated as global templates

-- Add dealer_id column to the whatsapp_template table
ALTER TABLE customer.whatsapp_template
ADD COLUMN dealer_id VARCHAR(50) NULL;

-- Create index for efficient dealer-specific template lookup
CREATE INDEX IF NOT EXISTS idx_whatsapp_template_dealer_lookup
ON customer.whatsapp_template (dealer_id, reminder_target, reminder_type);

-- Update the existing composite index to include dealer_id for better performance
DROP INDEX IF EXISTS customer.idx_whatsapp_template_lookup;
CREATE INDEX IF NOT EXISTS idx_whatsapp_template_lookup
ON customer.whatsapp_template (reminder_target, reminder_type, dealer_id);

-- Optional: Add foreign key constraint to ensure data integrity
-- Uncomment the following lines if you want to enforce referential integrity
-- ALTER TABLE customer.whatsapp_template
-- ADD CONSTRAINT fk_whatsapp_template_dealer
-- FOREIGN KEY (dealer_id) REFERENCES dealer_integration.dealers(dealer_id)
-- ON DELETE SET NULL;

-- Note: Existing templates will have dealer_id = NULL and will be treated as global templates
-- This provides backwards compatibility while enabling dealer-specific customization