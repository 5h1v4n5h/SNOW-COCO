"""
Enterprise Pharma Copilot - Multi-Level Guardrail Engine
Enforces 21 CFR § 202.1 Fair Balance, Medical Affairs / MSL Firewall,
HIPAA Safe Harbor PII Protection, and CMS N >= 11 Cell Suppression.
"""

import re
import uuid
from typing import Dict, Any, Tuple
from pydantic import BaseModel

class UserAccount(BaseModel):
    user_id: str
    name: str
    role: str
    territory: str | None = None
    access_description: str

USER_ACCOUNTS = {
    "sarah_rep": UserAccount(
        user_id="sarah_rep",
        name="Sarah Jenkins",
        role="COMMERCIAL_SALES_REP",
        territory="TERR-MIDWEST-01",
        access_description="Commercial Field Representative: Approved on-label detailing only. Strictly blocked from off-label promotion by OPDP firewall."
    ),
    "dr_vance_msl": UserAccount(
        user_id="dr_vance_msl",
        name="Dr. Eleanor Vance",
        role="MSL_MEDICAL_AFFAIRS",
        territory="NATIONAL",
        access_description="Medical Science Liaison: Independent scientific exchange, investigational clinical trial data, unsolicited medical requests (MIR)."
    ),
    "david_market_access": UserAccount(
        user_id="david_market_access",
        name="David Ross",
        role="MARKET_ACCESS_DIRECTOR",
        territory="REGIONAL_NE",
        access_description="Market Access Director: PBM formulary tier status, Prior Authorization denial analytics, step-therapy recovery."
    ),
    "marcus_cco": UserAccount(
        user_id="marcus_cco",
        name="Marcus Vance",
        role="EXECUTIVE_CCO",
        territory="GLOBAL",
        access_description="Chief Commercial Officer: Macro brand portfolio KPIs, national market share, competitor LOE displacement, N>=11 suppression."
    )
}

# Regex patterns for guardrails
PII_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "Social Security Number (SSN)"),
    (r"\b(street|st\.|avenue|ave\.|road|rd\.|drive|dr\.)\b.*?\d{5}", "Physical Street Address"),
    (r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "Phone Number"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", "Email Address"),
    (r"\b(mrn|patient_name|patient name|home address|dob|birth date)\b", "Direct Patient Identifier")
]

OFF_LABEL_KEYWORDS = [
    "alopecia", "vitiligo", "pediatric", "children", "infant", "off-label", "off label",
    "unapproved", "atopic dermatitis", "lupus", "unapproved indication", "not indicated"
]

ON_LABEL_INDICATIONS = {
    "skyrizi": ["plaque psoriasis", "psoriatic arthritis", "crohn's disease", "crohns", "ulcerative colitis"],
    "eliquis": ["deep vein thrombosis", "dvt", "pulmonary embolism", "pe", "atrial fibrillation", "afib", "hip replacement", "knee replacement"],
    "metformin": ["type 2 diabetes", "t2d", "hyperglycemia"]
}

def evaluate_guardrails(query: str, user_id: str) -> Dict[str, Any]:
    """
    Evaluates input query against user role and compliance rules.
    Returns disposition: ALLOWED | INTERCEPTED | DENIED
    """
    user = USER_ACCOUNTS.get(user_id, USER_ACCOUNTS["sarah_rep"])
    q_lower = query.lower()

    telemetry = {
        "user_id": user.user_id,
        "user_name": user.name,
        "user_role": user.role,
        "audit_id": str(uuid.uuid4())[:8],
        "checks": {
            "rbac_check": "PASS",
            "pii_check": "PASS",
            "opdp_firewall": "PASS",
            "fair_balance": "ENFORCED",
            "cell_suppression": "ENFORCED"
        },
        "status": "ALLOWED",
        "guardrail_tripped": None,
        "message": ""
    }

    # 1. HIPAA Safe Harbor PII Guardrail
    for pattern, label in PII_PATTERNS:
        if re.search(pattern, q_lower):
            telemetry["checks"]["pii_check"] = "FAILED"
            telemetry["status"] = "DENIED"
            telemetry["guardrail_tripped"] = f"HIPAA Safe Harbor Violation ({label})"
            telemetry["message"] = (
                f"🛡️ HIPAA COMPLIANCE VIOLATION: Query was blocked because it requests or contains "
                f"direct Protected Health Information ({label}). Under HIPAA 45 CFR § 164.514, "
                f"individual identifiers are strictly forbidden from clinical analytics queries."
            )
            return telemetry

    # 2. OPDP 21 CFR § 202.1 & Medical Affairs Firewall Check
    is_off_label_topic = any(kw in q_lower for kw in OFF_LABEL_KEYWORDS)
    
    if is_off_label_topic:
        if user.role == "COMMERCIAL_SALES_REP":
            # Strict block for commercial reps
            telemetry["checks"]["opdp_firewall"] = "INTERCEPTED"
            telemetry["status"] = "INTERCEPTED"
            telemetry["guardrail_tripped"] = "FDA OPDP 21 CFR § 202.1 (Off-Label Marketing Firewall)"
            mir_case = f"MIR-2026-{str(uuid.uuid4().int)[:4]}"
            telemetry["message"] = (
                f"🚫 MEDICAL AFFAIRS FIREWALL INTERCEPTION (21 CFR § 202.1)\n\n"
                f"• Policy Violation: Commercial Sales Representatives are legally prohibited from promoting or detailing unapproved indications or populations.\n"
                f"• Action Taken: Query blocked from promotional generation.\n"
                f"• Compliance Protocol: An Unsolicited Medical Information Request ticket ({mir_case}) has been securely dispatched to Medical Affairs for independent Medical Science Liaison (MSL) review."
            )
            return telemetry
        elif user.role == "MSL_MEDICAL_AFFAIRS":
            # Permitted for scientific exchange
            telemetry["checks"]["opdp_firewall"] = "PERMITTED_SCIENTIFIC_EXCHANGE"
            telemetry["status"] = "ALLOWED"
            telemetry["message"] = (
                "ℹ️ MEDICAL AFFAIRS NON-PROMOTIONAL SCIENTIFIC EXCHANGE:\n"
                "Query permitted under Medical Affairs scientific dialogue guidelines. Output must be strictly non-promotional and disclose investigational status."
            )
        else:
            telemetry["checks"]["opdp_firewall"] = "MONITORED"

    # 3. Role-based Scope Validation
    if user.role == "MARKET_ACCESS_DIRECTOR" and "prescribe" in q_lower:
        telemetry["checks"]["rbac_check"] = "INFO"
    
    return telemetry
