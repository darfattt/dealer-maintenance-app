-- =====================================================================
-- SQL Migration Script: Add Unique Constraints for Bulk Upsert Operations
-- =====================================================================
-- 
-- This script adds unique constraints to support ON CONFLICT operations
-- in bulk upsert procedures across all processor tables.
--
-- IMPORTANT: Run this script in your SQL editor before testing processors
--
-- Date: 2025-07-17
-- Purpose: Fix "no unique or exclusion constraint matching" errors
-- =====================================================================

-- Start transaction for safety
BEGIN;

-- =====================================================================
-- PKB (Service Record) Processor Constraints
-- =====================================================================

-- PKB Data: Main service records
-- Constraint: (dealer_id, no_work_order)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_pkb_dealer_work_order'
    ) THEN
        ALTER TABLE pkb_data 
        ADD CONSTRAINT uq_pkb_dealer_work_order 
        UNIQUE (dealer_id, no_work_order);
        
        RAISE NOTICE 'Added constraint: uq_pkb_dealer_work_order';
    ELSE
        RAISE NOTICE 'Constraint uq_pkb_dealer_work_order already exists';
    END IF;
END
$$;

-- PKB Service: Service line items
-- Constraint: (pkb_data_id, id_job)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_pkb_service_data_id_job'
    ) THEN
        ALTER TABLE pkb_services 
        ADD CONSTRAINT uq_pkb_service_data_id_job 
        UNIQUE (pkb_data_id, id_job);
        
        RAISE NOTICE 'Added constraint: uq_pkb_service_data_id_job';
    ELSE
        RAISE NOTICE 'Constraint uq_pkb_service_data_id_job already exists';
    END IF;
END
$$;

-- PKB Part: Parts used in service
-- Constraint: (pkb_data_id, id_job, parts_number)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_pkb_part_data_id_job_parts_number'
    ) THEN
        ALTER TABLE pkb_parts 
        ADD CONSTRAINT uq_pkb_part_data_id_job_parts_number 
        UNIQUE (pkb_data_id, id_job, parts_number);
        
        RAISE NOTICE 'Added constraint: uq_pkb_part_data_id_job_parts_number';
    ELSE
        RAISE NOTICE 'Constraint uq_pkb_part_data_id_job_parts_number already exists';
    END IF;
END
$$;

-- =====================================================================
-- Prospect Data Processor Constraints
-- =====================================================================

-- Prospect Data: Main prospect records
-- Constraint: (dealer_id, id_prospect)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_prospect_dealer_id_prospect'
    ) THEN
        ALTER TABLE prospect_data 
        ADD CONSTRAINT uq_prospect_dealer_id_prospect 
        UNIQUE (dealer_id, id_prospect);
        
        RAISE NOTICE 'Added constraint: uq_prospect_dealer_id_prospect';
    ELSE
        RAISE NOTICE 'Constraint uq_prospect_dealer_id_prospect already exists';
    END IF;
END
$$;

-- =====================================================================
-- Document Handling Processor Constraints
-- =====================================================================

-- Document Handling Data: Main document records
-- Constraint: (dealer_id, id_so)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_document_handling_dealer_id_so'
    ) THEN
        ALTER TABLE document_handling_data 
        ADD CONSTRAINT uq_document_handling_dealer_id_so 
        UNIQUE (dealer_id, id_so);
        
        RAISE NOTICE 'Added constraint: uq_document_handling_dealer_id_so';
    ELSE
        RAISE NOTICE 'Constraint uq_document_handling_dealer_id_so already exists';
    END IF;
END
$$;

-- Document Handling Unit: Document unit details
-- Constraint: (document_handling_data_id, nomor_rangka)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_document_handling_unit_data_id_rangka'
    ) THEN
        ALTER TABLE document_handling_units 
        ADD CONSTRAINT uq_document_handling_unit_data_id_rangka 
        UNIQUE (document_handling_data_id, nomor_rangka);
        
        RAISE NOTICE 'Added constraint: uq_document_handling_unit_data_id_rangka';
    ELSE
        RAISE NOTICE 'Constraint uq_document_handling_unit_data_id_rangka already exists';
    END IF;
END
$$;

-- =====================================================================
-- Billing Process Processor Constraints
-- =====================================================================

-- Billing Process Data: Invoice records
-- Constraint: (dealer_id, id_invoice)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_billing_process_dealer_invoice'
    ) THEN
        ALTER TABLE billing_process_data 
        ADD CONSTRAINT uq_billing_process_dealer_invoice 
        UNIQUE (dealer_id, id_invoice);
        
        RAISE NOTICE 'Added constraint: uq_billing_process_dealer_invoice';
    ELSE
        RAISE NOTICE 'Constraint uq_billing_process_dealer_invoice already exists';
    END IF;
END
$$;

-- =====================================================================
-- SPK Dealing Process Processor Constraints
-- =====================================================================

-- SPK Dealing Process Data: Main SPK records
-- Constraint: (dealer_id, id_spk)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_spk_dealing_dealer_id_spk'
    ) THEN
        ALTER TABLE spk_dealing_process_data 
        ADD CONSTRAINT uq_spk_dealing_dealer_id_spk 
        UNIQUE (dealer_id, id_spk);
        
        RAISE NOTICE 'Added constraint: uq_spk_dealing_dealer_id_spk';
    ELSE
        RAISE NOTICE 'Constraint uq_spk_dealing_dealer_id_spk already exists';
    END IF;
END
$$;

-- =====================================================================
-- Parts Inbound Processor Constraints
-- =====================================================================

-- Parts Inbound Data: Parts receipt records
-- Constraint: (dealer_id, no_penerimaan)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_parts_inbound_dealer_no_penerimaan'
    ) THEN
        ALTER TABLE parts_inbound_data 
        ADD CONSTRAINT uq_parts_inbound_dealer_no_penerimaan 
        UNIQUE (dealer_id, no_penerimaan);
        
        RAISE NOTICE 'Added constraint: uq_parts_inbound_dealer_no_penerimaan';
    ELSE
        RAISE NOTICE 'Constraint uq_parts_inbound_dealer_no_penerimaan already exists';
    END IF;
END
$$;

-- =====================================================================
-- Leasing Data Processor Constraints
-- =====================================================================

-- Leasing Data: Leasing application records
-- Constraint: (dealer_id, id_dokumen_pengajuan)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_leasing_dealer_id_dokumen_pengajuan'
    ) THEN
        ALTER TABLE leasing_data 
        ADD CONSTRAINT uq_leasing_dealer_id_dokumen_pengajuan 
        UNIQUE (dealer_id, id_dokumen_pengajuan);
        
        RAISE NOTICE 'Added constraint: uq_leasing_dealer_id_dokumen_pengajuan';
    ELSE
        RAISE NOTICE 'Constraint uq_leasing_dealer_id_dokumen_pengajuan already exists';
    END IF;
END
$$;

-- =====================================================================
-- Unit Inbound Processor Constraints
-- =====================================================================

-- Unit Inbound Data: Unit receipt records
-- Constraint: (dealer_id, no_shipping_list)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_unit_inbound_dealer_no_shipping_list'
    ) THEN
        ALTER TABLE unit_inbound_data 
        ADD CONSTRAINT uq_unit_inbound_dealer_no_shipping_list 
        UNIQUE (dealer_id, no_shipping_list);
        
        RAISE NOTICE 'Added constraint: uq_unit_inbound_dealer_no_shipping_list';
    ELSE
        RAISE NOTICE 'Constraint uq_unit_inbound_dealer_no_shipping_list already exists';
    END IF;
END
$$;

-- Unit Inbound Unit: Individual unit details
-- Constraint: (unit_inbound_data_id, no_rangka)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_unit_inbound_unit_data_id_no_rangka'
    ) THEN
        ALTER TABLE unit_inbound_units 
        ADD CONSTRAINT uq_unit_inbound_unit_data_id_no_rangka 
        UNIQUE (unit_inbound_data_id, no_rangka);
        
        RAISE NOTICE 'Added constraint: uq_unit_inbound_unit_data_id_no_rangka';
    ELSE
        RAISE NOTICE 'Constraint uq_unit_inbound_unit_data_id_no_rangka already exists';
    END IF;
END
$$;

-- =====================================================================
-- Delivery Process Processor Constraints
-- =====================================================================

-- Delivery Process Data: Delivery records
-- Constraint: (dealer_id, delivery_document_id)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_delivery_process_dealer_delivery_document_id'
    ) THEN
        ALTER TABLE delivery_process_data 
        ADD CONSTRAINT uq_delivery_process_dealer_delivery_document_id 
        UNIQUE (dealer_id, delivery_document_id);
        
        RAISE NOTICE 'Added constraint: uq_delivery_process_dealer_delivery_document_id';
    ELSE
        RAISE NOTICE 'Constraint uq_delivery_process_dealer_delivery_document_id already exists';
    END IF;
END
$$;

-- =====================================================================
-- Unit Invoice Processor Constraints
-- =====================================================================

-- Unit Invoice Data: Unit invoice records
-- Constraint: (dealer_id, no_invoice)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_unit_invoice_dealer_no_invoice'
    ) THEN
        ALTER TABLE unit_invoice_data 
        ADD CONSTRAINT uq_unit_invoice_dealer_no_invoice 
        UNIQUE (dealer_id, no_invoice);
        
        RAISE NOTICE 'Added constraint: uq_unit_invoice_dealer_no_invoice';
    ELSE
        RAISE NOTICE 'Constraint uq_unit_invoice_dealer_no_invoice already exists';
    END IF;
END
$$;

-- Unit Invoice Unit: Individual invoice unit details
-- Constraint: (unit_invoice_data_id, no_rangka)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_unit_invoice_unit_data_id_no_rangka'
    ) THEN
        ALTER TABLE unit_invoice_units 
        ADD CONSTRAINT uq_unit_invoice_unit_data_id_no_rangka 
        UNIQUE (unit_invoice_data_id, no_rangka);
        
        RAISE NOTICE 'Added constraint: uq_unit_invoice_unit_data_id_no_rangka';
    ELSE
        RAISE NOTICE 'Constraint uq_unit_invoice_unit_data_id_no_rangka already exists';
    END IF;
END
$$;

-- =====================================================================
-- Parts Sales Processor Constraints
-- =====================================================================

-- Parts Sales Data: Parts sales records
-- Constraint: (dealer_id, no_so)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_parts_sales_dealer_no_so'
    ) THEN
        ALTER TABLE parts_sales_data 
        ADD CONSTRAINT uq_parts_sales_dealer_no_so 
        UNIQUE (dealer_id, no_so);
        
        RAISE NOTICE 'Added constraint: uq_parts_sales_dealer_no_so';
    ELSE
        RAISE NOTICE 'Constraint uq_parts_sales_dealer_no_so already exists';
    END IF;
END
$$;

-- Parts Sales Part: Individual parts in sales
-- Constraint: (parts_sales_data_id, parts_number)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_parts_sales_part_data_id_parts_number'
    ) THEN
        ALTER TABLE parts_sales_parts 
        ADD CONSTRAINT uq_parts_sales_part_data_id_parts_number 
        UNIQUE (parts_sales_data_id, parts_number);
        
        RAISE NOTICE 'Added constraint: uq_parts_sales_part_data_id_parts_number';
    ELSE
        RAISE NOTICE 'Constraint uq_parts_sales_part_data_id_parts_number already exists';
    END IF;
END
$$;

-- =====================================================================
-- Workshop Invoice Processor Constraints
-- =====================================================================

-- Workshop Invoice Data: Workshop invoice records
-- Constraint: (dealer_id, no_work_order)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_workshop_invoice_dealer_no_work_order'
    ) THEN
        ALTER TABLE workshop_invoice_data 
        ADD CONSTRAINT uq_workshop_invoice_dealer_no_work_order 
        UNIQUE (dealer_id, no_work_order);
        
        RAISE NOTICE 'Added constraint: uq_workshop_invoice_dealer_no_work_order';
    ELSE
        RAISE NOTICE 'Constraint uq_workshop_invoice_dealer_no_work_order already exists';
    END IF;
END
$$;

-- =====================================================================
-- DP HLO Processor Constraints
-- =====================================================================

-- DP HLO Data: DP HLO records
-- Constraint: (dealer_id, id_hlo_document)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_dp_hlo_dealer_document'
    ) THEN
        ALTER TABLE dp_hlo_data 
        ADD CONSTRAINT uq_dp_hlo_dealer_document 
        UNIQUE (dealer_id, id_hlo_document);
        
        RAISE NOTICE 'Added constraint: uq_dp_hlo_dealer_document';
    ELSE
        RAISE NOTICE 'Constraint uq_dp_hlo_dealer_document already exists';
    END IF;
END
$$;

-- =====================================================================
-- Unpaid HLO Processor Constraints
-- =====================================================================

-- Unpaid HLO Data: Unpaid HLO records
-- Constraint: (dealer_id, id_hlo_document)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_unpaid_hlo_dealer_document'
    ) THEN
        ALTER TABLE unpaid_hlo_data 
        ADD CONSTRAINT uq_unpaid_hlo_dealer_document 
        UNIQUE (dealer_id, id_hlo_document);
        
        RAISE NOTICE 'Added constraint: uq_unpaid_hlo_dealer_document';
    ELSE
        RAISE NOTICE 'Constraint uq_unpaid_hlo_dealer_document already exists';
    END IF;
END
$$;

-- =====================================================================
-- Parts Invoice Processor Constraints
-- =====================================================================

-- Parts Invoice Data: Parts invoice records
-- Constraint: (dealer_id, no_invoice)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_parts_invoice_dealer_no_invoice'
    ) THEN
        ALTER TABLE parts_invoice_data 
        ADD CONSTRAINT uq_parts_invoice_dealer_no_invoice 
        UNIQUE (dealer_id, no_invoice);
        
        RAISE NOTICE 'Added constraint: uq_parts_invoice_dealer_no_invoice';
    ELSE
        RAISE NOTICE 'Constraint uq_parts_invoice_dealer_no_invoice already exists';
    END IF;
END
$$;

-- Parts Invoice Part: Individual parts for parts invoice
-- Constraint: (parts_invoice_data_id, parts_number, no_po)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_parts_invoice_part_data_id_parts_number_no_po'
    ) THEN
        ALTER TABLE parts_invoice_parts 
        ADD CONSTRAINT uq_parts_invoice_part_data_id_parts_number_no_po 
        UNIQUE (parts_invoice_data_id, parts_number, no_po);
        
        RAISE NOTICE 'Added constraint: uq_parts_invoice_part_data_id_parts_number_no_po';
    ELSE
        RAISE NOTICE 'Constraint uq_parts_invoice_part_data_id_parts_number_no_po already exists';
    END IF;
END
$$;

-- =====================================================================
-- Commit transaction
-- =====================================================================

COMMIT;

-- =====================================================================
-- Verification Query
-- =====================================================================

-- Run this query to verify all constraints were created successfully:
SELECT 
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint 
WHERE conname LIKE 'uq_%' 
  AND contype = 'u'
ORDER BY conrelid::regclass::text, conname;

-- =====================================================================
-- END OF MIGRATION SCRIPT
-- =====================================================================