-- ==============================================================================
-- AegisCortex AI - 04_cortex_search_setup.sql
-- Cortex Search Service DDL for Sub-Second Semantic Retrieval
-- Embedding Model: snowflake-arctic-embed-l-v2.0 (Native Cortex Vector)
-- ==============================================================================

USE DATABASE AEGIS_CORTEX_DB;
USE SCHEMA APP;

-- 1. Create the Cortex Search Service on Document Chunks
-- Enables semantic vector retrieval with metadata filtering on patient, document type, and section
CREATE OR REPLACE CORTEX SEARCH SERVICE AEGIS_CORTEX_DB.APP.CLINICAL_DOC_SEARCH
ON CHUNK_TEXT
ATTRIBUTES DOC_TYPE, PATIENT_ID, SECTION_NAME, DOC_TITLE, FILE_NAME
WAREHOUSE = COMPUTE_WH
TARGET_LAG = '1 hour'
AS (
    SELECT 
        CHUNK_ID,
        CHUNK_TEXT,
        DOC_TYPE,
        PATIENT_ID,
        SECTION_NAME,
        DOC_TITLE,
        FILE_NAME
    FROM AEGIS_CORTEX_DB.TRANSFORMED.CLINICAL_DOC_CHUNKS
);

COMMENT ON CORTEX SEARCH SERVICE AEGIS_CORTEX_DB.APP.CLINICAL_DOC_SEARCH 
IS 'AegisCortex AI Vector Search Service for FDA Inserts, HEDIS Guidelines, and Clinical Notes with sub-second hybrid retrieval';

-- 2. Verification Query Template
-- Demonstrates how to test Cortex Search from SQL using SNOWFLAKE.CORTEX.SEARCH_PREVIEW
/*
SELECT PARSE_JSON(
    SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'AEGIS_CORTEX_DB.APP.CLINICAL_DOC_SEARCH',
        '{
            "query": "eGFR threshold contraindication for metformin lactic acidosis risk",
            "columns": ["CHUNK_ID", "CHUNK_TEXT", "DOC_TITLE", "SECTION_NAME"],
            "filter": {"@eq": {"DOC_TYPE": "FDA_INSERT"}},
            "limit": 3
        }'
    )
)['results'] AS SEARCH_RESULTS;
*/

-- 3. Stored Procedure for Safe LLM Synthesis with Anti-Hallucination Guardrail
CREATE OR REPLACE PROCEDURE AEGIS_CORTEX_DB.APP.SYNTHESIZE_CLINICAL_INSIGHT(
    PROMPT VARCHAR,
    CONTEXT_CHUNKS VARCHAR
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    SYSTEM_INSTRUCTION VARCHAR;
    FULL_PROMPT VARCHAR;
    RESPONSE VARCHAR;
BEGIN
    SYSTEM_INSTRUCTION := 'You are AegisCortex AI Clinical Regulatory Copilot. ' ||
        'Answer strictly using the provided context chunks. ' ||
        'Every factual assertion must cite its exact source in the format [Doc: <TITLE>, Section: <SECTION>]. ' ||
        'If a contraindication is detected, output [SAFETY ALERT: CRITICAL] immediately. ' ||
        'Never speculate or extrapolate outside the provided clinical documents.';
        
    FULL_PROMPT := SYSTEM_INSTRUCTION || '\n\nCONTEXT:\n' || CONTEXT_CHUNKS || '\n\nQUESTION:\n' || PROMPT;
    
    RESPONSE := SNOWFLAKE.CORTEX.COMPLETE('llama3.3-70b', FULL_PROMPT);
    RETURN RESPONSE;
END;
$$;
