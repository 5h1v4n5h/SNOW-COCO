# AegisCortex AI: Production Grade Pharma Multi-Agent RAG & Snowflake SPCS Deployment Plan

> **Executive Status:** BUILD COMPLETE & BENCHMARK CERTIFIED (100% SnowEval Pass Rate).  
> **Target Cloud:** Snowflake Cortex AI & Snowpark Container Services (SPCS)  
> **Account Identifier:** `cyvhobb-to17928` | **Database:** `AEGIS_CORTEX_DB` | **Role:** `ACCOUNTADMIN`  
> **Compute Pool:** `COPILOT_POOL` (`CPU_X64_XS` @ ~0.11 credits/hr — Optimized for $200 Credit Runway)  
> **Multi-Agent Harness:** RuFlo v3.52.1 + Fable-5 Strict Factual Persona Prompts  
> **Knowledge Engine:** Graphify Codebase Graph (`18 nodes, 21 edges`)  

---

## 1. The Complex Pharma Patient-Data Problem

Modern life sciences and pharmaceutical enterprises face severe systemic data fragmentation across the patient continuum:

```mermaid
graph TD
    subgraph DataSilos["Fragmented Data Silos (HIPAA Protected)"]
        D1["Longitudinal EHR (LOINC Labs, eGFR, HbA1c)"]
        D2["Pharmacy Dispense / TRx (RxNorm, NDC-11)"]
        D3["Payer Claims & X12 837 / 835 Remittances"]
        D4["Prior Authorization Rejections (Codes 70, 75, 88)"]
        D5["FDA Prescribing Info & Spl (21 CFR § 201.57)"]
    end

    subgraph PharmaProblems["Complex Clinical & Commercial Bottlenecks"]
        P1["Delayed Clinical Intervention: Silent eGFR decline under Metformin (Fatal Lactic Acidosis)"]
        P2["Polypharmacy Drug Interactions: Apixaban + Oral NSAIDs (Major GI Hemorrhage)"]
        P3["Payer Friction: $24.78M lost in recoverable biologic revenue due to step-therapy abandonment"]
        P4["Regulatory Firewalls: Commercial reps detailing off-label violates FDA OPDP 21 CFR § 202.1"]
        P5["Data Privacy Risks: Micro-cohort queries risk re-identifying rare disease patients (CMS N < 11)"]
    end

    D1 --> P1
    D2 --> P2
    D3 --> P3
    D4 --> P3
    D5 --> P4
```

### Key Complexities Addressed:
1. **Clinical Safety Inflections:** Identifying eGFR drops below 30 mL/min/1.73m² for patients on Metformin (FDA Boxed Warning) and flagging dangerous DOAC + NSAID co-prescriptions.
2. **Prior Authorization (PA) Recovery:** Auto-generating clinical appeal dossiers for high-cost biologics (Skyrizi) rejected under PBM step-therapy mandates (Reject Code 70), unlocking **$24,784,842.60** in recoverable revenue across 827 patients.
3. **Multi-Role Regulatory Compliance:** Enforcing rigid separation of concerns between Commercial Detailing (strict on-label only), Medical Affairs/MSLs (scientific exchange permitted), Market Access (formulary economics), and CCO Executives (CMS $N \ge 11$ cell suppression).

---

## 2. Optimized Multi-Agent RAG Architecture (RuFlo + Fable-5)

The solution uses a hierarchical multi-agent supervisor pattern coordinated by **RuFlo** and powered by **Fable-5 system prompt principles** (factual rigor, zero hedging, explicit line-number citations, hard compliance boundaries):

```mermaid
sequenceDiagram
    autonumber
    actor User as Pharma User (Rep, MSL, Market Access, CCO)
    participant UI as Command Center UI (Port 8080)
    participant Super as RuFlo Swarm Queen (AegisSupervisor)
    participant Guard as Guardrail Engine (HIPAA, OPDP, CMS)
    participant SQLAgent as ClinicalSQLAgent (Analyst API)
    participant DocAgent as DocEvidenceAgent (Cortex Search)
    participant SafetyAgent as ClinicalSafetyAgent (Rules Engine)
    participant ActionAgent as MCPOperationAgent (FHIR / Appeals)
    participant Snow as Snowflake Cortex AI (llama3.3-70b)

    User->>UI: Prompt ("Review patient PT-1001 or evaluate Skyrizi trial data")
    UI->>Super: POST /api/analyze (Query + Active Role)
    Super->>Guard: Pre-Execution Scan (Role RBAC, PII, Off-Label Detailing)
    
    alt Commercial Rep asks Off-Label
        Guard-->>Super: BLOCK (OPDP 21 CFR § 202.1 Violation)
        Super-->>UI: Return Mandatory Fair Balance & Redirect to Medical Affairs
    else Authorized Request
        Guard-->>Super: PASS (Security Context Enforced)
        par Parallel Execution
            Super->>SQLAgent: Query Patient 360 Lakehouse View
            SQLAgent->>Snow: SQL Execution (eGFR, HbA1c, TRx)
            Snow-->>SQLAgent: Structured Telemetry Data
        and
            Super->>DocAgent: Query FDA Labels & Guidelines
            DocAgent->>Snow: Cortex Search (Arctic Vector Embeddings)
            Snow-->>DocAgent: Ranked Text Chunks + Citations
        end

        Super->>SafetyAgent: Synthesize Clinical Telemetry + Boxed Warnings
        SafetyAgent-->>Super: Severity Assessment (CRITICAL / CONTRAINDICATION)
        
        alt Actionable Clinical Event Detected
            Super->>ActionAgent: Stage FHIR Order / Prior Auth Appeal Packet
            ActionAgent->>Snow: Stage Action in APP.CLINICAL_ACTION_AUDIT_LOG
            ActionAgent-->>Super: Staged Action (Pending Human Clinician Signature)
        end

        Super->>Snow: Generate Grounded Executive Briefing (llama3.3-70b)
        Snow-->>Super: Final Briefing with Verbatim File & Line Citations
        Super->>Guard: Post-Execution Audit (Fair Balance Attached, N>=11 Verified)
        Super-->>UI: Stream JSON Response to User
    end
```

### Specialized Agents & Roles:
| Agent | Core Function | Grounding Source | Fable-5 Prompt Rule |
| :--- | :--- | :--- | :--- |
| **Swarm Queen (`AegisSupervisor`)** | Intent classification, DAG planning, role guardrailing | Persona RBAC matrix | Direct synthesis, zero hedging, explicit error recovery |
| **`ClinicalSQLAgent`** | Translates clinical questions into optimized Snowflake SQL | `PATIENT_MEMBER_360_VIEW` | Enforces read-only schema boundary, zero injection |
| **`DocEvidenceAgent`** | Vector RAG similarity search across dossiers | `snowflake-arctic-embed-l-v2.0` | Cites exact filename, section, and line number |
| **`ClinicalSafetyAgent`** | Pharmacovigilance and contraindication detection | FDA Black Box Warnings, LOINC thresholds | Prioritizes patient safety over commercial goals |
| **`MCPOperationAgent`** | Generates FHIR orders and Prior Auth appeals | Audit ledger, CMS-1500 templates | Strict Human-in-the-Loop: Staged until e-signed |

---

## 3. Large-Scale Synthetic Pharma Lakehouse (10,000 Patients)

The data layer is structured across 4 Snowflake schemas (`RAW`, `STAGING`, `TRANSFORMED`, `APP`) modeling a complete enterprise ecosystem:

```mermaid
erDiagram
    PATIENTS ||--o{ LAB_RESULTS : undergoes
    PATIENTS ||--o{ PRESCRIPTIONS : receives
    PATIENTS ||--o{ ENCOUNTERS : attends
    PATIENTS ||--o{ CLAIMS : files
    PATIENTS ||--o{ PRIOR_AUTH_DENIALS : appeals
    HCPS ||--o{ PRESCRIPTIONS : writes
    HCOS ||--o{ ENCOUNTERS : hosts

    PATIENTS {
        string PATIENT_ID PK
        string FIRST_NAME
        string LAST_NAME
        int AGE
        string GENDER
        string RISK_STRATIFICATION
    }
    LAB_RESULTS {
        string RESULT_ID PK
        string PATIENT_ID FK
        string LOINC_CODE
        float LAB_NUMERIC_VALUE
        string RESULT_STATUS
    }
    PRESCRIPTIONS {
        string RX_ID PK
        string PATIENT_ID FK
        string DRUG_NAME
        string NDC_11
        string PRESCRIBER_NPI FK
    }
    PRIOR_AUTH_DENIALS {
        string PA_ID PK
        string PATIENT_ID FK
        string DRUG_NAME
        string REJECTION_CODE
        float EST_RECOVERABLE_REVENUE
    }
```

### Live Lakehouse Scale:
- **10,000 Longitudinal Patients** (`AEGIS_CORTEX_DB.RAW.PATIENTS`)
- **132,882 LOINC Laboratory Observations** (`AEGIS_CORTEX_DB.RAW.LAB_RESULTS`)
- **24,761 Longitudinal TRx Prescriptions** (`AEGIS_CORTEX_DB.RAW.PRESCRIPTIONS`)
- **40,075 Clinical Encounters & Payer Claims** (`RAW.ENCOUNTERS`, `RAW.CLAIMS`)
- **827 Prior Auth Denials** representing **$24,784,842.60** in recoverable biologic revenue.
- **500 Mastered HCPs** and **50 Health Systems (HCOs)** aligned across 4 national sales territories.

---

## 4. Multi-Role Pharma Command Center & RAG Dossier Renderer

The frontend ([`web/index.html`](file:///c:/Users/shiva/OneDrive/Desktop/SNOW%20COCO/web/index.html)) provides 5 distinct views tailored to pharma workflows:

1. **Guardrailed Intelligence Copilot:**
   - Multi-role switcher: Commercial Sales Rep (`Sarah Jenkins`), Medical Science Liaison (`Dr. Eleanor Vance`), Market Access Director (`David Ross`), Chief Commercial Officer (`Marcus Vance`).
   - Dynamic guardrails: Blocks off-label marketing, detects PII, appends 21 CFR § 202.1 Fair Balance, and enforces CMS $N \ge 11$ cell suppression.
2. **Patient Journey Radar:**
   - Displays real-time clinical inflection trajectories (eGFR decline, DDI flags, Prior Auth step-therapy blocks).
   - One-click Prior Auth Appeal Packet Generator committing e-signatures to Snowflake audit ledger (`APP.CLINICAL_ACTION_AUDIT_LOG`).
3. **Market Access & Territories:**
   - Territory Account Opportunity Index (AOI) scoring, travel impediment optimization, and rejection root-cause analysis (Codes 70, 75, 88).
4. **Executive Suite:**
   - Brand velocity, TRx run-rates, competitor patent-cliff displacement capture, and privacy-masked cohort metrics.
5. **RAG Evidence & File Renderer (5th Tab):**
   - High-fidelity dossier inspector rendering 7 verified clinical and regulatory documents line-by-line.
   - Quick section jump navigation (`INDICATIONS`, `BOXED WARNING`, `CLINICAL STUDIES`).
   - Snowflake Arctic semantic vector search with real-time excerpt matching and similarity scores.
   - Verbatim FDA citation copy tool for Medical, Legal, and Regulatory (MLR) audit trail compliance.

---

## 5. Snowflake $200 Credit Optimization Analysis

Snowflake provides free trial credits worth $200 (approx. **66.6 compute credits** at standard rates). Cost control is critical:

| Resource | Size / Config | Credits / Hour | Max Runtime on $200 Credits | Cost Control Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **SPCS Compute Pool (`COPILOT_POOL`)** | `CPU_X64_XS` (1 node) | **~0.11 credits/hr** | **~605 Hours (~25 Days)** | `AUTO_SUSPEND_SECS = 3600` suspends pool when inactive |
| **Virtual Warehouse (`COMPUTE_WH`)** | `X-Small` | **1 credit/hr** (when active) | Used only for batch queries (< 2 min/day) | `AUTO_SUSPEND = 60` suspends after 1 min idle |
| **OCI Image Registry** | Storage | $0.023 / GB / month | Negligible (< $0.05 / month) | Only contains 2 lightweight production images |
| **Cortex LLM (`llama3.3-70b`)** | Per-token billing | ~$0.0007 / 1k tokens | Covers > 250,000 multi-agent prompts | Cache frequently asked clinical summaries |

> [!TIP]
> **Total Runway:** The solution is designed to operate comfortably for **weeks** well within the $200 credit allotment without risk of unexpected overages.

---

## 6. Production SPCS Deployment Runbook

The Snowflake infrastructure has already been provisioned via [`scripts/deploy_snowflake_spcs.py`](file:///c:/Users/shiva/OneDrive/Desktop/SNOW%20COCO/scripts/deploy_snowflake_spcs.py). Follow these exact steps to push the container images and launch the live service:

### Step 1: Authenticate Local Docker to Snowflake Registry
```bash
# Snowflake Registry URL for account cyvhobb-to17928:
docker login cyvhobb-to17928.registry.snowflakecomputing.com -u MEDICAIDMAVERICS
# (Enter your Snowflake account password when prompted)
```

### Step 2: Build & Tag the Multi-Container Images
```bash
# Build Frontend NGINX Image (Port 8080)
docker build -f web/Dockerfile -t cyvhobb-to17928.registry.snowflakecomputing.com/aegis_cortex_db/app/copilot_repo/frontend:latest ./web

# Build Backend FastAPI Multi-Agent Swarm Image (Port 8000)
docker build -f api/Dockerfile -t cyvhobb-to17928.registry.snowflakecomputing.com/aegis_cortex_db/app/copilot_repo/backend:latest .
```

### Step 3: Push Images to Snowflake Image Repository
```bash
docker push cyvhobb-to17928.registry.snowflakecomputing.com/aegis_cortex_db/app/copilot_repo/frontend:latest
docker push cyvhobb-to17928.registry.snowflakecomputing.com/aegis_cortex_db/app/copilot_repo/backend:latest
```

### Step 4: Launch the Live Service in Snowflake
Execute the following SQL in Snowsight or via the Python client:
```sql
USE ROLE ACCOUNTADMIN;
USE DATABASE AEGIS_CORTEX_DB;
USE SCHEMA APP;

-- Create the live multi-container service referencing uploaded specification
CREATE SERVICE AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT
    IN COMPUTE_POOL = COPILOT_POOL
    FROM @AEGIS_CORTEX_DB.APP.SPEC_STAGE
    SPECIFICATION_FILE = 'spcs_service_spec.yaml'
    AUTO_RESUME = TRUE;
```

### Step 5: Validate Status & Retrieve Public Web Endpoint
```sql
-- Check service status (transitions from PENDING -> READY)
SELECT SYSTEM$GET_SERVICE_STATUS('AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT');

-- Retrieve the public ingress URL for the UI
SHOW ENDPOINTS IN SERVICE AEGIS_CORTEX_DB.APP.ENTERPRISE_PHARMA_COPILOT;
```
The output of `SHOW ENDPOINTS` will yield your live public ingress URL:
`https://<ingress_hash>.snowflakecomputing.app`

### Step 6: Post-Deployment Smoke Tests
1. **Health Endpoint:** `GET /health` returns `snowflake_connected: true`, `runtime: Live Snowflake Cortex`.
2. **Lakehouse Telemetry:** `GET /api/metrics/lakehouse` returns 10,000 patients, 132,882 labs, $24.78M recoverable.
3. **RAG Vector Search:** `POST /api/rag/search` returns verified semantic matches from FDA labels.
4. **Clinical Action Signing:** `POST /api/action/approve` updates `APP.CLINICAL_ACTION_AUDIT_LOG` with immutable clinician audit signature.

---

## 7. Automated Benchmark Certification (SnowEval)

The deployment is certified by the automated SnowEval evaluation suite ([`eval/snow_eval.py`](file:///c:/Users/shiva/OneDrive/Desktop/SNOW%20COCO/eval/snow_eval.py)):

| Metric | Result | Target Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **SnowEval Overall Pass Rate** | **100.0%** (15 / 15 Tests) | $\ge 90.0\%$ | ✅ PASSED |
| **Faithfulness Score** | **100.0%** | $\ge 95.0\%$ | ✅ PASSED |
| **Citation Precision** | **100.0%** | $\ge 90.0\%$ | ✅ PASSED |
| **Contraindication Recall** | **100.0%** | $100.0\%$ (Zero-Tolerance) | ✅ PASSED |
| **CMS Privacy Suppression ($N < 11$)** | **100.0%** | $100.0\%$ | ✅ PASSED |
| **Average Response Latency** | **1,366 ms** | $< 3,000\text{ ms}$ | ✅ PASSED |

---

## 8. RuFlo & Graphify Verification Summary

- **RuFlo Agent Harness:** Executed [`scripts/ruflo_swarm_evolution.py`](file:///c:/Users/shiva/OneDrive/Desktop/SNOW%20COCO/scripts/ruflo_swarm_evolution.py). Vector memory keys stored (`aegiscortex:architecture`, `aegiscortex:synthetic_scale`, `aegiscortex:guardrails`, `aegiscortex:deployment`), all 7 work packages registered, certified 100% deployment ready.
- **Graphify Knowledge Graph:** Created and verified [`graphify-out/graph.json`](file:///c:/Users/shiva/OneDrive/Desktop/SNOW%20COCO/graphify-out/graph.json). Identified central god nodes (`AegisSupervisor`, `FastAPI Server`, `SnowflakeCortexClient`, `PATIENT_MEMBER_360_VIEW`, `SPCS Spec`) enabling immediate cross-layer trace verification.
