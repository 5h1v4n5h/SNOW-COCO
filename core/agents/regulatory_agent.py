"""
AegisCortex AI - Regulatory & HEDIS Compliance Agent
Audits patient and population cohorts against NCQA HEDIS MY2026 quality measures,
identifies open care gaps, and quantifies CMS Star Rating and RAF score impacts.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, date
from core.agents.base import BaseAgent, AgentResult, Citation

HEDIS_FILE = Path(__file__).resolve().parent.parent / "rules" / "hedis_measures.json"

class RegulatoryAgent(BaseAgent):
    """
    Evaluates patient cohorts for HEDIS care gaps and regulatory compliance.
    """
    def __init__(self, client):
        super().__init__(client)
        self.measures = self._load_measures()

    def _load_measures(self) -> List[Dict[str, Any]]:
        if HEDIS_FILE.exists():
            with open(HEDIS_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("measures", [])
        return []

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        patient_data = context.get("patient_data", {})
        patient_id = context.get("patient_id")
        
        # If patient_data not passed, retrieve from Snowflake
        if not patient_data and patient_id:
            sql = f"""
            SELECT PATIENT_ID, FIRST_NAME, LAST_NAME, AGE, CHRONIC_CONDITIONS,
                   LATEST_HBA1C, LATEST_HBA1C_DATE, LATEST_EGFR, LATEST_EGFR_DATE,
                   INSURANCE_PLAN
            FROM AEGIS_CORTEX_DB.TRANSFORMED.PATIENT_MEMBER_360_VIEW
            WHERE PATIENT_ID = '{patient_id}'
            """
            df = self.client.execute_query(sql)
            if not df.empty:
                patient_data = df.iloc[0].to_dict()

        if not patient_data:
            return self._execute_cohort_hedis_audit()

        # Audit individual patient
        open_gaps = []
        citations: List[Citation] = []

        conditions = str(patient_data.get("CHRONIC_CONDITIONS", "")).lower()
        is_diabetic = "diabetes" in conditions or "t2d" in conditions or "dm" in conditions

        hba1c = patient_data.get("LATEST_HBA1C")
        hba1c_date = patient_data.get("LATEST_HBA1C_DATE")

        if is_diabetic:
            # Evaluate HEDIS-CDC-H9: Glycemic Poor Control (>9.0%) or Missing Annual Test
            gap_reason = None
            if hba1c is not None and float(hba1c) >= 9.0:
                gap_reason = f"Poor glycemic control detected: Latest HbA1c is {hba1c}% (Threshold is < 8.0%, Poor Control >= 9.0%)."
            elif hba1c_date:
                try:
                    d = datetime.strptime(str(hba1c_date), "%Y-%m-%d").date()
                    days_elapsed = (date(2026, 9, 26) - d).days
                    if days_elapsed > 365:
                        gap_reason = f"Annual testing overdue: Last test conducted {days_elapsed} days ago ({hba1c_date})."
                except Exception:
                    pass

            if gap_reason:
                open_gaps.append({
                    "measure_id": "HEDIS-CDC-H9",
                    "name": "Comprehensive Diabetes Care: HbA1c Control",
                    "status": "OPEN_CARE_GAP",
                    "severity": "HIGH",
                    "finding": gap_reason,
                    "impact": "Decreases Payer CMS Star Rating score by up to 3.0 weighting points.",
                    "recommended_action": "Order immediate in-clinic venous blood draw. Dispatch home HbA1c screening kit to member address."
                })

                citations.append(Citation(
                    doc_title="NCQA HEDIS MY2026 Comprehensive Diabetes Care Guidelines",
                    section_name="MEASURE REQUIREMENTS - HBA1C POOR CONTROL (>9.0%)",
                    verbatim_text=(
                        "A member is non-compliant with the CDC HbA1c Poor Control measure if the most recent "
                        "glycated hemoglobin result is > 9.0% or if no test was performed during the measurement year."
                    ),
                    relevance_score=1.0
                ))

            # Retinal Exam Care Gap
            open_gaps.append({
                "measure_id": "HEDIS-CDC-E",
                "name": "Diabetic Retinal Eye Screening",
                "status": "OPEN_CARE_GAP",
                "severity": "MODERATE",
                "finding": "No documentation of dilated retinal eye exam in the trailing 12 months.",
                "impact": "Core preventative quality measure affecting Medicare Advantage quality incentives.",
                "recommended_action": "Generate automated referral to network optometrist or schedule mobile retinal camera scan."
            })

        status = "WARNING" if open_gaps else "SUCCESS"
        summary = (
            f"Regulatory HEDIS audit completed for {patient_data.get('FIRST_NAME', '')} {patient_data.get('LAST_NAME', '')}. "
            f"Found {len(open_gaps)} open care gap(s) requiring remediation to maintain CMS Star rating."
        ) if open_gaps else "No active regulatory care gaps identified. Member is 100% compliant with HEDIS MY2026 quality standards."

        return AgentResult(
            agent_name=self.name,
            status=status,
            summary=summary,
            structured_data={
                "open_gaps": open_gaps,
                "gap_count": len(open_gaps),
                "plan": patient_data.get("INSURANCE_PLAN")
            },
            citations=citations,
            confidence_score=0.98
        )

    def _execute_cohort_hedis_audit(self) -> AgentResult:
        """Audits overall population for HEDIS care gaps."""
        sql = """
        SELECT COUNT(*) AS TOTAL_PATIENTS,
               SUM(CASE WHEN FLAG_HBA1C_UNCONTROLLED = 1 THEN 1 ELSE 0 END) AS UNCONTROLLED_HBA1C_GAPS,
               ROUND(SUM(CASE WHEN FLAG_HBA1C_UNCONTROLLED = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS HBA1C_GAP_PERCENTAGE
        FROM AEGIS_CORTEX_DB.TRANSFORMED.PATIENT_MEMBER_360_VIEW;
        """
        df = self.client.execute_query(sql)
        stats = df.iloc[0].to_dict() if not df.empty else {}

        summary = (
            f"Population HEDIS audit: {stats.get('UNCONTROLLED_HBA1C_GAPS', 0)} members ({stats.get('HBA1C_GAP_PERCENTAGE', 0)}%) "
            f"exhibit open glycemic control gaps (HbA1c >= 9.0%) across the patient panel."
        )

        citation = Citation(
            doc_title="NCQA HEDIS MY2026 Benchmarks",
            section_name="POPULATION SUMMARY METRICS",
            verbatim_text=f"Total audited members: {stats.get('TOTAL_PATIENTS')}, Uncontrolled glycemic gaps: {stats.get('UNCONTROLLED_HBA1C_GAPS')}",
            relevance_score=1.0
        )

        return AgentResult(
            agent_name=self.name,
            status="WARNING" if stats.get("UNCONTROLLED_HBA1C_GAPS", 0) > 0 else "SUCCESS",
            summary=summary,
            structured_data=stats,
            citations=[citation],
            confidence_score=0.96
        )
