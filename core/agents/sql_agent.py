"""
AegisCortex AI - Clinical Structured SQL Agent
Queries longitudinal Patient 360 views, LOINC laboratory trends, and financial claims.
"""

from typing import Dict, Any, List
import pandas as pd
from core.agents.base import BaseAgent, AgentResult, Citation

class ClinicalSQLAgent(BaseAgent):
    """
    Executes structured queries against Snowflake PATIENT_MEMBER_360_VIEW,
    LAB_RESULTS, CLAIMS, and ENCOUNTERS.
    """
    def execute(self, context: Dict[str, Any]) -> AgentResult:
        patient_id = context.get("patient_id")
        query_text = context.get("query", "")
        
        # 1. Resolve Patient ID from query if not explicitly passed
        if not patient_id:
            if "PT-1001" in query_text or "eleanor" in query_text.lower():
                patient_id = "PT-1001"
            elif "PT-1002" in query_text or "marcus" in query_text.lower():
                patient_id = "PT-1002"
            elif "PT-1003" in query_text or "arthur" in query_text.lower():
                patient_id = "PT-1003"

        # 2. Population-level query execution
        if not patient_id and any(w in query_text.lower() for w in ["population", "all patients", "cohort", "contraindicated", "uncontrolled"]):
            return self._execute_cohort_query(query_text)

        # 3. Patient-specific longitudinal telemetry
        if patient_id:
            return self._execute_patient_telemetry(patient_id)

        # Fallback to general cohort snapshot
        return self._execute_cohort_query(query_text)

    def _execute_patient_telemetry(self, patient_id: str) -> AgentResult:
        """Retrieves comprehensive longitudinal profile for an individual member."""
        p360_sql = f"""
        SELECT *
        FROM AEGIS_CORTEX_DB.TRANSFORMED.PATIENT_MEMBER_360_VIEW
        WHERE PATIENT_ID = '{patient_id}'
        LIMIT 1;
        """
        df_p360 = self.client.execute_query(p360_sql)
        
        if df_p360.empty:
            return AgentResult(
                agent_name=self.name,
                status="NO_DATA",
                summary=f"No clinical records identified for Patient Identifier {patient_id}.",
                structured_data={"patient_id": patient_id},
                confidence_score=0.95
            )

        row = df_p360.iloc[0].to_dict()

        # Retrieve longitudinal lab trend for eGFR and HbA1c
        labs_sql = f"""
        SELECT COLLECTION_DATE, LOINC_CODE, TEST_NAME, NUMERIC_VALUE, UNITS, ABNORMAL_FLAG
        FROM AEGIS_CORTEX_DB.RAW.LAB_RESULTS
        WHERE PATIENT_ID = '{patient_id}'
        ORDER BY COLLECTION_DATE ASC;
        """
        df_labs = self.client.execute_query(labs_sql)
        lab_history = df_labs.to_dict(orient="records") if not df_labs.empty else []

        # Retrieve claims breakdown
        claims_sql = f"""
        SELECT SERVICE_DATE, CPT_CODE, SERVICE_DESCRIPTION, TOTAL_CHARGES, PAID_AMOUNT, CLAIM_STATUS
        FROM AEGIS_CORTEX_DB.RAW.CLAIMS
        WHERE PATIENT_ID = '{patient_id}'
        ORDER BY SERVICE_DATE DESC;
        """
        df_claims = self.client.execute_query(claims_sql)
        claims_history = df_claims.to_dict(orient="records") if not df_claims.empty else []

        # Formulate clinical summary
        egfr_val = row.get("LATEST_EGFR")
        hba1c_val = row.get("LATEST_HBA1C")
        meds = row.get("ACTIVE_MEDICATIONS", "")
        spend = row.get("TOTAL_PAID_AMOUNT", 0.0)

        summary = (
            f"Longitudinal record for {row.get('FIRST_NAME')} {row.get('LAST_NAME')} (ID: {patient_id}, Age: {row.get('AGE')}, Plan: {row.get('INSURANCE_PLAN')}). "
            f"Latest eGFR: {egfr_val} mL/min/1.73m2 ({row.get('LATEST_EGFR_DATE')}); "
            f"Latest HbA1c: {hba1c_val}% ({row.get('LATEST_HBA1C_DATE')}). "
            f"Active Meds: {meds}. Cumulative Plan Paid: ${spend:,.2f} across {row.get('TOTAL_CLAIMS_COUNT')} claims."
        )

        citation = Citation(
            doc_title="Snowflake Warehouse - PATIENT_MEMBER_360_VIEW",
            section_name=f"Record Row PATIENT_ID={patient_id}",
            verbatim_text=f"eGFR={egfr_val}, HbA1c={hba1c_val}, Meds={meds}, TotalClaimsPaid={spend}",
            relevance_score=1.0
        )

        return AgentResult(
            agent_name=self.name,
            status="SUCCESS",
            summary=summary,
            structured_data={
                "profile": row,
                "lab_history": lab_history,
                "claims_history": claims_history
            },
            citations=[citation],
            confidence_score=1.0
        )

    def _execute_cohort_query(self, query_text: str) -> AgentResult:
        """Executes aggregate or filtered cohort discovery queries."""
        sql = """
        SELECT PATIENT_ID, FIRST_NAME, LAST_NAME, AGE, RISK_STRATIFICATION,
               ACTIVE_MEDICATIONS, LATEST_EGFR, LATEST_HBA1C, TOTAL_PAID_AMOUNT,
               FLAG_METFORMIN_CONTRAINDICATED, FLAG_HBA1C_UNCONTROLLED, FLAG_HIGH_UTILIZER_RISK
        FROM AEGIS_CORTEX_DB.TRANSFORMED.PATIENT_MEMBER_360_VIEW
        ORDER BY TOTAL_PAID_AMOUNT DESC
        LIMIT 25;
        """
        df = self.client.execute_query(sql)
        records = df.to_dict(orient="records") if not df.empty else []

        contraindicated_count = sum(1 for r in records if r.get("FLAG_METFORMIN_CONTRAINDICATED") == 1)
        uncontrolled_count = sum(1 for r in records if r.get("FLAG_HBA1C_UNCONTROLLED") == 1)

        summary = (
            f"Retrieved population cohort of {len(records)} patients. "
            f"Identified {contraindicated_count} patient(s) with active Metformin contraindication (eGFR < 30) "
            f"and {uncontrolled_count} patient(s) with uncontrolled HbA1c (>= 9.0%)."
        )

        citation = Citation(
            doc_title="Snowflake Warehouse - Cohort Aggregation",
            section_name="PATIENT_MEMBER_360_VIEW Filtered Cohort",
            verbatim_text=f"Cohort count={len(records)}, Metformin contraindications={contraindicated_count}",
            relevance_score=1.0
        )

        return AgentResult(
            agent_name=self.name,
            status="SUCCESS",
            summary=summary,
            structured_data={"cohort": records, "count": len(records)},
            citations=[citation],
            confidence_score=0.98
        )
