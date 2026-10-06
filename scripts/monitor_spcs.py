import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.snowflake_client import SnowflakeCortexClient

def main():
    c = SnowflakeCortexClient()
    cur = c.conn.cursor()
    print("Monitoring SPCS service status...")
    
    for attempt in range(20):
        time.sleep(5)
        try:
            cur.execute("SELECT SYSTEM$GET_SERVICE_STATUS('AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT');")
            raw = cur.fetchone()[0]
            data = json.loads(raw)
            print(f"\n--- Attempt {attempt + 1} ({attempt * 5}s) ---")
            ready_count = 0
            for item in data:
                cname = item.get("containerName")
                status = item.get("status")
                msg = item.get("message")
                restarts = item.get("restartCount")
                print(f"  Container [{cname}]: status={status}, restarts={restarts}, msg={msg}")
                if status == "READY":
                    ready_count += 1
            
            if ready_count == len(data) and len(data) > 0:
                print("\n SUCCESS: ALL CONTAINERS ARE READY AND HEALTHY!")
                break
                
            for item in data:
                if item.get("status") == "FAILED":
                    cname = item.get("containerName")
                    print(f"\n Container {cname} FAILED! Fetching logs...")
                    cur.execute(f"SELECT SYSTEM$GET_SERVICE_LOGS('AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT', 0, '{cname}', 50);")
                    print(cur.fetchone()[0])
                    return
        except Exception as e:
            print(f"Query note: {e}")

    # Fetch endpoint
    cur.execute("SHOW ENDPOINTS IN SERVICE AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT;")
    for row in cur.fetchall():
        print(f"Endpoint: {row[0]}, Port: {row[1]}, Ingress URL: https://{row[5]}")

if __name__ == "__main__":
    main()
