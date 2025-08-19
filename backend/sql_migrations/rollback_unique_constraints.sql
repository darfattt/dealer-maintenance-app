-- =====================================================================
-- SQL Rollback Script: Remove Unique Constraints
-- =====================================================================
-- 
-- This script removes the unique constraints added by add_unique_constraints.sql
-- Use this if you need to rollback the constraint additions.
--
-- IMPORTANT: Only run this if you need to remove the constraints
--
-- Date: 2025-07-17
-- Purpose: Rollback unique constraints for bulk upsert operations
-- =====================================================================

-- Start transaction for safety
BEGIN;

-- =====================================================================
-- Remove PKB (Service Record) Processor Constraints
-- =====================================================================

-- Remove PKB Data constraint
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_pkb_dealer_work_order'
    ) THEN
        ALTER TABLE pkb_data 
        DROP CONSTRAINT uq_pkb_dealer_work_order;
        
        RAISE NOTICE 'Removed constraint: uq_pkb_dealer_work_order';
    ELSE
        RAISE NOTICE 'Constraint uq_pkb_dealer_work_order does not exist';
    END IF;
END
$$;

-- Remove PKB Service constraint
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_pkb_service_data_id_job'
    ) THEN
        ALTER TABLE pkb_services 
        DROP CONSTRAINT uq_pkb_service_data_id_job;
        
        RAISE NOTICE 'Removed constraint: uq_pkb_service_data_id_job';
    ELSE
        RAISE NOTICE 'Constraint uq_pkb_service_data_id_job does not exist';
    END IF;
END
$$;

-- Remove PKB Part constraint
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_pkb_part_data_id_job_parts_number'
    ) THEN
        ALTER TABLE pkb_parts 
        DROP CONSTRAINT uq_pkb_part_data_id_job_parts_number;
        
        RAISE NOTICE 'Removed constraint: uq_pkb_part_data_id_job_parts_number';
    ELSE
        RAISE NOTICE 'Constraint uq_pkb_part_data_id_job_parts_number does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove Prospect Data Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_prospect_dealer_id_prospect'
    ) THEN
        ALTER TABLE prospect_data 
        DROP CONSTRAINT uq_prospect_dealer_id_prospect;
        
        RAISE NOTICE 'Removed constraint: uq_prospect_dealer_id_prospect';
    ELSE
        RAISE NOTICE 'Constraint uq_prospect_dealer_id_prospect does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove Document Handling Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_document_handling_dealer_id_so'
    ) THEN
        ALTER TABLE document_handling_data 
        DROP CONSTRAINT uq_document_handling_dealer_id_so;
        
        RAISE NOTICE 'Removed constraint: uq_document_handling_dealer_id_so';
    ELSE
        RAISE NOTICE 'Constraint uq_document_handling_dealer_id_so does not exist';
    END IF;
END
$$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_document_handling_unit_data_id_rangka'
    ) THEN
        ALTER TABLE document_handling_units 
        DROP CONSTRAINT uq_document_handling_unit_data_id_rangka;
        
        RAISE NOTICE 'Removed constraint: uq_document_handling_unit_data_id_rangka';
    ELSE
        RAISE NOTICE 'Constraint uq_document_handling_unit_data_id_rangka does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove Billing Process Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_billing_process_dealer_invoice'
    ) THEN
        ALTER TABLE billing_process_data 
        DROP CONSTRAINT uq_billing_process_dealer_invoice;
        
        RAISE NOTICE 'Removed constraint: uq_billing_process_dealer_invoice';
    ELSE
        RAISE NOTICE 'Constraint uq_billing_process_dealer_invoice does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove SPK Dealing Process Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_spk_dealing_dealer_id_spk'
    ) THEN
        ALTER TABLE spk_dealing_process_data 
        DROP CONSTRAINT uq_spk_dealing_dealer_id_spk;
        
        RAISE NOTICE 'Removed constraint: uq_spk_dealing_dealer_id_spk';
    ELSE
        RAISE NOTICE 'Constraint uq_spk_dealing_dealer_id_spk does not exist';
    END IF;
END
$$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_spk_dealing_unit_data_id_tipe_warna'
    ) THEN
        ALTER TABLE spk_dealing_process_units 
        DROP CONSTRAINT uq_spk_dealing_unit_data_id_tipe_warna;
        
        RAISE NOTICE 'Removed constraint: uq_spk_dealing_unit_data_id_tipe_warna';
    ELSE
        RAISE NOTICE 'Constraint uq_spk_dealing_unit_data_id_tipe_warna does not exist';
    END IF;
END
$$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_spk_dealing_family_data_id_anggota_kk'
    ) THEN
        ALTER TABLE spk_dealing_process_family_members 
        DROP CONSTRAINT uq_spk_dealing_family_data_id_anggota_kk;
        
        RAISE NOTICE 'Removed constraint: uq_spk_dealing_family_data_id_anggota_kk';
    ELSE
        RAISE NOTICE 'Constraint uq_spk_dealing_family_data_id_anggota_kk does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove Parts Inbound Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_parts_inbound_dealer_no_penerimaan'
    ) THEN
        ALTER TABLE parts_inbound_data 
        DROP CONSTRAINT uq_parts_inbound_dealer_no_penerimaan;
        
        RAISE NOTICE 'Removed constraint: uq_parts_inbound_dealer_no_penerimaan';
    ELSE
        RAISE NOTICE 'Constraint uq_parts_inbound_dealer_no_penerimaan does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove Leasing Data Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_leasing_dealer_id_dokumen_pengajuan'
    ) THEN
        ALTER TABLE leasing_data 
        DROP CONSTRAINT uq_leasing_dealer_id_dokumen_pengajuan;
        
        RAISE NOTICE 'Removed constraint: uq_leasing_dealer_id_dokumen_pengajuan';
    ELSE
        RAISE NOTICE 'Constraint uq_leasing_dealer_id_dokumen_pengajuan does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove Unit Inbound Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_unit_inbound_dealer_no_shipping_list'
    ) THEN
        ALTER TABLE unit_inbound_data 
        DROP CONSTRAINT uq_unit_inbound_dealer_no_shipping_list;
        
        RAISE NOTICE 'Removed constraint: uq_unit_inbound_dealer_no_shipping_list';
    ELSE
        RAISE NOTICE 'Constraint uq_unit_inbound_dealer_no_shipping_list does not exist';
    END IF;
END
$$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_unit_inbound_unit_data_id_no_rangka'
    ) THEN
        ALTER TABLE unit_inbound_units 
        DROP CONSTRAINT uq_unit_inbound_unit_data_id_no_rangka;
        
        RAISE NOTICE 'Removed constraint: uq_unit_inbound_unit_data_id_no_rangka';
    ELSE
        RAISE NOTICE 'Constraint uq_unit_inbound_unit_data_id_no_rangka does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove Delivery Process Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_delivery_process_dealer_delivery_document_id'
    ) THEN
        ALTER TABLE delivery_process_data 
        DROP CONSTRAINT uq_delivery_process_dealer_delivery_document_id;
        
        RAISE NOTICE 'Removed constraint: uq_delivery_process_dealer_delivery_document_id';
    ELSE
        RAISE NOTICE 'Constraint uq_delivery_process_dealer_delivery_document_id does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove Unit Invoice Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_unit_invoice_dealer_no_invoice'
    ) THEN
        ALTER TABLE unit_invoice_data 
        DROP CONSTRAINT uq_unit_invoice_dealer_no_invoice;
        
        RAISE NOTICE 'Removed constraint: uq_unit_invoice_dealer_no_invoice';
    ELSE
        RAISE NOTICE 'Constraint uq_unit_invoice_dealer_no_invoice does not exist';
    END IF;
END
$$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_unit_invoice_unit_data_id_no_rangka'
    ) THEN
        ALTER TABLE unit_invoice_units 
        DROP CONSTRAINT uq_unit_invoice_unit_data_id_no_rangka;
        
        RAISE NOTICE 'Removed constraint: uq_unit_invoice_unit_data_id_no_rangka';
    ELSE
        RAISE NOTICE 'Constraint uq_unit_invoice_unit_data_id_no_rangka does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove Parts Sales Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_parts_sales_dealer_no_so'
    ) THEN
        ALTER TABLE parts_sales_data 
        DROP CONSTRAINT uq_parts_sales_dealer_no_so;
        
        RAISE NOTICE 'Removed constraint: uq_parts_sales_dealer_no_so';
    ELSE
        RAISE NOTICE 'Constraint uq_parts_sales_dealer_no_so does not exist';
    END IF;
END
$$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_parts_sales_part_data_id_parts_number'
    ) THEN
        ALTER TABLE parts_sales_parts 
        DROP CONSTRAINT uq_parts_sales_part_data_id_parts_number;
        
        RAISE NOTICE 'Removed constraint: uq_parts_sales_part_data_id_parts_number';
    ELSE
        RAISE NOTICE 'Constraint uq_parts_sales_part_data_id_parts_number does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove Workshop Invoice Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_workshop_invoice_dealer_no_work_order'
    ) THEN
        ALTER TABLE workshop_invoice_data 
        DROP CONSTRAINT uq_workshop_invoice_dealer_no_work_order;
        
        RAISE NOTICE 'Removed constraint: uq_workshop_invoice_dealer_no_work_order';
    ELSE
        RAISE NOTICE 'Constraint uq_workshop_invoice_dealer_no_work_order does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove DP HLO Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_dp_hlo_dealer_document'
    ) THEN
        ALTER TABLE dp_hlo_data 
        DROP CONSTRAINT uq_dp_hlo_dealer_document;
        
        RAISE NOTICE 'Removed constraint: uq_dp_hlo_dealer_document';
    ELSE
        RAISE NOTICE 'Constraint uq_dp_hlo_dealer_document does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove Unpaid HLO Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_unpaid_hlo_dealer_document'
    ) THEN
        ALTER TABLE unpaid_hlo_data 
        DROP CONSTRAINT uq_unpaid_hlo_dealer_document;
        
        RAISE NOTICE 'Removed constraint: uq_unpaid_hlo_dealer_document';
    ELSE
        RAISE NOTICE 'Constraint uq_unpaid_hlo_dealer_document does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Remove Parts Invoice Processor Constraints
-- =====================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_parts_invoice_dealer_no_invoice'
    ) THEN
        ALTER TABLE parts_invoice_data 
        DROP CONSTRAINT uq_parts_invoice_dealer_no_invoice;
        
        RAISE NOTICE 'Removed constraint: uq_parts_invoice_dealer_no_invoice';
    ELSE
        RAISE NOTICE 'Constraint uq_parts_invoice_dealer_no_invoice does not exist';
    END IF;
END
$$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_parts_invoice_part_data_id_parts_number_no_po'
    ) THEN
        ALTER TABLE parts_invoice_parts 
        DROP CONSTRAINT uq_parts_invoice_part_data_id_parts_number_no_po;
        
        RAISE NOTICE 'Removed constraint: uq_parts_invoice_part_data_id_parts_number_no_po';
    ELSE
        RAISE NOTICE 'Constraint uq_parts_invoice_part_data_id_parts_number_no_po does not exist';
    END IF;
END
$$;

-- =====================================================================
-- Commit rollback transaction
-- =====================================================================

COMMIT;

-- =====================================================================
-- Verification Query
-- =====================================================================

-- Run this query to verify constraints were removed:
SELECT 
    conname AS constraint_name,
    conrelid::regclass AS table_name
FROM pg_constraint 
WHERE conname LIKE 'uq_%' 
  AND contype = 'u'
ORDER BY conrelid::regclass::text, conname;

-- If the above query returns no rows, all constraints were successfully removed.

-- =====================================================================
-- END OF ROLLBACK SCRIPT
-- =====================================================================