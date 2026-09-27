Below is a production-oriented `api/main.py` implementation for the private FastAPI container in SPCS. It assumes Snowflake governed secure views exist for the configured view names and that NGINX proxies authenticated requests to this service at `127.0.0.1:8000`.

```python
# api/main.py
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import time
import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime
from decimal import Decimal
from functools import lru_cache
from typing import Any, Literal

import anyio
import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jwt import PyJWKClient
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from snowflake.connector import connect
from snowflake.connector.errors import DatabaseError, OperationalError, ProgrammingError

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s %(message)s",
)
logger = logging.getLogger("enterprise_pharma_copilot")

class RequestIdLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True

for handler in logging.getLogger().handlers:
    handler.addFilter(RequestIdLogFilter())

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_$\.]*$")
_MODEL_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
_HCP_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

class Settings(BaseSettings):
    """
    Production settings are supplied through SPCS service environment variables
    and Snowflake secrets mounted into the FastAPI container.

    No credentials, PHI, prompt text, access tokens, or Snowflake query results
    are written to application logs.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "production"
    log_level: str = "INFO"

    # Inbound OAuth/JWT authentication
    jwt_jwks_url: str | None = None
    jwt_issuer: str | None = None
    jwt_audience: str | None = None
    allow_unauthenticated_development: bool = False

    # Snowflake connection
    snowflake_account: str
    snowflake_user: str
    snowflake_warehouse: str
    snowflake_database: str
    snowflake_schema: str
    snowflake_role: str

    # Prefer key-pair authentication in SPCS. OAuth is supported when supplied.
    snowflake_private_key_file: str | None = None
    snowflake_private_key_file_pwd: str | None = None
    snowflake_oauth_token: str | None = None

    # Query controls
    snowflake_query_timeout_seconds: int = Field(default=25, ge=1, le=120)
    api_query_timeout_seconds: int = Field(default=30, ge=1, le=130)
    max_territories: int = Field(default=1000, ge=1, le=5000)
    max_copilot_prompt_chars: int = Field(default=2000, ge=50, le=10000)

    # Governed secure views. Do not configure these with user-controlled values.
    kpi_view: str = "ANALYTICS_GOVERNED.COMMERCIAL_KPI_V"
    territory_view: str = "ANALYTICS_GOVERNED.TERRITORY_ALIGNMENT_V"
    hcp_view: str = "ANALYTICS_GOVERNED.HCP_GOLDEN_RECORD_V"
    denial_view: str = "ANALYTICS_GOVERNED.PA_DENIAL_DIAGNOSTICS_V"
    approved_content_view: str = "ANALYTICS_GOVERNED.COPILOT_APPROVED_CONTENT_V"
    audit_view: str = "ANALYTICS_GOVERNED.COPILOT_AUDIT_LOG"

    # Cortex model approved by the organization.
    cortex_model: str = "snowflake-arctic"

    # CORS is ordinarily unnecessary when NGINX serves the SPA and proxies /api.
    cors_allowed_origins: str = ""

    @field_validator(
        "kpi_view",
        "territory_view",
        "hcp_view",
        "denial_view",
        "approved_content_view",
        "audit_view",
    )
    @classmethod
    def validate_snowflake_identifier(cls, value: str) -> str:
        if not _IDENTIFIER_RE.fullmatch(value):
            raise ValueError("Configured Snowflake object name is invalid")
        return value

    @field_validator("cortex_model")
    @classmethod
    def validate_cortex_model(cls, value: str) -> str:
        if not _MODEL_RE.fullmatch(value):
            raise ValueError("Configured Cortex model name is invalid")
        return value

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        if self.app_env != "development":
            if self.allow_unauthenticated_development:
                raise ValueError(
                    "allow_unauthenticated_development must never be enabled outside development"
                )
            if not (self.jwt_jwks_url and self.jwt_issuer and self.jwt_audience):
                raise ValueError(
                    "JWT_JWKS_URL, JWT_ISSUER, and JWT_AUDIENCE are required in production"
                )

        if not self.snowflake_oauth_token and not self.snowflake_private_key_file:
            raise ValueError(
                "Configure SNOWFLAKE_PRIVATE_KEY_FILE or SNOWFLAKE_OAUTH_TOKEN"
            )

        return self

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]

@lru_cache
def get_settings() -> Settings:
    return Settings()

# ------------------------------------------------------------------------------
# API models
# ------------------------------------------------------------------------------

class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

class HealthResponse(APIModel):
    status: Literal["ok", "degraded"]
    spcs_ready: bool
    snowflake_ready: bool
    timestamp: datetime

class CommercialKPIs(APIModel):
    as_of_date: date | None = None
    trx: int = Field(ge=0)
    nrx: int = Field(ge=0)
    target_hcps: int = Field(ge=0)
    pa_denial_rate: float = Field(ge=0, le=1)
    net_revenue: float

class Territory(APIModel):
    territory_id: str
    territory_name: str
    area_of_interest: str | None = None
    representative_name: str | None = None
    prescriber_count: int = Field(ge=0)

class TerritoryListResponse(APIModel):
    territories: list[Territory]
    count: int

class HCPGoldenRecord(APIModel):
    hcp_id: str
    npi: str | None = None
    full_name: str
    specialty: str | None = None
    decile: int | None = Field(default=None, ge=1, le=10)
    territory_id: str | None = None
    territory_name: str | None = None
    area_of_interest: str | None = None
    representative_name: str | None = None
    recent_rx_volume: int = Field(ge=0)
    rx_period_start: date | None = None
    rx_period_end: date | None = None
    record_last_updated_at: datetime | None = None

class DenialDiagnostic(APIModel):
    rejection_code: str
    rejection_description: str | None = None
    denial_count: int = Field(ge=0)
    denial_rate: float = Field(ge=0, le=1)
    recoverable_revenue: float = Field(ge=0)
    recommended_action: str | None = None

class DenialDiagnosticsResponse(APIModel):
    as_of_date: date | None = None
    diagnostics: list[DenialDiagnostic]
    total_recoverable_revenue: float = Field(ge=0)

class CopilotQueryRequest(APIModel):
    prompt: str = Field(min_length=1, max_length=10000)
    product_name: str | None = Field(default=None, max_length=150)

    @field_validator("prompt")
    @classmethod
    def normalize_prompt(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Prompt cannot be blank")
        return value

class CopilotCitation(APIModel):
    content_id: str
    title: str
    version: str | None = None
    effective_date: date | None = None

class CopilotQueryResponse(APIModel):
    request_id: str
    status: Literal["answered", "intercepted", "no_approved_content"]
    response: str
    fair_balance_required: bool
    citations: list[CopilotCitation] = Field(default_factory=list)

class ErrorResponse(APIModel):
    detail: str
    request_id: str | None = None

# ------------------------------------------------------------------------------
# Identity and authorization
# ------------------------------------------------------------------------------

class Principal(APIModel):
    subject: str
    scopes: set[str] = Field(default_factory=set)
    roles: set[str] = Field(default_factory=set)

def _extract_string_set(claims: dict[str, Any], *names: str) -> set[str]:
    values: set[str] = set()

    for name in names:
        raw = claims.get(name)
        if isinstance(raw, str):
            values.update(raw.split())
        elif isinstance(raw, list):
            values.update(str(item) for item in raw if isinstance(item, (str, int)))

    return values

class JWTAuthenticator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.jwk_client = (
            PyJWKClient(settings.jwt_jwks_url)
            if settings.jwt_jwks_url
            else None
        )

    def validate(self, token: str) -> Principal:
        if not self.jwk_client or not self.settings.jwt_issuer or not self.settings.jwt_audience:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service is not configured",
            )

        try:
            signing_key = self.jwk_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"],
                audience=self.settings.jwt_audience,
                issuer=self.settings.jwt_issuer,
                options={
                    "require": ["exp", "iat", "sub", "iss", "aud"],
                    "verify_signature": True,
                },
            )
        except jwt.PyJWTError as exc:
            logger.info("Rejected invalid bearer token: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token subject is invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return Principal(
            subject=subject,
            scopes=_extract_string_set(claims, "scope", "scp", "scopes"),
            roles=_extract_string_set(claims, "roles", "role", "groups"),
        )

async def get_principal(request: Request) -> Principal:
    settings: Settings = request.app.state.settings

    if (
        settings.app_env == "development"
        and settings.allow_unauthenticated_development
    ):
        return Principal(
            subject="development-user",
            scopes={
                "commercial.read",
                "hcp.read",
                "market_access.read",
                "copilot.use",
            },
            roles={"PHARMA_COPILOT_ADMIN"},
        )

    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return request.app.state.authenticator.validate(token)

def require_scope(required_scope: str):
    async def dependency(principal: Principal = Depends(get_principal)) -> Principal:
        # Administrative access remains explicit rather than relying on an
        # untrusted client-provided role header.
        if (
            required_scope not in principal.scopes
            and "PHARMA_COPILOT_ADMIN" not in principal.roles
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient authorization",
            )
        return principal

    return dependency

# ------------------------------------------------------------------------------
# Snowflake gateway
# ------------------------------------------------------------------------------

class SnowflakeGateway:
    """
    Snowflake's Python connector is synchronous. Calls are isolated in worker
    threads so FastAPI's asyncio event loop remains non-blocking.

    Every request uses a new connection. This avoids sharing Snowflake cursors
    or connector sessions between concurrent coroutines and preserves session
    role isolation.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _connection_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "account": self.settings.snowflake_account,
            "user": self.settings.snowflake_user,
            "warehouse": self.settings.snowflake_warehouse,
            "database": self.settings.snowflake_database,
            "schema": self.settings.snowflake_schema,
            "role": self.settings.snowflake_role,
            "paramstyle": "qmark",
            "login_timeout": 15,
            "network_timeout": self.settings.snowflake_query_timeout_seconds,
            "session_parameters": {
                "QUERY_TAG": "enterprise-pharma-copilot-api",
                "STATEMENT_TIMEOUT_IN_SECONDS": self.settings.snowflake_query_timeout_seconds,
            },
        }

        if self.settings.snowflake_oauth_token:
            kwargs.update(
                {
                    "authenticator": "oauth",
                    "token": self.settings.snowflake_oauth_token,
                }
            )
        else:
            kwargs.update(
                {
                    "authenticator": "SNOWFLAKE_JWT",
                    "private_key_file": self.settings.snowflake_private_key_file,
                    "private_key_file_pwd": self.settings.snowflake_private_key_file_pwd,
                }
            )

        return kwargs

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (datetime, date)):
            return value
        return value

    def _execute_sync(
        self,
        sql: str,
        params: tuple[Any, ...] = (),
    ) -> list[dict[str, Any]]:
        connection = None
        cursor = None

        try:
            connection = connect(**self._connection_kwargs())
            cursor = connection.cursor()
            cursor.execute(sql, params)

            if cursor.description is None:
                return []

            columns = [column[0].upper() for column in cursor.description]
            rows = cursor.fetchall()

            return [
                {
                    column: self._normalize_value(value)
                    for column, value in zip(columns, row, strict=True)
                }
                for row in rows
            ]
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

    async def execute(
        self,
        sql: str,
        params: tuple[Any, ...] = (),
    ) -> list[dict[str, Any]]:
        try:
            return await asyncio.wait_for(
                anyio.to_thread.run_sync(self._execute_sync, sql, params),
                timeout=self.settings.api_query_timeout_seconds,
            )
        except TimeoutError as exc:
            logger.warning("Snowflake operation timed out")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Data service timed out",
            ) from exc
        except (DatabaseError, OperationalError, ProgrammingError) as exc:
            logger.error("Snowflake operation failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Data service is temporarily unavailable",
            ) from exc

    async def ping(self) -> bool:
        try:
            rows = await self.execute("SELECT 1 AS READY")
            return bool(rows and rows[0].get("READY") == 1)
        except HTTPException:
            return False

# ------------------------------------------------------------------------------
# Audit logging
# ------------------------------------------------------------------------------

def request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "-")

def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

async def write_audit_event(
    request: Request,
    principal: Principal,
    *,
    action: str,
    resource: str,
    outcome: str,
    details: dict[str, Any] | None = None,
    fail_closed: bool = True,
) -> None:
    """
    Audit records intentionally contain metadata and hashes only.

    Raw prompts, generated output, access tokens, patient identifiers, and
    detailed HCP content are not persisted in the application audit payload.
    Snowflake retention, row access, and immutable audit controls must be
    configured on the audit target by the platform team.
    """
    settings: Settings = request.app.state.settings
    db: SnowflakeGateway = request.app.state.snowflake

    safe_details = json.dumps(details or {}, separators=(",", ":"), default=str)
    sql = f"""
        INSERT INTO {settings.audit_view}
            (
                EVENT_TS,
                REQUEST_ID,
                SUBJECT,
                ACTION,
                RESOURCE,
                OUTCOME,
                DETAILS
            )
        SELECT
            CURRENT_TIMESTAMP(),
            ?,
            ?,
            ?,
            ?,
            ?,
            PARSE_JSON(?)
    """

    try:
        await db.execute(
            sql,
            (
                request_id(request),
                principal.subject,
                action,
                resource,
                outcome,
                safe_details,
            ),
        )
    except HTTPException:
        logger.error(
            "Audit write failed action=%s resource=%s request_id=%s",
            action,
            resource,
            request_id(request),
        )
        if fail_closed:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audit service is unavailable; request was not processed",
            )

# ------------------------------------------------------------------------------
# OPDP / Fair Balance firewall
# ------------------------------------------------------------------------------

class ComplianceFirewall:
    """
    Conservative interception controls.

    This is not a substitute for an MLR review workflow. It prevents generation
    of promotional product claims unless controlled approved content is
    retrieved, and only releases output with mandatory indication and safety
    sections. The returned content remains subject to applicable approved-label,
    OPDP, 21 CFR 202.1, and organizational promotional-review policies.
    """

    PHI_PATTERNS = (
        re.compile(r"\b(?:ssn|social security number)\b", re.IGNORECASE),
        re.compile(r"\b(?:date of birth|dob)\b", re.IGNORECASE),
        re.compile(r"\b(?:medical record number|mrn)\b", re.IGNORECASE),
        re.compile(r"\b(?:patient name|patient address|home address)\b", re.IGNORECASE),
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN pattern
    )

    PROMOTIONAL_PATTERNS = (
        re.compile(
            r"\b(?:promote|promotional|sales aid|detail aid|marketing copy|advertisement)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:best|safest|superior|guaranteed|risk[- ]free|cure|miracle)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:efficacy|effective|indication|adverse event|side effect|contraindication|"
            r"warning|precaution|dosing|dose)\b",
            re.IGNORECASE,
        ),
    )

    @classmethod
    def contains_possible_phi(cls, text: str) -> bool:
        return any(pattern.search(text) for pattern in cls.PHI_PATTERNS)

    @classmethod
    def requires_fair_balance(cls, text: str, product_name: str | None) -> bool:
        if product_name:
            return True
        return any(pattern.search(text) for pattern in cls.PROMOTIONAL_PATTERNS)

    @classmethod
    def validate_generated_response(cls, response: str, fair_balance_required: bool) -> bool:
        if cls.contains_possible_phi(response):
            return False

        if not fair_balance_required:
            return True

        normalized = response.casefold()
        return (
            "approved indication" in normalized
            and "important safety information" in normalized
            and "not a substitute for the full prescribing information" in normalized
        )

    @staticmethod
    def phi_interception_message() -> str:
        return (
            "This request was intercepted because it may contain protected health "
            "information or direct patient identifiers. Do not submit PHI to the "
            "Copilot. Use de-identified, aggregate, and minimum-necessary data only."
        )

    @staticmethod
    def fair_balance_interception_message() -> str:
        return (
            "This request requires approved product content and Fair Balance review. "
            "No generated promotional or clinical product claim was released because "
            "the response could not be grounded in approved indication and important "
            "safety information. Consult the approved prescribing information and "
            "your Medical, Legal, and Regulatory review process."
        )

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------

def as_int(value: Any, default: int = 0) -> int:
    return default if value is None else int(value)

def as_float(value: Any, default: float = 0.0) -> float:
    return default if value is None else float(value)

def safe_search_terms(prompt: str) -> str:
    """
    Produces a bounded, non-sensitive retrieval term for an approved-content
    secure view. The original prompt is never inserted into SQL text.
    """
    terms = re.findall(r"[A-Za-z0-9]{3,}", prompt.lower())
    return " ".join(terms[:12])[:250]

# ------------------------------------------------------------------------------
# Application lifecycle and middleware
# ------------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.state.settings = settings
    app.state.snowflake = SnowflakeGateway(settings)
    app.state.authenticator = JWTAuthenticator(settings)

    logger.info("FastAPI application initialized for environment=%s", settings.app_env)
    yield
    logger.info("FastAPI application stopped")

app = FastAPI(
    title="Enterprise Pharma Copilot Gateway",
    version="1.0.0",
    docs_url="/docs" if os.getenv("APP_ENV", "production") == "development" else None,
    redoc_url=None,
    openapi_url="/openapi.json" if os.getenv("APP_ENV", "production") == "development" else None,
    lifespan=lifespan,
)

# The browser normally communicates with the same NGINX origin. CORS is opt-in.
_initial_settings = get_settings()
if _initial_settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_initial_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
        max_age=600,
    )

@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    inbound_request_id = request.headers.get("X-Request-ID", "")
    assigned_request_id = (
        inbound_request_id
        if re.fullmatch(r"[A-Za-z0-9_-]{8,128}", inbound_request_id)
        else str(uuid.uuid4())
    )

    request.state.request_id = assigned_request_id
    start = time.monotonic()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled request failure",
            extra={"request_id": assigned_request_id},
        )
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "request_id": assigned_request_id,
            },
        )

    response.headers["X-Request-ID"] = assigned_request_id
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"

    logger.info(
        "%s %s status=%s duration_ms=%d",
        request.method,
        request.url.path,
        response.status_code,
        int((time.monotonic() - start) * 1000),
        extra={"request_id": assigned_request_id},
    )
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    _: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Request validation failed",
            "request_id": request_id(request),
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    headers = dict(exc.headers or {})
    headers["X-Request-ID"] = request_id(request)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": request_id(request),
        },
        headers=headers,
    )

# ------------------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------------------

@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["Operations"],
)
async def health(request: Request, response: Response) -> HealthResponse:
    """
    SPCS container readiness and Snowflake reachability check.

    This endpoint deliberately returns no account, role, warehouse, or database
    metadata. NGINX/SPCS network policy should limit access to health endpoints.
    """
    db: SnowflakeGateway = request.app.state.snowflake
    snowflake_ready = await db.ping()

    if not snowflake_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        status="ok" if snowflake_ready else "degraded",
        spcs_ready=True,
        snowflake_ready=snowflake_ready,
        timestamp=datetime.utcnow(),
    )

@app.get(
    "/api/kpis",
    response_model=CommercialKPIs,
    tags=["Commercial"],
)
async def get_kpis(
    request: Request,
    principal: Principal = Depends(require_scope("commercial.read")),
) -> CommercialKPIs:
    settings: Settings = request.app.state.settings
    db: SnowflakeGateway = request.app.state.snowflake

    await write_audit_event(
        request,
        principal,
        action="READ",
        resource="commercial_kpis",
        outcome="ATTEMPT",
    )

    rows = await db.execute(
        f"""
        SELECT
            AS_OF_DATE,
            TRX,
            NRX,
            TARGET_HCPS,
            PA_DENIAL_RATE,
            NET_REVENUE
        FROM {settings.kpi_view}
        QUALIFY ROW_NUMBER() OVER (ORDER BY AS_OF_DATE DESC) = 1
        """
    )

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No KPI data is available",
        )

    row = rows[0]
    return CommercialKPIs(
        as_of_date=row.get("AS_OF_DATE"),
        trx=as_int(row.get("TRX")),
        nrx=as_int(row.get("NRX")),
        target_hcps=as_int(row.get("TARGET_HCPS")),
        pa_denial_rate=as_float(row.get("PA_DENIAL_RATE")),
        net_revenue=as_float(row.get("NET_REVENUE")),
    )

@app.get(
    "/api/territories",
    response_model=TerritoryListResponse,
    tags=["Commercial"],
)
async def get_territories(
    request: Request,
    principal: Principal = Depends(require_scope("commercial.read")),
) -> TerritoryListResponse:
    settings: Settings = request.app.state.settings
    db: SnowflakeGateway = request.app.state.snowflake

    await write_audit_event(
        request,
        principal,
        action="READ",
        resource="territory_alignment",
        outcome="ATTEMPT",
    )

    rows = await db.execute(
        f"""
        SELECT
            TERRITORY_ID,
            TERRITORY_NAME,
            AREA_OF_INTEREST,
            REPRESENTATIVE_NAME,
            PRESCRIBER_COUNT
        FROM {settings.territory_view}
        ORDER BY TERRITORY_NAME, TERRITORY_ID
        LIMIT ?
        """,
        (settings.max_territories,),
    )

    territories = [
        Territory(
            territory_id=str(row["TERRITORY_ID"]),
            territory_name=str(row["TERRITORY_NAME"]),
            area_of_interest=row.get("AREA_OF_INTEREST"),
            representative_name=row.get("REPRESENTATIVE_NAME"),
            prescriber_count=as_int(row.get("PRESCRIBER_COUNT")),
        )
        for row in rows
    ]

    return TerritoryListResponse(territories=territories, count=len(territories))

@app.get(
    "/api/hcp/{hcp_id}",
    response_model=HCPGoldenRecord,
    tags=["HCP"],
)
async def get_hcp(
    hcp_id: str,
    request: Request,
    principal: Principal = Depends(require_scope("hcp.read")),
) -> HCPGoldenRecord:
    """
    HCP records are accessed exclusively through a governed secure view.

    Snowflake row access and masking policies remain the source of truth for
    territory eligibility, NPI masking, and minimum-necessary field exposure.
    """
    if not _HCP_ID_RE.fullmatch(hcp_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid HCP identifier",
        )

    settings: Settings = request.app.state.settings
    db: SnowflakeGateway = request.app.state.snowflake

    await write_audit_event(
        request,
        principal,
        action="READ",
        resource="hcp_golden_record",
        outcome="ATTEMPT",
        details={"hcp_id_hash": prompt_hash(hcp_id)},
    )

    rows = await db.execute(
        f"""
        SELECT
            HCP_ID,
            NPI,
            FULL_NAME,
            SPECIALTY,
            DECILE,
            TERRITORY_ID,
            TERRITORY_NAME,
            AREA_OF_INTEREST,
            REPRESENTATIVE_NAME,
            RECENT_RX_VOLUME,
            RX_PERIOD_START,
            RX_PERIOD_END,
            RECORD_LAST_UPDATED_AT
        FROM {settings.hcp_view}
        WHERE HCP_ID = ?
        QUALIFY ROW_NUMBER() OVER (
            ORDER BY RECORD_LAST_UPDATED_AT DESC NULLS LAST
        ) = 1
        """,
        (hcp_id,),
    )

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HCP record was not found or is not authorized",
        )

    row = rows[0]
    return HCPGoldenRecord(
        hcp_id=str(row["HCP_ID"]),
        npi=str(row["NPI"]) if row.get("NPI") is not None else None,
        full_name=str(row["FULL_NAME"]),
        specialty=row.get("SPECIALTY"),
        decile=as_int(row["DECILE"]) if row.get("DECILE") is not None else None,
        territory_id=row.get("TERRITORY_ID"),
        territory_name=row.get("TERRITORY_NAME"),
        area_of_interest=row.get("AREA_OF_INTEREST"),
        representative_name=row.get("REPRESENTATIVE_NAME"),
        recent_rx_volume=as_int(row.get("RECENT_RX_VOLUME")),
        rx_period_start=row.get("RX_PERIOD_START"),
        rx_period_end=row.get("RX_PERIOD_END"),
        record_last_updated_at=row.get("RECORD_LAST_UPDATED_AT"),
    )

@app.get(
    "/api/market-access/denials",
    response_model=DenialDiagnosticsResponse,
    tags=["Market Access"],
)
async def get_denial_diagnostics(
    request: Request,
    principal: Principal = Depends(require_scope("market_access.read")),
) -> DenialDiagnosticsResponse:
    settings: Settings = request.app.state.settings
    db: SnowflakeGateway = request.app.state.snowflake

    await write_audit_event(
        request,
        principal,
        action="READ",
        resource="prior_authorization_denials",
        outcome="ATTEMPT",
    )

    rows = await db.execute(
        f"""
        SELECT
            AS_OF_DATE,
            REJECTION_CODE,
            REJECTION_DESCRIPTION,
            DENIAL_COUNT,
            DENIAL_RATE,
            RECOVERABLE_REVENUE,
            RECOMMENDED_ACTION
        FROM {settings.denial_view}
        QUALIFY AS_OF_DATE = MAX(AS_OF_DATE) OVER ()
        ORDER BY RECOVERABLE_REVENUE DESC, DENIAL_COUNT DESC
        """
    )

    diagnostics = [
        DenialDiagnostic(
            rejection_code=str(row["REJECTION_CODE"]),
            rejection_description=row.get("REJECTION_DESCRIPTION"),
            denial_count=as_int(row.get("DENIAL_COUNT")),
            denial_rate=as_float(row.get("DENIAL_RATE")),
            recoverable_revenue=as_float(row.get("RECOVERABLE_REVENUE")),
            recommended_action=row.get("RECOMMENDED_ACTION"),
        )
        for row in rows
    ]

    return DenialDiagnosticsResponse(
        as_of_date=rows[0].get("AS_OF_DATE") if rows else None,
        diagnostics=diagnostics,
        total_recoverable_revenue=sum(
            diagnostic.recoverable_revenue for diagnostic in diagnostics
        ),
    )

@app.post(
    "/api/copilot/query",
    response_model=CopilotQueryResponse,
    tags=["Copilot"],
)
async def copilot_query(
    payload: CopilotQueryRequest,
    request: Request,
    principal: Principal = Depends(require_scope("copilot.use")),
) -> CopilotQueryResponse:
    """
    Enterprise Copilot with a fail-closed OPDP/Fair Balance firewall.

    Flow:
      1. Detect likely PHI and block it before retrieval or generation.
      2. Retrieve only approved, governed content through a secure view.
      3. Generate only against retrieved approved content.
      4. Require indication, safety information, and prescribing-information
         language for product/clinical/promotional responses.
      5. Fail closed when output cannot meet Fair Balance requirements.
    """
    settings: Settings = request.app.state.settings
    db: SnowflakeGateway = request.app.state.snowflake
    firewall = ComplianceFirewall()

    if len(payload.prompt) > settings.max_copilot_prompt_chars:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Prompt exceeds the permitted length",
        )

    prompt_digest = prompt_hash(payload.prompt)
    fair_balance_required = firewall.requires_fair_balance(
        payload.prompt,
        payload.product_name,
    )

    if firewall.contains_possible_phi(payload.prompt):
        await write_audit_event(
            request,
            principal,
            action="COPILOT_QUERY",
            resource="copilot",
            outcome="INTERCEPTED_PHI",
            details={"prompt_sha256": prompt_digest},
        )
        return CopilotQueryResponse(
            request_id=request_id(request),
            status="intercepted",
            response=firewall.phi_interception_message(),
            fair_balance_required=fair_balance_required,
        )

    await write_audit_event(
        request,
        principal,
        action="COPILOT_QUERY",
        resource="copilot",
        outcome="ATTEMPT",
        details={
            "prompt_sha256": prompt_digest,
            "fair_balance_required": fair_balance_required,
            "product_supplied": bool(payload.product_name),
        },
    )

    retrieval_terms = safe_search_terms(
        f"{payload.product_name or ''} {payload.prompt}"
    )

    # The secure view must only contain MLR-approved content. Expected columns:
    # CONTENT_ID, TITLE, VERSION, EFFECTIVE_DATE, APPROVED_CONTENT, SEARCH_TEXT.
    content_rows = await db.execute(
        f"""
        SELECT
            CONTENT_ID,
            TITLE,
            VERSION,
            EFFECTIVE_DATE,
            APPROVED_CONTENT
        FROM {settings.approved_content_view}
        WHERE SEARCH_TEXT ILIKE ?
        ORDER BY EFFECTIVE_DATE DESC NULLS LAST, CONTENT_ID
        LIMIT 5
        """,
        (f"%{retrieval_terms}%",),
    )

    citations = [
        CopilotCitation(
            content_id=str(row["CONTENT_ID"]),
            title=str(row["TITLE"]),
            version=str(row["VERSION"]) if row.get("VERSION") is not None else None,
            effective_date=row.get("EFFECTIVE_DATE"),
        )
        for row in content_rows
    ]

    if not content_rows:
        await write_audit_event(
            request,
            principal,
            action="COPILOT_QUERY",
            resource="copilot",
            outcome="NO_APPROVED_CONTENT",
            details={"prompt_sha256": prompt_digest},
        )
        return CopilotQueryResponse(
            request_id=request_id(request),
            status="no_approved_content",
            response=(
                "No approved governed content was found for this request. "
                "The Copilot will not generate product, clinical, or promotional "
                "claims without approved source material. Consult Medical Affairs "
                "or the approved content repository."
            ),
            fair_balance_required=fair_balance_required,
            citations=[],
        )

    approved_context = "\n\n".join(
        (
            f"[SOURCE ID: {row['CONTENT_ID']}]\n"
            f"[TITLE: {row['TITLE']}]\n"
            f"{row['APPROVED_CONTENT']}"
        )
        for row in content_rows
    )

    system_prompt = """
You are the Enterprise Pharma Copilot. Answer only from the APPROVED CONTENT
provided below. Do not use external knowledge, infer unstated clinical claims,
compare products, claim superiority, minimize risks, or create off-label content.

If the user asks for product, clinical, efficacy, safety, dosing, indication,
or promotional content, your response MUST contain exactly these visible
headings:
1. Approved Indication
2. Response
3. Important Safety Information
4. References

The Important Safety Information section must be materially complete based on
the approved content. Include the sentence:
"This is not a substitute for the full prescribing information."

Cite source IDs in the References section. If approved content does not support
the request, state that the information is not available in the approved
content. Do not disclose patient information or personal data.
""".strip()

    composed_prompt = f"""
{system_prompt}

APPROVED CONTENT:
{approved_context}

USER REQUEST:
{payload.prompt}
""".strip()

    cortex_rows = await db.execute(
        """
        SELECT SNOWFLAKE.CORTEX.COMPLETE(?, ?) AS RESPONSE
        """,
        (settings.cortex_model, composed_prompt),
    )

    generated_response = (
        str(cortex_rows[0].get("RESPONSE", "")).strip()
        if cortex_rows
        else ""
    )

    if (
        not generated_response
        or not firewall.validate_generated_response(
            generated_response,
            fair_balance_required,
        )
    ):
        await write_audit_event(
            request,
            principal,
            action="COPILOT_QUERY",
            resource="copilot",
            outcome="INTERCEPTED_COMPLIANCE",
            details={
                "prompt_sha256": prompt_digest,
                "retrieved_content_count": len(content_rows),
            },
        )
        return CopilotQueryResponse(
            request_id=request_id(request),
            status="intercepted",
            response=firewall.fair_balance_interception_message(),
            fair_balance_required=fair_balance_required,
            citations=citations,
        )

    await write_audit_event(
        request,
        principal,
        action="COPILOT_QUERY",
        resource="copilot",
        outcome="ANSWERED",
        details={
            "prompt_sha256": prompt_digest,
            "retrieved_content_count": len(content_rows),
        },
    )

    return CopilotQueryResponse(
        request_id=request_id(request),
        status="answered",
        response=generated_response,
        fair_balance_required=fair_balance_required,
        citations=citations,
    )
```

Required Python dependencies:

```text
fastapi>=0.115,<1.0
uvicorn[standard]>=0.30,<1.0
snowflake-connector-python>=3.12,<4.0
pydantic>=2.8,<3.0
pydantic-settings>=2.4,<3.0
PyJWT[crypto]>=2.9,<3.0
anyio>=4.4,<5.0
```

The configured Snowflake secure views must expose the explicitly selected columns used by each endpoint. In particular, `COPILOT_APPROVED_CONTENT_V` must contain only approved/MLR-governed source content and must include:

```text
CONTENT_ID
TITLE
VERSION
EFFECTIVE_DATE
APPROVED_CONTENT
SEARCH_TEXT
```

The audit target must support:

```text
EVENT_TS
REQUEST_ID
SUBJECT
ACTION
RESOURCE
OUTCOME
DETAILS
```

For production SPCS deployment, configure at minimum:

```text
APP_ENV=production

JWT_JWKS_URL=https://<identity-provider>/.well-known/jwks.json
JWT_ISSUER=https://<identity-provider>/
JWT_AUDIENCE=enterprise-pharma-copilot-api

SNOWFLAKE_ACCOUNT=<organization-account>
SNOWFLAKE_USER=<service-user>
SNOWFLAKE_WAREHOUSE=<governed-warehouse>
SNOWFLAKE_DATABASE=<database>
SNOWFLAKE_SCHEMA=<schema>
SNOWFLAKE_ROLE=<least-privilege-service-role>
SNOWFLAKE_PRIVATE_KEY_FILE=/path/to/mounted/private_key.p8
SNOWFLAKE_PRIVATE_KEY_FILE_PWD=<secret-if-applicable>

CORTEX_MODEL=<organization-approved-cortex-model>
```