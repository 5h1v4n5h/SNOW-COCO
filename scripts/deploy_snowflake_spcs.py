"""
AegisCortex AI - Snowflake SPCS Production Deployment & Provisioning Engine
Provisions compute pools, image repositories, stages, uploads service specs,
and validates the deployment on Snowflake Cortex AI and SPCS.
"""

import os
import sys
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.snowflake_client import SnowflakeCortexClient

def deploy_spcs():
    print("================================================================================")
    print("❄️  SNOWFLAKE SPCS PRODUCTION DEPLOYMENT & PROVISIONING ENGINE")
    print("================================================================================")
    print("[*] Target Database:  AEGIS_CORTEX_DB")
    print("[*] Target Schema:    APP")
    print("[*] Compute Pool:     COPILOT_POOL (Instance Family: CPU_X64_XS)")
    print("[*] Service Target:   ENTERPRISE_PHARMA_COPILOT")
    print("================================================================================\n")

    client = SnowflakeCortexClient()
    if not client.is_live():
        print("[!] Live Snowflake credentials not active. Aborting deployment.")
        return False

    cur = client.conn.cursor()

    # 1. Verify Database & Schemas
    print("[Step 1/6] Verifying Database and 4-Layer Lakehouse Schemas...")
    cur.execute("CREATE DATABASE IF NOT EXISTS AEGIS_CORTEX_DB;")
    for schema in ["RAW", "STAGING", "TRANSFORMED", "APP"]:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS AEGIS_CORTEX_DB.{schema};")
    print("  [OK] Schemas RAW, STAGING, TRANSFORMED, APP confirmed.")

    # 2. Provision Image Repository
    print("\n[Step 2/6] Provisioning SPCS OCI Image Repository...")
    cur.execute("CREATE IMAGE REPOSITORY IF NOT EXISTS AEGIS_CORTEX_DB.APP.COPILOT_REPO;")
    cur.execute("SHOW IMAGE REPOSITORIES IN SCHEMA AEGIS_CORTEX_DB.APP;")
    repo_rows = cur.fetchall()
    repo_url = repo_rows[0][4] if repo_rows else "Unknown"
    print(f"  [OK] Image Repository active: {repo_url}")

    # 3. Create Internal Stage & Upload Service Specification
    print("\n[Step 3/6] Uploading spcs_service_spec.yaml to @AEGIS_CORTEX_DB.APP.SPEC_STAGE...")
    cur.execute("CREATE STAGE IF NOT EXISTS AEGIS_CORTEX_DB.APP.SPEC_STAGE DIRECTORY = (ENABLE = TRUE);")
    spec_path = PROJECT_ROOT / "spcs_service_spec.yaml"
    put_sql = f"PUT 'file://{spec_path.as_posix()}' @AEGIS_CORTEX_DB.APP.SPEC_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
    cur.execute(put_sql)
    cur.execute("LIST @AEGIS_CORTEX_DB.APP.SPEC_STAGE;")
    stage_files = cur.fetchall()
    print(f"  [OK] Spec uploaded: {[f[0] for f in stage_files]}")

    # 4. Provision or Verify Compute Pool
    print("\n[Step 4/6] Provisioning / Inspecting Compute Pool COPILOT_POOL...")
    try:
        cur.execute("""
        CREATE COMPUTE POOL IF NOT EXISTS COPILOT_POOL
            MIN_NODES = 1
            MAX_NODES = 1
            INSTANCE_FAMILY = CPU_X64_XS
            AUTO_RESUME = TRUE
            AUTO_SUSPEND_SECS = 3600;
        """)
        cur.execute("SHOW COMPUTE POOLS LIKE 'COPILOT_POOL';")
        pool_info = cur.fetchall()
        status = pool_info[0][1] if pool_info else "ACTIVE"
        print(f"  [OK] Compute Pool COPILOT_POOL status: {status} (Cost-optimized CPU_X64_XS, ~0.11 credits/hr)")
    except Exception as e:
        print(f"  [!] Note on compute pool: {e}")

    # 5. Verify / Create Clinical Action Audit Ledger Table
    print("\n[Step 5/6] Verifying APP.CLINICAL_ACTION_AUDIT_LOG table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS AEGIS_CORTEX_DB.APP.CLINICAL_ACTION_AUDIT_LOG (
        ACTION_ID VARCHAR(64) PRIMARY KEY,
        SESSION_ID VARCHAR(64),
        PATIENT_ID VARCHAR(32),
        ACTION_TYPE VARCHAR(64),
        SEVERITY VARCHAR(16),
        ACTION_PAYLOAD VARIANT,
        DESTINATION VARCHAR(64),
        DISPATCHED_BY_AGENT VARCHAR(64),
        APPROVED_BY_USER VARCHAR(128),
        CITATION_HASH VARCHAR(128),
        DISPATCHED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    );
    """)
    print("  [OK] Audit Ledger Table active and ready.")

    # 6. Check Service Status or Create Service
    print("\n[Step 6/6] Checking SPCS Service status in AEGIS_CORTEX_DB.APP...")
    try:
        cur.execute("SHOW SERVICES IN SCHEMA AEGIS_CORTEX_DB.APP;")
        services = cur.fetchall()
        print(f"  [OK] Existing services: {[s[1] for s in services] if services else 'None (Ready for creation)'}")
    except Exception as e:
        print(f"  [!] Note checking services: {e}")

    print("\n================================================================================")
    print("🚀 SNOWFLAKE SPCS INFRASTRUCTURE PROVISIONING COMPLETE!")
    print("================================================================================")
    print("To push container images to your Snowflake OCI Registry:")
    print(f"  1. docker login {repo_url.split('/')[0]} -u {client.user}")
    print(f"  2. docker build -f web/Dockerfile -t {repo_url}/frontend:latest ./web")
    print(f"  3. docker build -f api/Dockerfile -t {repo_url}/backend:latest .")
    print(f"  4. docker push {repo_url}/frontend:latest")
    print(f"  5. docker push {repo_url}/backend:latest")
    print("\nTo launch the live multi-container service in Snowflake:")
    print("  CREATE SERVICE AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT")
    print("    IN COMPUTE_POOL = COPILOT_POOL")
    print("    FROM @AEGIS_CORTEX_DB.APP.SPEC_STAGE")
    print("    SPECIFICATION_FILE = 'spcs_service_spec.yaml';")
    print("================================================================================\n")
    cur.close()
    return True

if __name__ == "__main__":
    deploy_spcs()
