-- ==============================================================================
-- AegisCortex AI - 03_patient_360_views.sql
-- Enterprise Patient & Member 360 View, Snapshot, and Audit Ledger
-- ==============================================================================

USE DATABASE AEGIS_CORTEX_DB;
USE SCHEMA TRANSFORMED;

CREATE OR REPLACE VIEW AEGIS_CORTEX_DB.TRANSFORMED.PATIENT_MEMBER_360_VIEW AS
WITH claims_agg AS (
    SELECT 
        PATIENT_ID,
        COUNT(CLAIM_ID) AS TOTAL_CLAIMS_COUNT,
        ROUND(SUM(TOTAL_CHARGES), 2) AS CUMULATIVE_CHARGES,
        ROUND(SUM(PAID_AMOUNT), 2) AS CUMULATIVE_PAID_AMOUNT,
        MAX(SERVICE_DATE) AS LAST_CLAIM_DATE
    FROM AEGIS_CORTEX_DB.RAW.CLAIMS
    GROUP BY PATIENT_ID
),
encounters_agg AS (
    SELECT 
        PATIENT_ID,
        COUNT(ENCOUNTER_ID) AS TOTAL_ENCOUNTERS_COUNT,
        MAX(ENCOUNTER_DATE) AS LAST_ENCOUNTER_DATE
    FROM AEGIS_CORTEX_DB.RAW.ENCOUNTERS
    GROUP BY PATIENT_ID
),
egfr_ranked AS (
    SELECT 
        PATIENT_ID,
        COLLECTION_DATE,
        NUMERIC_VALUE AS EGFR_VALUE,
        ROW_NUMBER() OVER (PARTITION BY PATIENT_ID ORDER BY COLLECTION_DATE DESC) AS rn
    FROM AEGIS_CORTEX_DB.RAW.LAB_RESULTS
    WHERE LOINC_CODE = '33914-3'
),
hba1c_ranked AS (
    SELECT 
        PATIENT_ID,
        COLLECTION_DATE,
        NUMERIC_VALUE AS HBA1C_VALUE,
        ROW_NUMBER() OVER (PARTITION BY PATIENT_ID ORDER BY COLLECTION_DATE DESC) AS rn
    FROM AEGIS_CORTEX_DB.RAW.LAB_RESULTS
    WHERE LOINC_CODE = '4548-4'
),
creat_ranked AS (
    SELECT 
        PATIENT_ID,
        COLLECTION_DATE,
        NUMERIC_VALUE AS CREATININE_VALUE,
        ROW_NUMBER() OVER (PARTITION BY PATIENT_ID ORDER BY COLLECTION_DATE DESC) AS rn
    FROM AEGIS_CORTEX_DB.RAW.LAB_RESULTS
    WHERE LOINC_CODE = '2160-0'
)
SELECT 
    p.PATIENT_ID,
    p.FIRST_NAME,
    p.LAST_NAME,
    p.GENDER,
    p.BIRTH_DATE,
    p.AGE,
    p.CITY,
    p.STATE,
    p.PRIMARY_PHYSICIAN,
    p.CHRONIC_CONDITIONS,
    p.ACTIVE_MEDICATIONS,
    p.RISK_DECIL_SCORE,
    p.RISK_STRATIFICATION,
    p.INSURANCE_PLAN,
    
    -- Claims Spend
    COALESCE(c.TOTAL_CLAIMS_COUNT, 0) AS TOTAL_CLAIMS_COUNT,
    COALESCE(c.CUMULATIVE_CHARGES, 0.0) AS CUMULATIVE_CHARGES,
    COALESCE(c.CUMULATIVE_PAID_AMOUNT, 0.0) AS CUMULATIVE_PAID_AMOUNT,
    c.LAST_CLAIM_DATE,
    
    -- Encounters
    COALESCE(e.TOTAL_ENCOUNTERS_COUNT, 0) AS TOTAL_ENCOUNTERS_COUNT,
    e.LAST_ENCOUNTER_DATE,
    
    -- Renal Telemetry (eGFR trajectory)
    egfr_latest.EGFR_VALUE AS LATEST_EGFR,
    egfr_latest.COLLECTION_DATE AS LATEST_EGFR_DATE,
    egfr_prev.EGFR_VALUE AS PREVIOUS_EGFR,
    egfr_prev.COLLECTION_DATE AS PREVIOUS_EGFR_DATE,
    ROUND(COALESCE(egfr_latest.EGFR_VALUE, 0) - COALESCE(egfr_prev.EGFR_VALUE, egfr_latest.EGFR_VALUE), 1) AS EGFR_DELTA,
    
    -- Serum Creatinine
    creat_latest.CREATININE_VALUE AS LATEST_CREATININE,
    creat_latest.COLLECTION_DATE AS LATEST_CREATININE_DATE,
    
    -- Glycemic Control & Care Gap Audit (HbA1c)
    hba1c_latest.HBA1C_VALUE AS LATEST_HBA1C,
    hba1c_latest.COLLECTION_DATE AS LATEST_HBA1C_DATE,
    DATEDIFF('day', COALESCE(hba1c_latest.COLLECTION_DATE, '2020-01-01'), CURRENT_DATE()) AS DAYS_SINCE_LAST_HBA1C,
    
    -- Clinical Safety Contraindication Detection Flags
    CASE 
        WHEN egfr_latest.EGFR_VALUE < 30.0 AND p.ACTIVE_MEDICATIONS ILIKE '%Metformin%' 
            THEN 'CRITICAL_CONTRAINDICATION: Metformin Boxed Warning in Severe Renal Failure (eGFR < 30)'
        WHEN p.ACTIVE_MEDICATIONS ILIKE '%Apixaban%' AND p.ACTIVE_MEDICATIONS ILIKE '%Ibuprofen%' 
            THEN 'MAJOR_INTERACTION: Direct Oral Anticoagulant + NSAID Elevated Bleeding Risk'
        ELSE 'NONE_DETECTED'
    END AS CONTRAINDICATION_ALERT,
    
    -- HEDIS Quality Gap Flag
    CASE 
        WHEN p.CHRONIC_CONDITIONS ILIKE '%Diabetes%' AND (DATEDIFF('day', COALESCE(hba1c_latest.COLLECTION_DATE, '2020-01-01'), CURRENT_DATE()) > 365)
            THEN 'CARE_GAP_OPEN: Overdue for Annual HEDIS NQF-0059 HbA1c Screening'
        ELSE 'COMPLIANT'
    END AS HEDIS_CARE_GAP_STATUS

FROM AEGIS_CORTEX_DB.RAW.PATIENTS p
LEFT JOIN claims_agg c ON p.PATIENT_ID = c.PATIENT_ID
LEFT JOIN encounters_agg e ON p.PATIENT_ID = e.PATIENT_ID
LEFT JOIN egfr_ranked egfr_latest ON p.PATIENT_ID = egfr_latest.PATIENT_ID AND egfr_latest.rn = 1
LEFT JOIN egfr_ranked egfr_prev ON p.PATIENT_ID = egfr_prev.PATIENT_ID AND egfr_prev.rn = 2
LEFT JOIN creat_ranked creat_latest ON p.PATIENT_ID = creat_latest.PATIENT_ID AND creat_latest.rn = 1
LEFT JOIN hba1c_ranked hba1c_latest ON p.PATIENT_ID = hba1c_latest.PATIENT_ID AND hba1c_latest.rn = 1;

-- ==============================================================================
-- Materialized Snapshot in APP Schema
-- ==============================================================================
USE SCHEMA APP;

CREATE OR REPLACE TABLE AEGIS_CORTEX_DB.APP.PATIENT_360_SNAPSHOT AS
SELECT * FROM AEGIS_CORTEX_DB.TRANSFORMED.PATIENT_MEMBER_360_VIEW;

-- ==============================================================================
-- Audit & Action Dispatcher Ledger Table
-- ==============================================================================
CREATE OR REPLACE TABLE AEGIS_CORTEX_DB.APP.CLINICAL_ACTION_AUDIT_LOG (
    ACTION_ID VARCHAR(64) PRIMARY KEY,
    SESSION_ID VARCHAR(64),
    PATIENT_ID VARCHAR(32),
    ACTION_TYPE VARCHAR(64),           -- 'PHYSICIAN_OVERRIDE_ALERT', 'HEDIS_CARE_TICKET', 'EHR_FLAG'
    SEVERITY VARCHAR(16),              -- 'CRITICAL', 'WARNING', 'INFO'
    ACTION_PAYLOAD VARIANT,            -- Full JSON payload dispatched to MCP
    DESTINATION VARCHAR(64),           -- 'SLACK', 'JIRA', 'EHR_FHIR', 'AUDIT_ONLY'
    DISPATCHED_BY_AGENT VARCHAR(64),   -- 'MCPActionAgent'
    APPROVED_BY_USER VARCHAR(128),
    CITATION_HASH VARCHAR(128),
    DISPATCHED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
