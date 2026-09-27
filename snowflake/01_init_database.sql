-- ==============================================================================
-- AegisCortex AI - 01_init_database.sql
-- Initializes Database, Schemas, Stages, and HIPAA PHI Masking Policies
-- ==============================================================================

USE ROLE ACCOUNTADMIN;

-- 1. Create Core Database
CREATE DATABASE IF NOT EXISTS AEGIS_CORTEX_DB;
USE DATABASE AEGIS_CORTEX_DB;

-- 2. Create Functional Schemas
CREATE SCHEMA IF NOT EXISTS AEGIS_CORTEX_DB.RAW 
    COMMENT = 'Raw ingestion tables and encrypted stages for clinical files';

CREATE SCHEMA IF NOT EXISTS AEGIS_CORTEX_DB.TRANSFORMED 
    COMMENT = 'Cleaned, structured views and parsed document chunks';

CREATE SCHEMA IF NOT EXISTS AEGIS_CORTEX_DB.APP 
    COMMENT = 'Materialized serving tables, Cortex Search services, and audit ledgers';

-- 3. Create Internal Stage for PDFs and Unstructured Clinical Documents
CREATE OR REPLACE STAGE AEGIS_CORTEX_DB.RAW.STAGE_CLINICAL
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Server-side encrypted stage for clinical encounter notes, FDA package inserts, and guidelines';

-- 4. Dynamic Data Masking Policy for PHI (HIPAA Compliance)
-- Mask patient identifiers for standard analyst roles, revealing unmasked PHI only to privileged clinical roles
CREATE OR REPLACE MASKING POLICY AEGIS_CORTEX_DB.RAW.PHI_MASK_STRING AS (val STRING) 
RETURNS STRING ->
    CASE 
        WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'CLINICAL_ADMIN', 'CHIEF_MEDICAL_OFFICER', 'TREATING_PHYSICIAN') THEN val
        ELSE REGEXP_REPLACE(val, '(.).+', '\\1***')
    END;

-- 5. Warehouse Configuration
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH 
    WITH WAREHOUSE_SIZE = 'XSMALL' 
    AUTO_SUSPEND = 120 
    AUTO_RESUME = TRUE 
    INITIALLY_SUSPENDED = FALSE;

USE WAREHOUSE COMPUTE_WH;
