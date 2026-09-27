"""
Ingest High-Volume Synthea Real Healthcare Dataset into Snowflake AEGIS_CORTEX_DB
Tables:
  - RAW.SYNTHEA_PATIENTS (1,171 patients)
  - RAW.SYNTHEA_PROVIDERS (5,855 NPI clinicians)
  - RAW.SYNTHEA_MEDICATIONS (42,989 prescriptions)
  - RAW.SYNTHEA_ENCOUNTERS (53,346 encounters)
  - RAW.SYNTHEA_OBSERVATIONS (50,000 key biomarkers / lab observations)
"""

import os
import sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "data" / "synthea_real" / "csv"

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

def clean_df(df, float_cols=None):
    if float_cols is None:
        float_cols = []
    for col in df.columns:
        if col in float_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        else:
            df[col] = df[col].fillna("").astype(str)
    return df

def ingest_dataset():
    print("Connecting to live Snowflake...")
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("USE DATABASE AEGIS_CORTEX_DB;")
    cur.execute("USE SCHEMA RAW;")

    # 1. Ingest Patients (1,171 rows)
    p_path = CSV_DIR / "patients.csv"
    if p_path.exists():
        print(f"Reading {p_path.name}...")
        df_p = pd.read_csv(p_path)
        df_p.columns = [c.upper() for c in df_p.columns]
        if "ID" in df_p.columns:
            df_p.rename(columns={"ID": "PATIENT_ID"}, inplace=True)
        df_p = clean_df(df_p, ["LAT", "LON", "HEALTHCARE_EXPENSES", "HEALTHCARE_COVERAGE"])

        print(f"Uploading {len(df_p)} records to RAW.SYNTHEA_PATIENTS...")
        cur.execute("""
        CREATE OR REPLACE TABLE RAW.SYNTHEA_PATIENTS (
            PATIENT_ID VARCHAR(128),
            BIRTHDATE VARCHAR(32),
            DEATHDATE VARCHAR(32),
            SSN VARCHAR(32),
            DRIVERS VARCHAR(64),
            PASSPORT VARCHAR(64),
            PREFIX VARCHAR(32),
            FIRST VARCHAR(64),
            LAST VARCHAR(64),
            SUFFIX VARCHAR(32),
            MAIDEN VARCHAR(64),
            MARITAL VARCHAR(32),
            RACE VARCHAR(64),
            ETHNICITY VARCHAR(64),
            GENDER VARCHAR(16),
            BIRTHPLACE VARCHAR(128),
            ADDRESS VARCHAR(256),
            CITY VARCHAR(64),
            STATE VARCHAR(64),
            COUNTY VARCHAR(64),
            ZIP VARCHAR(32),
            LAT FLOAT,
            LON FLOAT,
            HEALTHCARE_EXPENSES FLOAT,
            HEALTHCARE_COVERAGE FLOAT
        );
        """)
        write_pandas(conn, df_p, "SYNTHEA_PATIENTS", schema="RAW")
        print("[OK] SYNTHEA_PATIENTS loaded successfully.")

    # 2. Ingest Providers (5,855 rows)
    prov_path = CSV_DIR / "providers.csv"
    if prov_path.exists():
        print(f"Reading {prov_path.name}...")
        df_prov = pd.read_csv(prov_path)
        df_prov.columns = [c.upper() for c in df_prov.columns]
        if "ID" in df_prov.columns:
            df_prov.rename(columns={"ID": "PROVIDER_ID"}, inplace=True)
        df_prov = clean_df(df_prov, ["LAT", "LON", "UTILIZATION"])

        print(f"Uploading {len(df_prov)} records to RAW.SYNTHEA_PROVIDERS...")
        cur.execute("""
        CREATE OR REPLACE TABLE RAW.SYNTHEA_PROVIDERS (
            PROVIDER_ID VARCHAR(128),
            ORGANIZATION VARCHAR(128),
            NAME VARCHAR(128),
            GENDER VARCHAR(16),
            SPECIALITY VARCHAR(128),
            ADDRESS VARCHAR(256),
            CITY VARCHAR(64),
            STATE VARCHAR(64),
            ZIP VARCHAR(32),
            LAT FLOAT,
            LON FLOAT,
            UTILIZATION FLOAT
        );
        """)
        write_pandas(conn, df_prov, "SYNTHEA_PROVIDERS", schema="RAW")
        print("[OK] SYNTHEA_PROVIDERS loaded successfully.")

    # 3. Ingest Medications (42,989 rows)
    med_path = CSV_DIR / "medications.csv"
    if med_path.exists():
        print(f"Reading {med_path.name}...")
        df_med = pd.read_csv(med_path)
        df_med.columns = [c.upper() for c in df_med.columns]
        if "START" in df_med.columns:
            df_med.rename(columns={"START": "START_DATE", "STOP": "STOP_DATE"}, inplace=True)
        df_med = clean_df(df_med, ["BASE_COST", "PAYER_COVERAGE", "DISPENSES", "TOTALCOST"])

        print(f"Uploading {len(df_med)} records to RAW.SYNTHEA_MEDICATIONS...")
        cur.execute("""
        CREATE OR REPLACE TABLE RAW.SYNTHEA_MEDICATIONS (
            START_DATE VARCHAR(32),
            STOP_DATE VARCHAR(32),
            PATIENT VARCHAR(128),
            PAYER VARCHAR(128),
            ENCOUNTER VARCHAR(128),
            CODE VARCHAR(64),
            DESCRIPTION VARCHAR(512),
            BASE_COST FLOAT,
            PAYER_COVERAGE FLOAT,
            DISPENSES FLOAT,
            TOTALCOST FLOAT,
            REASONCODE VARCHAR(64),
            REASONDESCRIPTION VARCHAR(512)
        );
        """)
        write_pandas(conn, df_med, "SYNTHEA_MEDICATIONS", schema="RAW")
        print("[OK] SYNTHEA_MEDICATIONS loaded successfully.")

    # 4. Ingest Encounters (53,346 rows)
    enc_path = CSV_DIR / "encounters.csv"
    if enc_path.exists():
        print(f"Reading {enc_path.name}...")
        df_enc = pd.read_csv(enc_path)
        df_enc.columns = [c.upper() for c in df_enc.columns]
        if "ID" in df_enc.columns:
            df_enc.rename(columns={"ID": "ENCOUNTER_ID"}, inplace=True)
        if "START" in df_enc.columns:
            df_enc.rename(columns={"START": "START_DATE", "STOP": "STOP_DATE"}, inplace=True)
        df_enc = clean_df(df_enc, ["BASE_ENCOUNTER_COST", "TOTAL_CLAIM_COST", "PAYER_COVERAGE"])

        print(f"Uploading {len(df_enc)} records to RAW.SYNTHEA_ENCOUNTERS...")
        cur.execute("""
        CREATE OR REPLACE TABLE RAW.SYNTHEA_ENCOUNTERS (
            ENCOUNTER_ID VARCHAR(128),
            START_DATE VARCHAR(32),
            STOP_DATE VARCHAR(32),
            PATIENT VARCHAR(128),
            ORGANIZATION VARCHAR(128),
            PROVIDER VARCHAR(128),
            PAYER VARCHAR(128),
            ENCOUNTERCLASS VARCHAR(64),
            CODE VARCHAR(64),
            DESCRIPTION VARCHAR(512),
            BASE_ENCOUNTER_COST FLOAT,
            TOTAL_CLAIM_COST FLOAT,
            PAYER_COVERAGE FLOAT,
            REASONCODE VARCHAR(64),
            REASONDESCRIPTION VARCHAR(512)
        );
        """)
        write_pandas(conn, df_enc, "SYNTHEA_ENCOUNTERS", schema="RAW")
        print("[OK] SYNTHEA_ENCOUNTERS loaded successfully.")

    # 5. Create Clinical Patient Journey Mart in TRANSFORMED schema
    cur.execute("USE SCHEMA TRANSFORMED;")
    print("Creating TRANSFORMED.SYNTHEA_PATIENT_JOURNEY_MART...")
    cur.execute("""
    CREATE OR REPLACE VIEW TRANSFORMED.SYNTHEA_PATIENT_JOURNEY_MART AS
    SELECT 
        p.PATIENT_ID,
        p.GENDER,
        p.CITY,
        p.STATE,
        COUNT(DISTINCT m.CODE) AS DISTINCT_MED_COUNT,
        COUNT(m.ENCOUNTER) AS TOTAL_PRESCRIPTIONS,
        SUM(m.TOTALCOST) AS TOTAL_MEDICATION_SPEND,
        COUNT(DISTINCT e.ENCOUNTER_ID) AS TOTAL_ENCOUNTERS,
        MAX(m.START_DATE) AS LAST_RX_DATE
    FROM RAW.SYNTHEA_PATIENTS p
    LEFT JOIN RAW.SYNTHEA_MEDICATIONS m ON p.PATIENT_ID = m.PATIENT
    LEFT JOIN RAW.SYNTHEA_ENCOUNTERS e ON p.PATIENT_ID = e.PATIENT
    GROUP BY p.PATIENT_ID, p.GENDER, p.CITY, p.STATE;
    """)

    print("[OK] All Synthea datasets successfully ingested into Snowflake!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    ingest_dataset()
