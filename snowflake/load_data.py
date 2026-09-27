"""
AegisCortex AI - Data Ingestion and Document Chunking Engine
Loads synthetic structured clinical records into Snowflake tables and parses
FDA inserts, HEDIS guidelines, and encounter notes into semantically tagged chunks
for Cortex Search and local agent reasoning.
"""

import os
import sys
import glob
import re
import hashlib
import json
import argparse
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_CSV_DIR = BASE_DIR / "data" / "raw_csv"
DOCS_DIR = BASE_DIR / "data" / "clinical_docs"
PROCESSED_DIR = BASE_DIR / "data"

def compute_hash(text: str) -> str:
    """Returns SHA256 hex digest for chunk deduplication and change tracking."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

def parse_clinical_documents():
    """
    Parses unstructured text files in data/clinical_docs/ into section-aware chunks.
    Extracts document type, patient ID (if clinical note), section title, and text.
    """
    chunks = []
    doc_files = list(DOCS_DIR.glob("*.txt"))
    print(f"[*] Found {len(doc_files)} clinical documents in {DOCS_DIR}")

    for file_path in doc_files:
        filename = file_path.name
        content = file_path.read_text(encoding="utf-8")
        
        # Determine document type & title
        if "FDA_Metformin" in filename:
            doc_type = "FDA_INSERT"
            doc_title = "FDA Prescribing Information - Metformin Hydrochloride (Glucophage)"
            patient_id = None
        elif "FDA_Eliquis" in filename:
            doc_type = "FDA_INSERT"
            doc_title = "FDA Prescribing Information - Eliquis (Apixaban)"
            patient_id = None
        elif "FDA_Skyrizi" in filename:
            doc_type = "FDA_INSERT"
            doc_title = "FDA Prescribing Information - Skyrizi (risankizumab-rzaa)"
            patient_id = None
        elif "HEDIS" in filename:
            doc_type = "HEDIS_GUIDELINE"
            doc_title = "NCQA HEDIS MY2026 Comprehensive Diabetes Care (CDC) Guidelines"
            patient_id = None
        elif "PT1001" in filename:
            doc_type = "CLINICAL_NOTE"
            doc_title = "Nephrology Clinical Encounter Progress Note - Eleanor Vance"
            patient_id = "PT-1001"
        elif "PT1002" in filename:
            doc_type = "CLINICAL_NOTE"
            doc_title = "Primary Care Annual Wellness Visit - Marcus Brody"
            patient_id = "PT-1002"
        elif "PT1003" in filename:
            doc_type = "CLINICAL_NOTE"
            doc_title = "Cardiovascular Inpatient Discharge Summary - Arthur Pendelton"
            patient_id = "PT-1003"
        else:
            doc_type = "CLINICAL_NOTE"
            doc_title = filename.replace("_", " ").replace(".txt", "")
            patient_id = None

        # Split document by Markdown headers or section separators
        # Regex captures lines starting with '## ' or '### ' or numbered sections like '4. CONTRAINDICATIONS'
        sections = re.split(r'\n(?=#{1,3}\s+|[0-9]+\.\s+[A-Z\s]{4,}:?)', content)
        
        chunk_idx = 0
        for sec in sections:
            sec_clean = sec.strip()
            if not sec_clean:
                continue
            
            # Extract section heading
            first_line = sec_clean.split("\n")[0].strip("# \t")
            section_name = first_line[:120] if first_line else "GENERAL"
            
            # If section is very long (> 1500 chars), further subdivide by paragraphs
            if len(sec_clean) > 1500:
                paragraphs = sec_clean.split("\n\n")
                current_p = []
                current_len = 0
                for p in paragraphs:
                    p_str = p.strip()
                    if not p_str:
                        continue
                    if current_len + len(p_str) > 1200 and current_p:
                        chunk_text = "\n\n".join(current_p)
                        chunk_idx += 1
                        chunk_id = f"{filename}_{chunk_idx:03d}"
                        chunks.append({
                            "CHUNK_ID": chunk_id,
                            "FILE_NAME": filename,
                            "DOC_TITLE": doc_title,
                            "DOC_TYPE": doc_type,
                            "PATIENT_ID": patient_id,
                            "SECTION_NAME": section_name,
                            "PAGE_NUMBER": 1,
                            "CHUNK_TEXT": chunk_text,
                            "CHUNK_HASH": compute_hash(chunk_text)
                        })
                        current_p = [p_str]
                        current_len = len(p_str)
                    else:
                        current_p.append(p_str)
                        current_len += len(p_str)
                if current_p:
                    chunk_text = "\n\n".join(current_p)
                    chunk_idx += 1
                    chunk_id = f"{filename}_{chunk_idx:03d}"
                    chunks.append({
                        "CHUNK_ID": chunk_id,
                        "FILE_NAME": filename,
                        "DOC_TITLE": doc_title,
                        "DOC_TYPE": doc_type,
                        "PATIENT_ID": patient_id,
                        "SECTION_NAME": section_name,
                        "PAGE_NUMBER": 1,
                        "CHUNK_TEXT": chunk_text,
                        "CHUNK_HASH": compute_hash(chunk_text)
                    })
            else:
                chunk_idx += 1
                chunk_id = f"{filename}_{chunk_idx:03d}"
                chunks.append({
                    "CHUNK_ID": chunk_id,
                    "FILE_NAME": filename,
                    "DOC_TITLE": doc_title,
                    "DOC_TYPE": doc_type,
                    "PATIENT_ID": patient_id,
                    "SECTION_NAME": section_name,
                    "PAGE_NUMBER": 1,
                    "CHUNK_TEXT": sec_clean,
                    "CHUNK_HASH": compute_hash(sec_clean)
                })

    df_chunks = pd.DataFrame(chunks)
    out_csv = PROCESSED_DIR / "processed_chunks.csv"
    out_json = PROCESSED_DIR / "processed_chunks.json"
    df_chunks.to_csv(out_csv, index=False)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
    print(f"[+] Successfully generated {len(chunks)} semantic chunks -> {out_csv}")
    return df_chunks

def load_to_snowflake(dry_run: bool = False):
    """
    Connects to Snowflake and ingests patients, encounters, lab results, claims,
    and semantic document chunks into their respective tables.
    """
    df_chunks = parse_clinical_documents()

    if dry_run:
        print("[!] Dry-run mode enabled. Skipping live Snowflake connection.")
        print(f"    - Patients CSV: {RAW_CSV_DIR / 'patients.csv'}")
        print(f"    - Labs CSV: {RAW_CSV_DIR / 'lab_results.csv'}")
        print(f"    - Encounters CSV: {RAW_CSV_DIR / 'encounters.csv'}")
        print(f"    - Claims CSV: {RAW_CSV_DIR / 'claims.csv'}")
        print(f"    - Document Chunks: {len(df_chunks)} records ready for Cortex Search")
        return

    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
    database = os.getenv("SNOWFLAKE_DATABASE", "AEGIS_CORTEX_DB")
    schema = os.getenv("SNOWFLAKE_SCHEMA", "RAW")
    role = os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")

    if not all([account, user, password]):
        print("[!] Snowflake credentials not fully configured in environment.")
        print("    Please configure .env with SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD.")
        print("    To run without live database, use: python snowflake/load_data.py --dry-run")
        return

    try:
        import snowflake.connector
        from snowflake.connector.pandas_tools import write_pandas

        print(f"[*] Connecting to Snowflake account {account} as user {user}...")
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            role=role
        )
        cur = conn.cursor()
        print("[+] Connected to Snowflake successfully.")

        # 1. Load CSVs (Ordered by foreign key dependencies)
        for table_name, csv_file in [
            ("MDM_HCO_MASTER", RAW_CSV_DIR / "mdm_hco_master.csv"),
            ("MDM_HCP_MASTER", RAW_CSV_DIR / "mdm_hcp_master.csv"),
            ("DIM_TERRITORY", RAW_CSV_DIR / "dim_territory.csv"),
            ("MAP_HCP_TERRITORY_ALIGNMENT", RAW_CSV_DIR / "map_hcp_territory_alignment.csv"),
            ("FACT_FORMULARY_TIER_COVERAGE", RAW_CSV_DIR / "fact_formulary_tier_coverage.csv"),
            ("FACT_PRESCRIPTION_EVENTS", RAW_CSV_DIR / "fact_prescription_events.csv"),
            ("FACT_PA_DENIALS", RAW_CSV_DIR / "fact_pa_denials.csv"),
            ("FACT_CALL_ACTIVITY", RAW_CSV_DIR / "fact_call_activity.csv"),
            ("PATIENTS", RAW_CSV_DIR / "patients.csv"),
            ("ENCOUNTERS", RAW_CSV_DIR / "encounters.csv"),
            ("LAB_RESULTS", RAW_CSV_DIR / "lab_results.csv"),
            ("CLAIMS", RAW_CSV_DIR / "claims.csv")
        ]:
            if not csv_file.exists():
                print(f"[!] Warning: {csv_file} does not exist.")
                continue
            df = pd.read_csv(csv_file)
            print(f"[*] Ingesting {len(df)} records into AEGIS_CORTEX_DB.RAW.{table_name}...")
            write_pandas(conn, df, table_name, database="AEGIS_CORTEX_DB", schema="RAW", overwrite=True)
            print(f"[+] Loaded {table_name}.")

        # 2. Load CLINICAL_DOC_CHUNKS into TRANSFORMED
        print(f"[*] Ingesting {len(df_chunks)} document chunks into AEGIS_CORTEX_DB.TRANSFORMED.CLINICAL_DOC_CHUNKS...")
        write_pandas(conn, df_chunks, "CLINICAL_DOC_CHUNKS", database="AEGIS_CORTEX_DB", schema="TRANSFORMED", overwrite=True)
        print("[+] Loaded CLINICAL_DOC_CHUNKS.")

        cur.close()
        conn.close()
        print("[+++] Complete data ingestion and Cortex Search indexing preparation finished!")
    except Exception as e:
        print(f"[X] Snowflake ingestion error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AegisCortex AI Data Ingestion")
    parser.add_argument("--dry-run", action="store_true", help="Process and validate chunks locally without live Snowflake upload")
    args = parser.parse_args()

    load_to_snowflake(dry_run=args.dry_run)
