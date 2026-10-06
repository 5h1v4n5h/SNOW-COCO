import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.snowflake_client import SnowflakeCortexClient

def main():
    print("=== Redeploying SPCS Service ENTERPRISE_PHARMA_COPILOT ===")
    client = SnowflakeCortexClient()
    cur = client.conn.cursor()

    # 1. Upload spec
    spec_path = Path(__file__).resolve().parent.parent / "spcs_service_spec.yaml"
    print(f"Uploading spec: {spec_path}")
    cur.execute("CREATE STAGE IF NOT EXISTS AEGIS_CORTEX_DB.APP.SPEC_STAGE DIRECTORY = (ENABLE = TRUE);")
    put_sql = f"PUT 'file://{spec_path.as_posix()}' @AEGIS_CORTEX_DB.APP.SPEC_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
    cur.execute(put_sql)
    print("Spec uploaded successfully.")

    # 2. Check compute pool COPILOT_POOL
    print("Ensuring COPILOT_POOL is active...")
    try:
        cur.execute("ALTER COMPUTE POOL COPILOT_POOL RESUME;")
    except Exception as e:
        print(f"Resume pool note: {e}")

    # 3. Drop and Recreate Service to force fresh image pull
    print("Recreating SPCS Service AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT...")
    try:
        cur.execute("DROP SERVICE IF EXISTS AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT;")
    except Exception as e:
        print(f"Drop service note: {e}")

    create_sql = """
    CREATE SERVICE AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT
        IN COMPUTE_POOL = COPILOT_POOL
        FROM @AEGIS_CORTEX_DB.APP.SPEC_STAGE
        SPECIFICATION_FILE = 'spcs_service_spec.yaml';
    """
    cur.execute(create_sql)
    print("Service created successfully!")

    # 4. Wait for service to become READY
    print("Waiting for containers to initialize (polling status)...")
    for i in range(24):  # Wait up to 2 minutes
        time.sleep(5)
        try:
            cur.execute("SELECT SYSTEM$GET_SERVICE_STATUS('AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT');")
            status_json_str = cur.fetchone()[0]
            status_data = json.loads(status_json_str)
            
            ready_count = 0
            for c in status_data:
                name = c.get("containerName")
                status = c.get("status")
                msg = c.get("message")
                print(f"  [{i*5}s] Container '{name}': {status} ({msg})")
                if status == "READY":
                    ready_count += 1
            
            if ready_count == len(status_data) and len(status_data) > 0:
                print("All containers are READY!")
                break
            
            # Check for failure
            for c in status_data:
                if c.get("status") == "FAILED":
                    print(f"Container '{c.get('containerName')}' reported FAILED.")
                    try:
                        cur.execute(f"SELECT SYSTEM$GET_SERVICE_LOGS('AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT', 0, '{c.get('containerName')}', 50);")
                        print("Logs:\n", cur.fetchone()[0])
                    except Exception as le:
                        print("Could not get logs:", le)
        except Exception as e:
            print(f"Polling error: {e}")

    # 5. Fetch public endpoint
    print("\n=== Service Endpoints ===")
    try:
        cur.execute("SHOW ENDPOINTS IN SERVICE AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT;")
        endpoints = cur.fetchall()
        for ep in endpoints:
            print(f"Endpoint: {ep[0]} | Port: {ep[1]} | Ingress: https://{ep[5]}")
    except Exception as e:
        print(f"Endpoint error: {e}")

    cur.close()

if __name__ == "__main__":
    main()
