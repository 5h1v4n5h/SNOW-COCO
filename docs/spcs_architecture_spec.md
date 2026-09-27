# Enterprise Pharma Copilot — Technical Architecture Specification

## 1. Purpose and deployment model

The Enterprise Pharma Copilot is deployed as a Snowpark Container Services (SPCS) multi-container service with:

1. **React/Vite frontend** served by NGINX.
2. **FastAPI Enterprise Copilot Gateway** for authentication, authorization, orchestration, audit logging, Snowflake retrieval, and AI response controls.
3. **Snowflake Pharma Lakehouse** accessed through governed secure views, Snowpark, and Snowflake SQL/Cortex capabilities.
4. **Snowflake-native security controls** for role-based access control, row access policies, masking policies, audit logging, and data retention.

Only the React/NGINX endpoint is publicly exposed. The FastAPI container remains private and is reached from NGINX over the same SPCS service instance at `127.0.0.1:8000`.

```text
User Browser
    |
    | HTTPS / Snowflake SPCS authenticated public endpoint
    v
+---------------------------------------------------------------+
| Snowpark Container Service: ENTERPRISE_PHARMA_COPILOT         |
|                                                               |
|  Public endpoint :8080                                        |
|  +------------------------------+                             |
|  | frontend                     |                             |
|  | React build + NGINX          |                             |
|  | - Static SPA                 |                             |
|  | - /api/* proxy               |--- localhost:8000 --------+ |
|  | - SSE proxy configuration    |                            | |
|  +------------------------------+                            | |
|                                                               | |
|  Private endpoint :8000                                      | |
|  +---------------------------------------------------------+  | |
|  | api-gateway                                             |  | |
|  | FastAPI / Uvicorn                                       |<-+ |
|  | - AuthN / token validation                              |    |
|  | - RBAC / ABAC / territory enforcement                   |    |
|  | - Snowpark / Snowflake Connector                        |    |
|  | - Retrieval and Copilot orchestration                   |    |
|  | - Audit event writer                                    |    |
|  | - Fair-balance / approved-content policy enforcement    |    |
|  +---------------------------------------------------------+    |
+---------------------------------------------------------------+
                            |
                            | OAuth service token mounted by SPCS
                            | /snowflake/session/token
                            v
+-----------------------------------------------------------------+
| Snowflake                                                       |
|                                                                 |
| Governed application views                                      |
|  - V_MDM_HCP_MASTER                                             |
|  - V_MDM_HCO_MASTER                                             |
|  - V_DIM_TERRITORY                                              |
|  - V_MAP_HCP_TERRITORY_ALIGNMENT                                |
|  - V_FACT_FORMULARY_TIER_COVERAGE                               |
|  - V_FACT_PA_DENIALS                                            |
|  - V_FACT_PRESCRIPTION_EVENTS_SAFE_HARBOR                       |
|                                                                 |
| Snowflake services                                               |
|  - Snowpark / SQL                                               |
|  - Cortex LLM functions or approved external model gateway      |
|  - Audit tables, row access policies, masking policies          |
+-----------------------------------------------------------------+
```

---

## 2. Core architectural decisions

| Area | Decision |
|---|---|
| Frontend | React 18+, TypeScript, Vite build, Tailwind CSS or Vanilla CSS design system, served by NGINX. |
| Backend | FastAPI, Python 3.11+, Uvicorn, Pydantic v2, async SSE streaming. |
| Container communication | NGINX proxies `/api/` to `http://127.0.0.1:8000`. No browser-visible API host is required. |
| Public exposure | Only port `8080` is public. FastAPI port `8000` is private. |
| Snowflake access | SPCS service OAuth token read from `/snowflake/session/token`; no static Snowflake password or private key in container image or environment. |
| Data access | Application role accesses governed secure views, never base pharma tables directly. |
| Authorization | Snowflake/enterprise identity is mapped to application roles, commercial teams, brands, and authorized territory scopes. |
| AI grounding | Copilot retrieval uses governed views and approved medical/legal/regulatory content only. Generated answers must include provenance. |
| Auditability | Every user action, query, data-access decision, prompt version, model version, output disposition, and approval event is written to a controlled Snowflake audit trail. |
| PHI | Patient-level prescription data is not presented to the application. Prescription analytics must be sourced from HIPAA Safe Harbor de-identified or approved limited-data-set views. |
| Promotional content | Promotional claims require approved-content references, indication context, safety information, citations, and fair-balance controls. |

---

## 3. Snowflake data architecture

### 3.1 Source layers

The backend consumes the following four lakehouse layers.

| Lakehouse domain | Primary objects | Copilot use |
|---|---|---|
| MDM | `MDM_HCP_MASTER`, `MDM_HCO_MASTER` | HCP/HCO search, affiliation context, specialty, identifiers, address normalization. |
| Commercial Alignment | `DIM_TERRITORY`, `MAP_HCP_TERRITORY_ALIGNMENT` | Territory-scoped access control, field-force alignment, eligibility filtering. |
| Market Access | `FACT_FORMULARY_TIER_COVERAGE`, `FACT_PA_DENIALS` | Payer/formulary insights, coverage trends, prior-authorization analytics. |
| Longitudinal Prescriptions | `FACT_PRESCRIPTION_EVENTS` | Aggregated, de-identified prescription trends and longitudinal analytics. |

### 3.2 Required governed application views

The FastAPI service role must query approved views rather than the physical tables.

```sql
CREATE OR REPLACE SECURE VIEW PHARMA_APP.GOVERNED.V_MDM_HCP_MASTER AS
SELECT
    HCP_MASTER_ID,
    NPI_HASH,
    HCP_DISPLAY_NAME,
    SPECIALTY,
    PRIMARY_HCO_MASTER_ID,
    ADDRESS_CITY,
    ADDRESS_STATE,
    ZIP3,
    ACTIVE_FLAG
FROM PHARMA_LAKEHOUSE.MDM.MDM_HCP_MASTER;

CREATE OR REPLACE SECURE VIEW PHARMA_APP.GOVERNED.V_MDM_HCO_MASTER AS
SELECT
    HCO_MASTER_ID,
    HCO_DISPLAY_NAME,
    HCO_TYPE,
    ADDRESS_CITY,
    ADDRESS_STATE,
    ZIP3,
    ACTIVE_FLAG
FROM PHARMA_LAKEHOUSE.MDM.MDM_HCO_MASTER;

CREATE OR REPLACE SECURE VIEW PHARMA_APP.GOVERNED.V_DIM_TERRITORY AS
SELECT
    TERRITORY_ID,
    TERRITORY_NAME,
    REGION_ID,
    REGION_NAME,
    BUSINESS_UNIT,
    ACTIVE_FLAG
FROM PHARMA_LAKEHOUSE.COMMERCIAL_ALIGNMENT.DIM_TERRITORY;

CREATE OR REPLACE SECURE VIEW PHARMA_APP.GOVERNED.V_MAP_HCP_TERRITORY_ALIGNMENT AS
SELECT
    HCP_MASTER_ID,
    TERRITORY_ID,
    ALIGNMENT_START_DATE,
    ALIGNMENT_END_DATE,
    ALIGNMENT_TYPE,
    ACTIVE_FLAG
FROM PHARMA_LAKEHOUSE.COMMERCIAL_ALIGNMENT.MAP_HCP_TERRITORY_ALIGNMENT;

CREATE OR REPLACE SECURE VIEW PHARMA_APP.GOVERNED.V_FACT_FORMULARY_TIER_COVERAGE AS
SELECT
    PLAN_ID,
    PAYER_ID,
    PRODUCT_ID,
    GEOGRAPHY_CODE,
    COVERAGE_PERIOD_MONTH,
    FORMULARY_TIER,
    COVERAGE_STATUS,
    RESTRICTION_CODE,
    PA_REQUIRED_FLAG,
    STEP_EDIT_FLAG,
    QUANTITY_LIMIT_FLAG
FROM PHARMA_LAKEHOUSE.MARKET_ACCESS.FACT_FORMULARY_TIER_COVERAGE;

CREATE OR REPLACE SECURE VIEW PHARMA_APP.GOVERNED.V_FACT_PA_DENIALS AS
SELECT
    PRODUCT_ID,
    PAYER_ID,
    GEOGRAPHY_CODE,
    EVENT_MONTH,
    DENIAL_REASON_CODE,
    DENIAL_COUNT,
    SUBMISSION_COUNT,
    APPROVAL_COUNT
FROM PHARMA_LAKEHOUSE.MARKET_ACCESS.FACT_PA_DENIALS;
```

### 3.3 HIPAA Safe Harbor prescription view

`FACT_PRESCRIPTION_EVENTS` must not be exposed directly when it contains patient-level, prescriber-sensitive, or date-granular information.

The application view must:

- Exclude direct identifiers.
- Exclude patient IDs, member IDs, medical-record numbers, claim IDs, and free-text notes.
- Use non-identifying HCP/HCO keys only where authorized.
- Generalize dates to month or another approved period.
- Use ZIP3 only where population threshold requirements are met.
- Suppress small cells, including counts below the organization-approved threshold.
- Prevent re-identification through joins and output combinations.
- Restrict detailed data based on user role and territory assignment.

Example:

```sql
CREATE OR REPLACE SECURE VIEW PHARMA_APP.GOVERNED.V_FACT_PRESCRIPTION_EVENTS_SAFE_HARBOR AS
SELECT
    PRODUCT_ID,
    HCP_MASTER_ID,
    TERRITORY_ID,
    EVENT_MONTH,
    PATIENT_AGE_BAND,
    GEOGRAPHY_ZIP3,
    PRESCRIPTION_EVENT_TYPE,
    COUNT(*) AS PRESCRIPTION_EVENT_COUNT
FROM PHARMA_LAKEHOUSE.PRESCRIPTIONS.FACT_PRESCRIPTION_EVENTS
WHERE EVENT_MONTH <= DATE_TRUNC('MONTH', CURRENT_DATE())
GROUP BY
    PRODUCT_ID,
    HCP_MASTER_ID,
    TERRITORY_ID,
    EVENT_MONTH,
    PATIENT_AGE_BAND,
    GEOGRAPHY_ZIP3,
    PRESCRIPTION_EVENT_TYPE
HAVING COUNT(*) >= 11;
```

The exact Safe Harbor transformation must be approved by Privacy, Security, and the organization’s HIPAA governance process before production use.

---

## 4. Security, identity, and authorization architecture

### 4.1 Authentication

The browser accesses the public SPCS endpoint using the enterprise-approved authentication path:

- Snowflake-native authentication for Snowflake users, or
- Enterprise SSO through a configured external OAuth/security integration.

The frontend sends the authenticated bearer token with API requests:

```http
Authorization: Bearer <enterprise-access-token>
```

NGINX forwards this header unchanged to FastAPI.

FastAPI validates:

- Token signature through the approved issuer JWKS.
- `iss`, `aud`, `exp`, `nbf`, and token signature.
- User identity (`sub`).
- Approved enterprise groups/roles.
- Tenant, business-unit, and brand claims where applicable.

The service-to-Snowflake connection does **not** reuse a browser token. It uses the SPCS mounted service token for controlled server-side Snowflake access.

### 4.2 Authorization

Authorization is evaluated on every API request.

```text
Authenticated user
    -> enterprise groups and claims
    -> application role mapping
    -> allowed brands / business units
    -> allowed territory identifiers
    -> permitted data domains and export capability
    -> governed SQL query with scope predicates
```

Recommended application roles:

| Application role | Typical access |
|---|---|
| `COPILOT_FIELD_USER` | Assigned territory HCP/HCO, approved market-access and aggregated Rx insights. |
| `COPILOT_MARKET_ACCESS_USER` | Payer/formulary analytics within approved product/geography scope. |
| `COPILOT_MEDICAL_USER` | Medical-information content and non-promotional scientific responses. |
| `COPILOT_COMMERCIAL_MANAGER` | Team/region aggregation, subject to approved hierarchy. |
| `COPILOT_MLR_REVIEWER` | Review queue, source traceability, approval/rejection decisions. |
| `COPILOT_AUDITOR` | Read-only audit evidence; no operational data export. |
| `COPILOT_ADMIN` | Configuration, policy, prompt/template lifecycle, no unrestricted patient data. |

### 4.3 Snowflake service connection

The FastAPI backend uses the SPCS-provided OAuth token.

```python
from pathlib import Path
import os
import snowflake.connector

def get_snowflake_connection():
    token = Path("/snowflake/session/token").read_text(encoding="utf-8").strip()

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        host=os.environ["SNOWFLAKE_HOST"],
        authenticator="oauth",
        token=token,
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        role=os.environ["SNOWFLAKE_ROLE"],
        session_parameters={
            "QUERY_TAG": "enterprise-pharma-copilot-api"
        },
    )
```

The implementation must use parameterized SQL bindings. User-supplied text must never be concatenated into SQL identifiers, SQL predicates, or query strings.

---

## 5. FastAPI service responsibilities

The FastAPI container is the sole enterprise gateway to Snowflake data and AI operations.

### 5.1 Gateway responsibilities

1. Validate enterprise access tokens.
2. Resolve user authorization scope.
3. Search HCP/HCO master data.
4. Enforce territory and commercial alignment policies.
5. Retrieve market access and prescription insights.
6. Apply minimum-cell-count and safe-harbor output controls.
7. Retrieve approved content and citations.
8. Call approved Snowflake Cortex models or approved model gateways.
9. Enforce prompt-injection defenses and output safety controls.
10. Ensure fair balance for promotional/product content.
11. Persist immutable-style audit evidence in Snowflake.
12. Stream grounded responses to the frontend with SSE.
13. Prevent unauthorized exports, unapproved disclosures, and cross-territory access.

### 5.2 Required API dependencies

```text
fastapi
uvicorn[standard]
pydantic
pydantic-settings
snowflake-connector-python
snowflake-snowpark-python
pyjwt[crypto]
httpx
structlog
orjson
sse-starlette
tenacity
prometheus-client
opentelemetry-api
opentelemetry-sdk
```

---

## 6. React frontend architecture

### 6.1 Technology stack

| Category | Technology |
|---|---|
| Framework | React 18+ |
| Language | TypeScript |
| Build | Vite |
| Styling | Tailwind CSS or controlled Vanilla CSS design system |
| Data fetching | TanStack Query or equivalent |
| Routing | React Router |
| Streaming | Server-Sent Events client |
| Visualization | Recharts, ECharts, or approved chart library |
| Accessibility | WCAG 2.1 AA-oriented semantic components, keyboard support, ARIA labels |
| Audit UX | Request IDs, citations, response classifications, and escalation indicators visible to authorized users |

### 6.2 Primary screens

1. **Copilot workspace**
   - Conversational prompt interface.
   - Streaming response rendering.
   - Citations, data-source labels, response confidence/disposition.
   - “Request medical review” workflow.
   - Safety/fair-balance panel where product discussion is detected.

2. **HCP/HCO explorer**
   - Search by name, identifier, specialty, HCO, state, or territory.
   - Role-scoped profile summary.
   - Territory alignment visibility.
   - No direct patient-level information.

3. **Market access dashboard**
   - Formulary status, tier distribution, restrictions, PA trends.
   - Payer/geography/product filters constrained by authorization scope.

4. **Prescription analytics**
   - Aggregated and de-identified trends only.
   - Small-cell suppression notice.
   - No raw prescription-event export.

5. **Review and audit workspace**
   - Available only to MLR reviewers/auditors.
   - Review response content, source citations, model/prompt version, and audit IDs.

---

## 7. React-to-FastAPI API contract

All browser API calls use relative paths under `/api/v1`. This avoids hardcoding an SPCS endpoint hostname in the Vite build.

Base path:

```text
/api/v1
```

Required headers:

```http
Authorization: Bearer <enterprise-access-token>
Content-Type: application/json
X-Correlation-ID: <uuid>
```

The backend generates a correlation ID when absent and returns it on every response.

### 7.1 Common response envelope

```json
{
  "requestId": "4e12225b-9a77-4582-86dc-aa4df41cf318",
  "data": {},
  "meta": {
    "generatedAt": "2025-03-08T12:00:00Z",
    "sourceSystems": ["PHARMA_APP.GOVERNED.V_MDM_HCP_MASTER"]
  }
}
```

### 7.2 Error response envelope

```json
{
  "requestId": "4e12225b-9a77-4582-86dc-aa4df41cf318",
  "error": {
    "code": "TERRITORY_ACCESS_DENIED",
    "message": "You are not authorized to access this territory.",
    "retryable": false
  }
}
```

### 7.3 API endpoints

#### Health

```http
GET /api/v1/health/live
GET /api/v1/health/ready
```

`/health/live` confirms process availability.  
`/health/ready` confirms that configuration is valid and a Snowflake connectivity check has succeeded.

Example response:

```json
{
  "requestId": "d8b2f0b9-095f-4338-91df-e158cd3f2942",
  "data": {
    "status": "ready",
    "service": "enterprise-pharma-copilot-api",
    "version": "1.0.0"
  }
}
```

#### Current user and authorization scope

```http
GET /api/v1/me
```

Response:

```json
{
  "requestId": "ec0a3d8b-d817-4408-a74f-5971de1fa027",
  "data": {
    "userId": "enterprise-user-id",
    "displayName": "Authorized User",
    "roles": ["COPILOT_FIELD_USER"],
    "authorizedTerritoryIds": ["TERR-NE-001", "TERR-NE-002"],
    "authorizedBrands": ["PRODUCT_A"],
    "permissions": [
      "hcp:read",
      "market_access:read",
      "prescription_aggregate:read",
      "copilot:query"
    ]
  }
}
```

#### HCP search

```http
GET /api/v1/hcps?query={query}&territoryId={territoryId}&limit=25
```

Response:

```json
{
  "requestId": "1e2eb9eb-9225-4d57-b9c8-8ad2ce3ba429",
  "data": {
    "items": [
      {
        "hcpMasterId": "HCP-100482",
        "displayName": "Dr. Example",
        "specialty": "Cardiology",
        "city": "Boston",
        "state": "MA",
        "assignedTerritoryIds": ["TERR-NE-001"]
      }
    ],
    "nextCursor": null
  }
}
```

#### HCP profile

```http
GET /api/v1/hcps/{hcpMasterId}
```

The backend must validate that the user is authorized for the HCP’s active territory alignment before returning a profile.

#### HCP market-access summary

```http
GET /api/v1/hcps/{hcpMasterId}/market-access?productId={productId}
```

Response includes payer/formulary information only within the requester’s role and geographic authorization.

#### Prescription trend

```http
GET /api/v1/hcps/{hcpMasterId}/prescription-trend?productId={productId}&fromMonth=YYYY-MM&toMonth=YYYY-MM
```

Response:

```json
{
  "requestId": "c89e6f34-89b7-4db7-8e18-a5de61df93f7",
  "data": {
    "hcpMasterId": "HCP-100482",
    "productId": "PRODUCT_A",
    "granularity": "MONTH",
    "isDeidentified": true,
    "smallCellSuppressionApplied": true,
    "series": [
      {
        "month": "2025-01",
        "prescriptionEventCount": 42
      }
    ]
  }
}
```

#### Copilot conversation creation

```http
POST /api/v1/copilot/conversations
```

Request:

```json
{
  "context": {
    "hcpMasterId": "HCP-100482",
    "productId": "PRODUCT_A",
    "territoryId": "TERR-NE-001"
  }
}
```

Response:

```json
{
  "requestId": "9f6f4e31-c5e0-47a8-98e0-9d923604e916",
  "data": {
    "conversationId": "conv_01JNM2M1VY6NANP1G7RG7D87K6"
  }
}
```

#### Copilot streaming message

```http
POST /api/v1/copilot/conversations/{conversationId}/messages/stream
Accept: text/event-stream
```

Request:

```json
{
  "message": "Summarize formulary access barriers for this HCP's territory.",
  "context": {
    "hcpMasterId": "HCP-100482",
    "productId": "PRODUCT_A",
    "territoryId": "TERR-NE-001"
  }
}
```

SSE event types:

```text
event: status
event: citation
event: token
event: safety
event: completed
event: error
```

Example citation event:

```text
event: citation
data: {"citationId":"src_01","title":"Formulary Coverage, January 2025","sourceType":"governed_data","sourceObject":"PHARMA_APP.GOVERNED.V_FACT_FORMULARY_TIER_COVERAGE","asOfDate":"2025-01-31"}
```

Example completed event:

```text
event: completed
data: {
  "responseId":"rsp_01JNM2VB7VC5F9VDV4T7JQ0B76",
  "classification":"ANALYTICAL_NON_PROMOTIONAL",
  "requiresReview":false,
  "auditEventId":"aud_01JNM2VBVFD5FHKJQ8TQFWG3M8",
  "citations":["src_01"]
}
```

#### Medical/legal/regulatory review request

```http
POST /api/v1/reviews
```

Request:

```json
{
  "responseId": "rsp_01JNM2VB7VC5F9VDV4T7JQ0B76",
  "reason": "USER_REQUESTED_REVIEW",
  "comment": "Please review response before field use."
}
```

#### Audit evidence lookup

```http
GET /api/v1/audit/events/{auditEventId}
```

This endpoint is restricted to `COPILOT_AUDITOR`, `COPILOT_MLR_REVIEWER`, and designated administrators.

---

## 8. Copilot orchestration and content controls

### 8.1 Processing sequence

```text
1. Validate user token.
2. Resolve application role and authorization scope.
3. Classify request:
   - analytics
   - market access
   - medical information
   - promotional/product claim
   - prohibited / unsupported
4. Detect prompt injection, data-exfiltration attempts, and unsafe requests.
5. Retrieve only authorized data and approved content.
6. Apply de-identification, small-cell suppression, and scoped aggregation.
7. Construct a bounded model prompt:
   - user question
   - approved retrieved evidence
   - policy constraints
   - citation requirements
   - no unsupported claim instructions
8. Invoke Snowflake Cortex or approved model gateway.
9. Validate output:
   - source citation presence
   - prohibited claim detection
   - fair-balance requirements
   - hallucination/unsupported-statement checks
   - PHI/PII leakage checks
10. Return answer, citations, classification, disposition, and audit ID.
11. Persist audit evidence.
```

### 8.2 Fair Balance and OPDP controls

For content that discusses a product, indication, efficacy, risk, safety, or comparative claim:

- The response must be classified as promotional, medical, or analytical before display.
- Promotional content must only use claims present in the approved-content repository.
- The response must present material risks and limitations with comparable prominence to benefit statements.
- Content must include approved indication and safety references where applicable.
- The system must not create new efficacy, superiority, comparative, or off-label claims.
- If approved evidence is absent, the gateway must decline or route the request to Medical Affairs/MLR review.
- The frontend must visibly distinguish:
  - analytical data summaries,
  - approved promotional content,
  - medical-information content,
  - pending-review content.

A model-generated answer is not an approved promotional asset merely because it has passed automated checks. Formal MLR workflow and validation remain required.

---

## 9. Audit trail and 21 CFR Part 11 support controls

The architecture supports Part 11-oriented technical controls but does not by itself establish compliance. Production use requires validation, SOPs, training, change control, access reviews, and documented system qualification.

### 9.1 Audit event schema

```sql
CREATE TABLE IF NOT EXISTS PHARMA_APP.AUDIT.COPILOT_AUDIT_EVENT (
    AUDIT_EVENT_ID STRING NOT NULL,
    EVENT_TS TIMESTAMP_TZ NOT NULL,
    CORRELATION_ID STRING NOT NULL,
    USER_ID STRING NOT NULL,
    USER_ROLE_VARIANT VARIANT NOT NULL,
    ACTION STRING NOT NULL,
    CONVERSATION_ID STRING,
    RESPONSE_ID STRING,
    REQUEST_HASH STRING,
    REQUEST_CLASSIFICATION STRING,
    AUTHORIZATION_SCOPE_HASH STRING,
    SOURCE_OBJECTS VARIANT,
    SOURCE_QUERY_IDS VARIANT,
    PROMPT_TEMPLATE_VERSION STRING,
    MODEL_PROVIDER STRING,
    MODEL_NAME STRING,
    MODEL_VERSION STRING,
    RESPONSE_HASH STRING,
    OUTPUT_CLASSIFICATION STRING,
    OUTPUT_DISPOSITION STRING,
    REVIEW_STATUS STRING,
    ERROR_CODE STRING,
    CLIENT_IP_HASH STRING,
    CREATED_BY_SERVICE STRING NOT NULL,
    PRIMARY KEY (AUDIT_EVENT_ID)
)
DATA_RETENTION_TIME_IN_DAYS = 2555;
```

### 9.2 Audit requirements

- Audit events are append-only for the application service role.
- Application users cannot update or delete audit records.
- Audit access is segregated from operational use.
- The system records timestamp, user identity, action, source objects, model version, prompt version, result disposition, and review status.
- Request and response values should be hashed or redacted where retaining raw content would create privacy or retention risk.
- Validated electronic-signature controls are required for approval actions if the workflow is used as a regulated approval record.
- All production changes to prompts, model versions, approval policy, RBAC mappings, and governed views require controlled change management.

---

# 10. SPCS multi-container service specification

File: `infra/spcs/spcs_service_spec.yaml`

```yaml
spec:
  containers:
    - name: frontend
      image: /PHARMA_APP/PLATFORM/IMAGE_REPOSITORY/enterprise-pharma-copilot-frontend:1.0.0
      env:
        NGINX_PORT: "8080"
        API_UPSTREAM_HOST: "127.0.0.1"
        API_UPSTREAM_PORT: "8000"
        APP_ENV: "production"
      resources:
        requests:
          cpu: "0.5"
          memory: "1Gi"
        limits:
          cpu: "1"
          memory: "2Gi"
      readinessProbe:
        port: 8080
        path: /healthz
        initialDelaySeconds: 10
        periodSeconds: 10
        failureThreshold: 3

    - name: api-gateway
      image: /PHARMA_APP/PLATFORM/IMAGE_REPOSITORY/enterprise-pharma-copilot-api:1.0.0
      env:
        APP_ENV: "production"
        LOG_LEVEL: "INFO"
        API_HOST: "0.0.0.0"
        API_PORT: "8000"
        API_ROOT_PATH: "/api"

        # Snowflake connection configuration.
        # The service OAuth token is read from /snowflake/session/token.
        SNOWFLAKE_ACCOUNT: "<account_locator>"
        SNOWFLAKE_HOST: "<account_locator>.<region_id>.<cloud>.snowflakecomputing.com"
        SNOWFLAKE_WAREHOUSE: "PHARMA_COPILOT_WH"
        SNOWFLAKE_DATABASE: "PHARMA_APP"
        SNOWFLAKE_SCHEMA: "GOVERNED"
        SNOWFLAKE_ROLE: "PHARMA_COPILOT_SERVICE_ROLE"

        # Fully qualified governed data objects.
        HCP_VIEW: "PHARMA_APP.GOVERNED.V_MDM_HCP_MASTER"
        HCO_VIEW: "PHARMA_APP.GOVERNED.V_MDM_HCO_MASTER"
        TERRITORY_VIEW: "PHARMA_APP.GOVERNED.V_DIM_TERRITORY"
        HCP_TERRITORY_VIEW: "PHARMA_APP.GOVERNED.V_MAP_HCP_TERRITORY_ALIGNMENT"
        FORMULARY_VIEW: "PHARMA_APP.GOVERNED.V_FACT_FORMULARY_TIER_COVERAGE"
        PA_DENIALS_VIEW: "PHARMA_APP.GOVERNED.V_FACT_PA_DENIALS"
        PRESCRIPTION_VIEW: "PHARMA_APP.GOVERNED.V_FACT_PRESCRIPTION_EVENTS_SAFE_HARBOR"
        AUDIT_TABLE: "PHARMA_APP.AUDIT.COPILOT_AUDIT_EVENT"

        # AI / approved-content controls.
        CORTEX_MODEL: "<approved_cortex_model>"
        APPROVED_CONTENT_VIEW: "PHARMA_APP.GOVERNED.V_APPROVED_CONTENT"
        CONTENT_POLICY_VIEW: "PHARMA_APP.GOVERNED.V_COPILOT_CONTENT_POLICY"
        PROMPT_TEMPLATE_VERSION: "1.0.0"
        MINIMUM_CELL_COUNT: "11"

        # Enterprise OAuth/JWT validation configuration.
        AUTH_ISSUER: "https://<enterprise-idp>/"
        AUTH_AUDIENCE: "enterprise-pharma-copilot"
        AUTH_JWKS_URL: "https://<enterprise-idp>/.well-known/jwks.json"
        AUTH_REQUIRED_SCOPES: "copilot.read"

        # Application controls.
        CORS_ALLOWED_ORIGINS: "https://<generated-spcs-frontend-endpoint>"
        REQUEST_MAX_BYTES: "1048576"
        COPILOT_MAX_MESSAGE_CHARS: "8000"
        SSE_HEARTBEAT_SECONDS: "15"
        QUERY_TIMEOUT_SECONDS: "60"
        AUDIT_ENABLED: "true"
        PHI_OUTPUT_BLOCKING_ENABLED: "true"
        FAIR_BALANCE_ENFORCEMENT_ENABLED: "true"
      resources:
        requests:
          cpu: "1"
          memory: "2Gi"
        limits:
          cpu: "2"
          memory: "4Gi"
      readinessProbe:
        port: 8000
        path: /api/v1/health/ready
        initialDelaySeconds: 20
        periodSeconds: 10
        failureThreshold: 6

  endpoints:
    - name: pharma-copilot-ui
      port: 8080
      public: true

    - name: pharma-copilot-api-internal
      port: 8000
      public: false
```

## 10.1 Port mappings

| Container | Listens on | Exposure | Purpose |
|---|---:|---|---|
| `frontend` | `8080` | Public SPCS endpoint: `pharma-copilot-ui` | React SPA, static assets, NGINX reverse proxy. |
| `api-gateway` | `8000` | Private SPCS endpoint: `pharma-copilot-api-internal` | FastAPI gateway, Snowflake retrieval, AI orchestration, audit logging. |
| NGINX to FastAPI | `127.0.0.1:8000` | Internal same-instance connection | `/api/*` request proxying and SSE streaming. |

The generated external URL is not known until service creation. Obtain it after deployment:

```sql
SHOW ENDPOINTS IN SERVICE PHARMA_APP.PLATFORM.ENTERPRISE_PHARMA_COPILOT;
```

Use the returned URL as the enterprise application entry point and, once known, update the `CORS_ALLOWED_ORIGINS` configuration if browser-origin enforcement is enabled.

---

# 11. NGINX configuration

File: `frontend/nginx/default.conf`

```nginx
server {
    listen 8080;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

    location = /healthz {
        access_log off;
        default_type application/json;
        return 200 '{"status":"ok"}';
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Correlation-ID $request_id;

        # Preserve caller identity token for FastAPI validation.
        proxy_set_header Authorization $http_authorization;

        # Required for SSE Copilot streaming.
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
        chunked_transfer_encoding on;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

# 12. Container build specifications

## 12.1 Frontend Dockerfile

File: `frontend/Dockerfile`

```dockerfile
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

RUN chown -R appuser:appgroup /usr/share/nginx/html \
    && touch /var/run/nginx.pid \
    && chown -R appuser:appgroup /var/cache/nginx /var/run/nginx.pid

USER appuser

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
```

## 12.2 FastAPI Dockerfile

File: `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

RUN groupadd --system appgroup \
    && useradd --system --gid appgroup --create-home appuser

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY app ./app

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
```

---

# 13. Recommended repository layout

```text
enterprise-pharma-copilot/
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── copilot.ts
│   │   │   ├── hcps.ts
│   │   │   └── marketAccess.ts
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── styles/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── nginx/default.conf
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       ├── health.py
│   │   │       ├── users.py
│   │   │       ├── hcp.py
│   │   │       ├── market_access.py
│   │   │       ├── prescriptions.py
│   │   │       ├── copilot.py
│   │   │       ├── reviews.py
│   │   │       └── audit.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── auth.py
│   │   │   ├── authorization.py
│   │   │   ├── logging.py
│   │   │   └── errors.py
│   │   ├── models/
│   │   │   ├── hcp.py
│   │   │   ├── copilot.py
│   │   │   ├── audit.py
│   │   │   └── review.py
│   │   ├── repositories/
│   │   │   ├── snowflake_connection.py
│   │   │   ├── hcp_repository.py
│   │   │   ├── market_access_repository.py
│   │   │   ├── prescription_repository.py
│   │   │   └── audit_repository.py
│   │   ├── services/
│   │   │   ├── copilot_orchestrator.py
│   │   │   ├── retrieval_service.py
│   │   │   ├── content_policy_service.py
│   │   │   ├── fair_balance_service.py
│   │   │   ├── phi_protection_service.py
│   │   │   └── review_service.py
│   │   └── sql/
│   │       ├── hcp_search.sql
│   │       ├── territory_scope.sql
│   │       ├── formulary_summary.sql
│   │       └── prescription_trend.sql
│   ├── Dockerfile
│   └── requirements.txt
│
├── infra/
│   ├── spcs/
│   │   └── spcs_service_spec.yaml
│   ├── snowflake/
│   │   ├── 001_roles_and_grants.sql
│   │   ├── 002_governed_views.sql
│   │   ├── 003_row_access_policies.sql
│   │   ├── 004_masking_policies.sql
│   │   ├── 005_audit_tables.sql
│   │   ├── 006_service_and_compute_pool.sql
│   │   └── 007_network_and_external_access.sql
│   └── ci/
│       ├── build_images.sh
│       ├── security_scan.sh
│       └── deploy_spcs.sh
│
├── docs/
│   ├── api-contract.md
│   ├── threat-model.md
│   ├── validation-plan.md
│   ├── data-classification.md
│   └── mlr-content-governance.md
└── README.md
```

---

# 14. Snowflake deployment sequence

## Step 1: Create operational roles

Create separate ownership, deployment, runtime, audit, and read-only roles. The service role must not own production data objects.

```sql
CREATE ROLE IF NOT EXISTS PHARMA_COPILOT_SERVICE_ROLE;
CREATE ROLE IF NOT EXISTS PHARMA_COPILOT_AUDITOR_ROLE;
CREATE ROLE IF NOT EXISTS PHARMA_COPILOT_DEPLOYER_ROLE;
```

## Step 2: Create warehouse, image repository, stage, and compute pool

```sql
CREATE WAREHOUSE IF NOT EXISTS PHARMA_COPILOT_WH
    WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

CREATE IMAGE REPOSITORY IF NOT EXISTS PHARMA_APP.PLATFORM.IMAGE_REPOSITORY;

CREATE STAGE IF NOT EXISTS PHARMA_APP.PLATFORM.SPCS_SPEC_STAGE
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

CREATE COMPUTE POOL IF NOT EXISTS PHARMA_COPILOT_POOL
    MIN_NODES = 1
    MAX_NODES = 3
    INSTANCE_FAMILY = CPU_X64_XS;
```

The actual instance family must be selected based on expected concurrency, response latency, Cortex usage, and Snowflake account availability.

## Step 3: Build and publish immutable container images

Images should be versioned with an immutable release identifier, for example:

```text
enterprise-pharma-copilot-frontend:1.0.0
enterprise-pharma-copilot-api:1.0.0
```

Do not deploy production using mutable tags such as `latest`.

## Step 4: Upload the SPCS specification

```sql
PUT file://infra/spcs/spcs_service_spec.yaml
  @PHARMA_APP.PLATFORM.SPCS_SPEC_STAGE
  AUTO_COMPRESS = FALSE
  OVERWRITE = TRUE;
```

## Step 5: Create the SPCS service

```sql
CREATE SERVICE IF NOT EXISTS PHARMA_APP.PLATFORM.ENTERPRISE_PHARMA_COPILOT
  IN COMPUTE POOL PHARMA_COPILOT_POOL
  FROM @PHARMA_APP.PLATFORM.SPCS_SPEC_STAGE
  SPECIFICATION_FILE = 'spcs_service_spec.yaml'
  MIN_INSTANCES = 1
  MAX_INSTANCES = 3;
```

## Step 6: Verify deployment evidence

```sql
SHOW SERVICES IN SCHEMA PHARMA_APP.PLATFORM;

SHOW SERVICE CONTAINERS IN SERVICE PHARMA_APP.PLATFORM.ENTERPRISE_PHARMA_COPILOT;

SHOW ENDPOINTS IN SERVICE PHARMA_APP.PLATFORM.ENTERPRISE_PHARMA_COPILOT;
```

The deployment is operational only after:

- Both containers show healthy status.
- Frontend readiness probe succeeds on port `8080`.
- API readiness probe succeeds on port `8000`.
- FastAPI successfully authenticates to Snowflake through `/snowflake/session/token`.
- The service role can query governed views but cannot query prohibited base objects.
- Authorization tests confirm cross-territory access is denied.
- Safe Harbor and small-cell suppression tests pass.
- Audit records are created for queries and Copilot interactions.
- MLR/fair-balance controls are validated for product-related prompts.

---

# 15. Production acceptance criteria

The following should be treated as release gates:

1. **Security**
   - No Snowflake passwords, private keys, PHI, or API secrets are baked into images.
   - Token validation, expiration handling, issuer/audience validation, and authorization tests pass.
   - API is not publicly exposed independently of the frontend endpoint.
   - Dependency, image, and source-code security scans pass.

2. **Data governance**
   - Service role has access only to approved governed views.
   - Row access, masking, and territory filtering are tested.
   - Prescription output is Safe Harbor compliant and small-cell suppression is enforced.
   - Export controls are tested.

3. **AI governance**
   - Every response has a classification and audit identifier.
   - Data-grounded answers provide provenance.
   - Unsupported product claims are blocked or routed for review.
   - Fair-balance policy behavior is tested with positive and negative scenarios.
   - Prompt-injection and data-exfiltration tests pass.

4. **Operational resilience**
   - Readiness/liveness checks are functioning.
   - API timeouts and Snowflake transient errors use bounded retry behavior.
   - Correlation IDs appear in frontend, API, Snowflake query tags, and audit records.
   - Load testing validates configured SPCS minimum and maximum instances.

5. **Validation and compliance**
   - Requirements, design specifications, risk assessment, test evidence, and traceability matrix are completed.
   - Approval and audit workflows are validated under the organization’s Part 11 quality system where applicable.
   - Privacy, Security, Medical, Legal, Regulatory, and Commercial governance approval is documented before production release.