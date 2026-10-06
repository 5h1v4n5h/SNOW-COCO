import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.snowflake_client import SnowflakeCortexClient
import json

c = SnowflakeCortexClient()
cur = c.conn.cursor()

def check(sql, title):
    print(f"=== {title} ===")
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        for r in rows:
            print(r)
        if not rows:
            print("(empty)")
    except Exception as e:
        print(f"Error: {e}")
    print()

check("SHOW IMAGES IN IMAGE REPOSITORY AEGIS_CORTEX_DB.APP.COPILOT_REPO;", "Images in Repo")
check("SELECT SYSTEM$GET_SERVICE_STATUS('AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT');", "Service Status JSON")
check("DESCRIBE SERVICE AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT;", "Describe Service")
check("SHOW ENDPOINTS IN SERVICE AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT;", "Service Endpoints")
check("SELECT SYSTEM$GET_SERVICE_LOGS('AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT', 0, 'backend', 100);", "Backend Container Logs")
check("SELECT SYSTEM$GET_SERVICE_LOGS('AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT', 0, 'frontend', 100);", "Frontend Container Logs")

