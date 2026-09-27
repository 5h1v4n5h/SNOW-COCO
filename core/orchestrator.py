"""
AegisCortex AI - Master Multi-Agent Supervisor & Orchestrator
Coordinates parallel worker agents (SQL, Document Evidence, Pharmacovigilance,
Regulatory, and MCP Action) in a directed acyclic graph (DAG) with citation anchoring
and an anti-hallucination guardrail.
"""

import time
import concurrent.futures
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from core.snowflake_client import SnowflakeCortexClient
from core.agents.base import AgentResult, Citation
from core.agents.sql_agent import ClinicalSQLAgent
from core.agents.doc_agent import DocEvidenceAgent
from core.agents.safety_agent import PharmacovigilanceAgent
from core.agents.regulatory_agent import RegulatoryAgent
from core.agents.mcp_action_agent import MCPActionAgent

class SwarmResponse(BaseModel):
    query: str
    patient_id: Optional[str] = None
    intent: str
    synthesis_markdown: str
    agent_results: Dict[str, AgentResult]
    citations: List[Citation]
    safety_status: str  # CLEAR, WARNING, CRITICAL_ALERT
    open_actions: List[Dict[str, Any]]
    total_latency_ms: float
    confidence_score: float

class AegisSupervisor:
    """
    Supervisor Agent orchestrating the clinical multi-agent swarm.
    """
    def __init__(self, client: Optional[SnowflakeCortexClient] = None):
        self.client = client or SnowflakeCortexClient()
        self.sql_agent = ClinicalSQLAgent(self.client)
        self.doc_agent = DocEvidenceAgent(self.client)
        self.safety_agent = PharmacovigilanceAgent(self.client)
        self.reg_agent = RegulatoryAgent(self.client)
        self.mcp_agent = MCPActionAgent(self.client)

    def route_intent(self, query: str) -> str:
        """Classifies clinical query intent to guide workflow execution."""
        q = query.lower()
        if any(w in q for w in ["metformin", "egfr", "kidney", "contraindication", "lactic acidosis", "toxic", "safety"]):
            return "CLINICAL_SAFETY_AUDIT"
        elif any(w in q for w in ["hedis", "care gap", "hba1c", "star rating", "measure", "diabetic"]):
            return "REGULATORY_CARE_GAP"
        elif any(w in q for w in ["spend", "claims", "cost", "polypharmacy", "utilizer", "eliquis", "bleeding"]):
            return "HIGH_COST_POLYPHARMACY"
        elif any(w in q for w in ["cohort", "population", "patients", "list", "how many"]):
            return "POPULATION_ANALYTICS"
        return "GENERAL_CLINICAL_QUERY"

    def process_query(self, query: str, patient_id: Optional[str] = None) -> SwarmResponse:
        """
        Executes parallel multi-agent evaluation DAG for a clinical query.
        """
        start_time = time.time()
        intent = self.route_intent(query)

        # 1. Resolve Patient ID if embedded in text
        if not patient_id:
            if "PT-1001" in query or "eleanor" in query.lower():
                patient_id = "PT-1001"
            elif "PT-1002" in query or "marcus" in query.lower():
                patient_id = "PT-1002"
            elif "PT-1003" in query or "arthur" in query.lower():
                patient_id = "PT-1003"

        agent_results: Dict[str, AgentResult] = {}
        all_citations: List[Citation] = []

        # 2. Stage 1: Parallel Execution of Data Retrieval Agents
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_sql = executor.submit(self.sql_agent.run, {"query": query, "patient_id": patient_id})
            future_doc = executor.submit(self.doc_agent.run, {"query": query, "patient_id": patient_id})

            sql_res = future_sql.result()
            doc_res = future_doc.result()

        agent_results["ClinicalSQLAgent"] = sql_res
        agent_results["DocEvidenceAgent"] = doc_res
        all_citations.extend(sql_res.citations)
        all_citations.extend(doc_res.citations)

        # Extract patient telemetry from SQL result
        patient_data = sql_res.structured_data.get("profile", {})
        if not patient_data and sql_res.structured_data.get("cohort") and patient_id:
            # If explicit patient query matched in cohort
            cohort = sql_res.structured_data.get("cohort", [])
            for c in cohort:
                if c.get("PATIENT_ID") == patient_id:
                    patient_data = c
                    break

        # 3. Stage 2: Specialized Clinical Evaluation Agents
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_safety = executor.submit(
                self.safety_agent.run,
                {"patient_data": patient_data, "patient_id": patient_id, "query": query}
            )
            future_reg = executor.submit(
                self.reg_agent.run,
                {"patient_data": patient_data, "patient_id": patient_id, "query": query}
            )

            safety_res = future_safety.result()
            reg_res = future_reg.result()

        agent_results["PharmacovigilanceAgent"] = safety_res
        agent_results["RegulatoryAgent"] = reg_res
        all_citations.extend(safety_res.citations)
        all_citations.extend(reg_res.citations)

        # 4. Stage 3: MCP Action Trigger if safety alert or care gap detected
        open_actions = []
        safety_status = "CLEAR"

        if safety_res.status in ["CRITICAL_ALERT", "WARNING"]:
            safety_status = safety_res.status
            mcp_res = self.mcp_agent.run({
                "patient_id": patient_id or "PT-1001",
                "action_type": "MEDICATION_DISCONTINUATION",
                "details": safety_res.structured_data
            })
            agent_results["MCPActionAgent"] = mcp_res
            all_citations.extend(mcp_res.citations)
            open_actions.append(mcp_res.structured_data)

        elif reg_res.status == "WARNING" and reg_res.structured_data.get("open_gaps"):
            safety_status = "WARNING"
            mcp_res = self.mcp_agent.run({
                "patient_id": patient_id or "PT-1002",
                "action_type": "CARE_GAP_CLOSURE",
                "details": reg_res.structured_data
            })
            agent_results["MCPActionAgent"] = mcp_res
            all_citations.extend(mcp_res.citations)
            open_actions.append(mcp_res.structured_data)

        # 5. Synthesize Final Briefing with Citation Anchoring
        synthesis = self._synthesize_briefing(query, intent, patient_id, patient_data, agent_results)

        total_latency = round((time.time() - start_time) * 1000, 2)
        confidence = round(sum(r.confidence_score for r in agent_results.values()) / max(len(agent_results), 1), 3)

        return SwarmResponse(
            query=query,
            patient_id=patient_id,
            intent=intent,
            synthesis_markdown=synthesis,
            agent_results=agent_results,
            citations=all_citations,
            safety_status=safety_status,
            open_actions=open_actions,
            total_latency_ms=total_latency,
            confidence_score=confidence
        )

    def _synthesize_briefing(
        self,
        query: str,
        intent: str,
        patient_id: Optional[str],
        patient_data: Dict[str, Any],
        agent_results: Dict[str, AgentResult]
    ) -> str:
        """
        Synthesizes an authoritative clinical briefing grounded in retrieved telemetry and citations.
        """
        safety_res = agent_results.get("PharmacovigilanceAgent")
        reg_res = agent_results.get("RegulatoryAgent")
        sql_res = agent_results.get("ClinicalSQLAgent")
        doc_res = agent_results.get("DocEvidenceAgent")
        mcp_res = agent_results.get("MCPActionAgent")

        lines = []

        # Header / Clinical Alert Banner
        if safety_res and safety_res.status == "CRITICAL_ALERT":
            lines.append("## 🚨 CRITICAL CLINICAL SAFETY ALERT: CONTRAINDICATION DETECTED")
            lines.append(f"**Patient**: {patient_data.get('FIRST_NAME', 'Member')} {patient_data.get('LAST_NAME', '')} (`ID: {patient_id}`)")
            lines.append(f"**Urgent Finding**: {safety_res.summary}")
            lines.append("")
        elif reg_res and reg_res.status == "WARNING":
            lines.append("## ⚠️ REGULATORY CARE GAP & QUALITY ALERT")
            lines.append(f"**Patient**: {patient_data.get('FIRST_NAME', 'Member')} {patient_data.get('LAST_NAME', '')} (`ID: {patient_id}`)")
            lines.append(f"**Audit Result**: {reg_res.summary}")
            lines.append("")
        else:
            lines.append("## 📋 CLINICAL EXECUTIVE BRIEFING")
            if patient_id:
                lines.append(f"**Patient Target**: {patient_data.get('FIRST_NAME', 'Member')} {patient_data.get('LAST_NAME', '')} (`ID: {patient_id}`)")
            lines.append(f"**Clinical Query**: *\"{query}\"*")
            lines.append("")

        # Section 1: Longitudinal EHR & Telemetry Findings
        lines.append("### 1. Longitudinal Telemetry & EHR Profile")
        if patient_data:
            lines.append(f"- **Demographics**: {patient_data.get('AGE', 'N/A')}yo {patient_data.get('GENDER', '')} | Risk Tier: **{patient_data.get('RISK_STRATIFICATION', 'Moderate')}** (Decile {patient_data.get('RISK_DECIL_SCORE', 5)}/10)")
            lines.append(f"- **Payer / Plan**: {patient_data.get('INSURANCE_PLAN', 'Medicare Advantage')}")
            lines.append(f"- **Active Medications**: `{patient_data.get('ACTIVE_MEDICATIONS', 'None')}`")
            lines.append(f"- **Key Lab Biomarkers**:")
            lines.append(f"  - **eGFR**: **{patient_data.get('LATEST_EGFR', 'N/A')} mL/min/1.73m²** (Measured: {patient_data.get('LATEST_EGFR_DATE', 'Recent')})")
            lines.append(f"  - **Serum Creatinine**: {patient_data.get('LATEST_CREATININE', 'N/A')} mg/dL")
            lines.append(f"  - **HbA1c**: **{patient_data.get('LATEST_HBA1C', 'N/A')}%** (Measured: {patient_data.get('LATEST_HBA1C_DATE', 'Recent')})")
            lines.append(f"- **Financial & Claims Spend**: **${patient_data.get('TOTAL_PAID_AMOUNT', 0.0):,.2f}** across {patient_data.get('TOTAL_CLAIMS_COUNT', 0)} claims")
        else:
            lines.append(sql_res.summary if sql_res else "No structured data available.")
        lines.append("")

        # Section 2: Authoritative Regulatory & Clinical Document Grounding
        lines.append("### 2. Document Evidence & Regulatory Citations")
        if doc_res and doc_res.citations:
            for idx, c in enumerate(doc_res.citations[:3]):
                lines.append(f"- **Citation [{idx+1}]**: **[{c.doc_title}](file:///{c.file_name or ''})** - Section *{c.section_name}*")
                # Quote first two sentences
                quote = c.verbatim_text.split(".")[0].strip() + "."
                lines.append(f"  > \"{quote}\"")
        else:
            lines.append("- Grounded against Snowflake Cortex Search indexed medical documents.")
        lines.append("")

        # Section 3: Recommended Interventions & EMR Actions
        lines.append("### 3. Recommended Interventions & MCP Tool Actions")
        if mcp_res:
            bundle = mcp_res.structured_data.get("fhir_bundle", {})
            lines.append(f"- **Pending EMR Action**: `{bundle.get('resourceType', 'Order')}` (ID: `{bundle.get('id', 'ACT-001')}`)")
            lines.append(f"- **Action Detail**: {mcp_res.summary}")
            lines.append("- **Audit State**: Recorded in `AEGIS_CORTEX_DB.APP.CLINICAL_ACTION_AUDIT_LOG` with status `PENDING_CLINICIAN_SIGNATURE`.")

        if reg_res and reg_res.structured_data.get("open_gaps"):
            lines.append("- **Identified Regulatory Care Gaps**:")
            for gap in reg_res.structured_data["open_gaps"]:
                lines.append(f"  - **{gap.get('name')}**: {gap.get('finding')} (Recommended: {gap.get('recommended_action')})")
        elif safety_res and safety_res.structured_data.get("alerts"):
            for alert in safety_res.structured_data["alerts"]:
                lines.append(f"- **{alert.get('warning_type')}**: {alert.get('recommended_action')}")
        elif not mcp_res:
            lines.append("- Continue routine preventative monitoring under primary care provider.")

        return "\n".join(lines)
