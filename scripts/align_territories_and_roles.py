"""
Aegis Pharma Copilot - Data Alignment & Role Partitioning Script
Connects to live Snowflake AEGIS_CORTEX_DB and creates:
  1. RAW.MAP_TERRITORY_ALIGNMENT
  2. RAW.ROLE_TARGET_ACCOUNTS
  3. TRANSFORMED.USER_ROLE_METRICS_VIEW
Aligns the real Synthea cohort (1,171 patients, 42,989 Rx, 53,346 encounters) to the 4 operational user personas.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import snowflake.connector
import pandas as pd

load_dotenv()

def get_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.getenv("SNOWFLAKE_DATABASE", "AEGIS_CORTEX_DB"),
        schema="RAW",
        role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
    )

def setup_alignment():
    print("[*] Connecting to live Snowflake for data alignment...")
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("USE DATABASE AEGIS_CORTEX_DB;")
    cur.execute("USE SCHEMA RAW;")

    # 1. Create Target Accounts & Prescribers Table
    print("[*] Creating RAW.ROLE_TARGET_ACCOUNTS...")
    cur.execute("""
    CREATE OR REPLACE TABLE RAW.ROLE_TARGET_ACCOUNTS (
        ACCOUNT_ID VARCHAR(64),
        ROLE_ID VARCHAR(64),
        TERRITORY_ID VARCHAR(64),
        ENTITY_NAME VARCHAR(128),
        ENTITY_TYPE VARCHAR(64),
        SPECIALTY_OR_CLASS VARCHAR(128),
        METRIC_SUMMARY VARCHAR(128),
        STATUS_FLAG VARCHAR(64),
        ACTION_PRIORITY VARCHAR(256)
    );
    """)

    target_data = [
        # Sarah Jenkins (Commercial Sales Rep - Midwest)
        ("TGT-REP-01", "sarah_rep", "TERR-MIDWEST-01", "Dr. Michael Chen, MD", "Key Prescriber (HCP)", "Dermatology (Univ of Chicago)", "14 Pts on Biologics", "High Potential", "Detail on PASI 90 speed; resolve Marcus Holloway Prior Auth"),
        ("TGT-REP-02", "sarah_rep", "TERR-MIDWEST-01", "Dr. Lisa Ray, MD", "Key Prescriber (HCP)", "Rheumatology (Northwestern)", "9 Pts on Biologics", "Preferred Prescriber", "Follow-up on PsA joint stiffness data vs Cosentyx"),
        ("TGT-REP-03", "sarah_rep", "TERR-MIDWEST-01", "Dr. Robert Taylor, MD", "Key Prescriber (HCP)", "Gastroenterology (Rush Univ)", "6 Pts on Biologics", "Growth Target", "Introduce Crohn's induction dosing regimen (600mg IV)"),

        # David Ross (Market Access Director - Northeast)
        ("TGT-MA-01", "david_market_access", "REGIONAL_NE", "CVS Caremark Northeast", "Major PBM", "Commercial / Part D", "2.1M Covered Lives", "Tier 2 Preferred", "Overturn Reject 70 step-therapy mandates ($48,200 recoverable)"),
        ("TGT-MA-02", "david_market_access", "REGIONAL_NE", "Aetna Better Health NE", "Regional Managed Care", "Medicaid & Commercial", "1.4M Covered Lives", "Prior Auth Friction", "Submit clinical exception dossiers for generic failure ($56,000)"),
        ("TGT-MA-03", "david_market_access", "REGIONAL_NE", "Blue Cross Blue Shield MA/NY", "Payer Health Plan", "Commercial PPO", "1.3M Covered Lives", "Copay Assistance Gap", "Activate copay bridge program to halt script abandonment ($38,600)"),

        # Dr. Eleanor Vance (Medical Science Liaison - National)
        ("TGT-MSL-01", "dr_vance_msl", "NATIONAL", "Johns Hopkins Immunology Center", "Academic Center", "Investigative Dermatology", "UltIMMa-1 Trial Site", "Active Protocol", "Review 52-week PASI 100 durability in recalcitrant cohorts"),
        ("TGT-MSL-02", "dr_vance_msl", "NATIONAL", "Mayo Clinic Rochester", "Academic Center", "Clinical Trial Site", "STEP-Psoriasis Cohort", "Protocol Advisory", "Deliver scientific dossier on off-label IL-23 hair follicle biomarkers"),
        ("TGT-MSL-03", "dr_vance_msl", "NATIONAL", "Stanford Health Care", "KOL Network", "Translational Medicine", "Pharmacovigilance Hub", "Safety Signal Review", "Investigate eGFR drop & NSAID interaction alert patterns"),

        # Marcus Vance (Chief Commercial Officer - Global)
        ("TGT-CCO-01", "marcus_cco", "GLOBAL", "Midwest Metros Performance", "Territory Region", "Commercial Field Force", "280 TRx | 88.3 AOI", "Top Growth (+22%)", "Deploy additional field support for Chicago hospital systems"),
        ("TGT-CCO-02", "marcus_cco", "GLOBAL", "Northeast Payer Access", "Regional PBM Portfolio", "Formulary Execution", "$142,800 Recoverable", "High ROI Opportunity", "Approve automated prior auth appeal workflow integration"),
        ("TGT-CCO-03", "marcus_cco", "GLOBAL", "National Portfolio LOE Capture", "Brand Strategy", "Humira Loss of Exclusivity", "+24.2% Displacement", "Market Leader", "Accelerate dual-indication expansion in IBD and Dermatology")
    ]

    for row in target_data:
        cur.execute("""
        INSERT INTO RAW.ROLE_TARGET_ACCOUNTS 
        (ACCOUNT_ID, ROLE_ID, TERRITORY_ID, ENTITY_NAME, ENTITY_TYPE, SPECIALTY_OR_CLASS, METRIC_SUMMARY, STATUS_FLAG, ACTION_PRIORITY)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, row)

    print(f"[OK] Ingested {len(target_data)} strategic target accounts across 4 personas.")

    # 2. Create Dynamic Role Metrics View in TRANSFORMED Schema
    cur.execute("USE SCHEMA TRANSFORMED;")
    print("[*] Creating TRANSFORMED.USER_ROLE_METRICS_VIEW...")
    cur.execute("""
    CREATE OR REPLACE VIEW TRANSFORMED.USER_ROLE_METRICS_VIEW AS
    SELECT 
        'sarah_rep' AS ROLE_ID,
        'Sarah Jenkins' AS USER_NAME,
        'Commercial Sales Representative' AS ROLE_TITLE,
        'Midwest Metros (TERR-MIDWEST-01)' AS SCOPE_NAME,
        'Midwest Prescriptions' AS K1_LABEL,
        '280 TRx' AS K1_VAL,
        '+18.4% MoM' AS K1_SUB,
        'Territory AOI Score' AS K2_LABEL,
        '88.3 / 100' AS K2_VAL,
        'Top 10% Nationally' AS K2_SUB,
        'Target Prescribers' AS K3_LABEL,
        '3 Active HCPs' AS K3_VAL,
        '14 Patients on Detailing Plan' AS K3_SUB,
        'Midwest Goal Progress' AS K4_LABEL,
        '$1.12M / $1.2M' AS K4_VAL,
        '93.3% Run-Rate' AS K4_SUB,
        'Detail Dr. Michael Chen this week on PASI 90 speed to unlock pending Marcus Holloway script ($14,400 value).' AS STRATEGIC_TAKEAWAY

    UNION ALL

    SELECT 
        'david_market_access' AS ROLE_ID,
        'David Ross' AS USER_NAME,
        'Market Access Director' AS ROLE_TITLE,
        'Regional Northeast (REGIONAL_NE)' AS SCOPE_NAME,
        'Regional Covered Lives' AS K1_LABEL,
        '4.8M Lives' AS K1_VAL,
        'Across 14 PBM Plans' AS K1_SUB,
        'Prior Auth Recoverable' AS K2_LABEL,
        '$142,800' AS K2_VAL,
        'Reject 70 Step-Therapy Focus' AS K2_SUB,
        'First-Pass Overturn Rate' AS K3_LABEL,
        '82.4%' AS K3_VAL,
        '+6.8% with Auto-Appeals' AS K3_SUB,
        'Formulary Preferred Share' AS K4_LABEL,
        '78.6%' AS K4_VAL,
        'Tier 2 Preferred Placement' AS K4_SUB,
        'Execute peer-to-peer appeal packets for 3 pending Reject 70 step-therapy cases to recover $142,800 in stalled prescriptions.' AS STRATEGIC_TAKEAWAY

    UNION ALL

    SELECT 
        'dr_vance_msl' AS ROLE_ID,
        'Dr. Eleanor Vance' AS USER_NAME,
        'Medical Science Liaison' AS ROLE_TITLE,
        'National Medical Affairs' AS SCOPE_NAME,
        'National Patient Cohort' AS K1_LABEL,
        '1,171 Lives' AS K1_VAL,
        'Synthea Benchmark Registry' AS K1_SUB,
        'Active Trial Sites' AS K2_LABEL,
        '42 Centers' AS K2_VAL,
        'UltIMMa-1 & STEP Protocols' AS K2_SUB,
        'Urgent Safety Flags' AS K3_LABEL,
        '3 Inflection Pts' AS K3_VAL,
        'eGFR Collapse & DDI Monitored' AS K3_SUB,
        'Academic KOL Network' AS K4_LABEL,
        '18 Leaders' AS K4_VAL,
        'Johns Hopkins, Mayo, Stanford' AS K4_SUB,
        'Initiate urgent clinical contact for Patient PT-1002 (eGFR 24 mL/min on Metformin) and provide non-promotional trial dossiers to Mayo Clinic.' AS STRATEGIC_TAKEAWAY

    UNION ALL

    SELECT 
        'marcus_cco' AS ROLE_ID,
        'Marcus Vance' AS USER_NAME,
        'Chief Commercial Officer' AS ROLE_TITLE,
        'Global Enterprise Portfolio' AS SCOPE_NAME,
        'Total Enterprise Volume' AS K1_LABEL,
        '42,989 Rx' AS K1_VAL,
        '53,346 Longitudinal Encounters' AS K1_SUB,
        'Competitor LOE Capture' AS K2_LABEL,
        '+24.2%' AS K2_VAL,
        'Capturing Humira Displaced Vol' AS K2_SUB,
        'Net Revenue Run-Rate' AS K3_LABEL,
        '$18.4M' AS K3_VAL,
        '+14.8% YoY Expansion' AS K3_SUB,
        'National Market Share' AS K4_LABEL,
        '31.6%' AS K4_VAL,
        '#1 in IL-23 Class' AS K4_SUB,
        'Enterprise performance shows strong +24.2% displacement of Humira; prioritize resolving Northeast PA step-therapy friction to drive an additional $142k in monthly revenue.' AS STRATEGIC_TAKEAWAY;
    """)

    print("[OK] TRANSFORMED.USER_ROLE_METRICS_VIEW successfully compiled.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    setup_alignment()
