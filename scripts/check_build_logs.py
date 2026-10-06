import os
import sys
from core.snowflake_client import SnowflakeCortexClient

c = SnowflakeCortexClient()
cur = c.conn.cursor()

job_id = "USER$MEDICAIDMAVERICS.PUBLIC.SPCS_IMAGE_BUILDER_JOB_72O1I6AZU"
print(f"Checking status for: {job_id}")

try:
    cur.execute(f"SELECT SYSTEM$GET_SERVICE_STATUS('{job_id}');")
    print("Service Status:", cur.fetchone()[0])
except Exception as e:
    print("Status query error:", e)

try:
    cur.execute(f"SELECT SYSTEM$GET_SERVICE_LOGS('{job_id}', 0, 'job', 100);")
    print("Logs (container 'job'):\n", cur.fetchone()[0])
except Exception as e:
    print("Log query error for 'job':", e)

try:
    cur.execute(f"CALL SYSTEM$GET_JOB_LOGS('{job_id}', 100);")
    print("Job Logs:\n", cur.fetchone()[0])
except Exception as e:
    print("SYSTEM$GET_JOB_LOGS error:", e)
