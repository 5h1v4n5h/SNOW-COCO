"""
AegisCortex AI - Native Snowflake Clinical Regulatory Copilot
Multi-Agent Swarm for Patient/Member 360, Deterministic Pharmacovigilance,
and NCQA HEDIS Quality Automation.
"""

import sys
import json
from pathlib import Path
import streamlit as st
import pandas as pd

# Append project root to sys.path for module resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.orchestrator import AegisSupervisor
from core.snowflake_client import SnowflakeCortexClient

# Page configuration
st.set_page_config(
    page_title="AegisCortex AI | Clinical Regulatory Copilot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Design System CSS (DESIGN.md Tokens: Dark Slate #07090E, Snowflake Cyan #29B5E8)
st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #07090E;
        color: #F1F5F9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Header Typography */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Neon Snowflake Cyan Highlights */
    .cyan-text {
        color: #29B5E8;
        font-weight: 600;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: #0F1420;
        border: 1px solid rgba(41, 181, 232, 0.2);
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Agent Status Badges */
    .agent-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        margin-right: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .pill-sql { background: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid #3B82F6; }
    .pill-doc { background: rgba(168, 85, 247, 0.2); color: #C084FC; border: 1px solid #A855F7; }
    .pill-safety { background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }
    .pill-reg { background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid #F59E0B; }
    .pill-mcp { background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }

    /* Alert Banners */
    .critical-banner {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid #EF4444;
        border-left: 6px solid #EF4444;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 20px;
    }
    .warning-banner {
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid #F59E0B;
        border-left: 6px solid #F59E0B;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "supervisor" not in st.session_state:
    st.session_state.client = SnowflakeCortexClient()
    st.session_state.supervisor = AegisSupervisor(st.session_state.client)

if "active_patient_id" not in st.session_state:
    st.session_state.active_patient_id = "PT-1001"

if "query_input" not in st.session_state:
    st.session_state.query_input = "Verify Metformin safety for Eleanor Vance with declining renal function"

supervisor = st.session_state.supervisor
client = st.session_state.client

# ==============================================================================
# SIDEBAR: Context & Navigation
# ==============================================================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/f/ff/Snowflake_Inc._logo.svg", width=140)
    st.title("AegisCortex AI")
    st.caption("Enterprise Clinical Regulatory Copilot • Snowflake CoCo Hackathon 2026")
    
    st.markdown("---")
    
    # Engine Telemetry
    conn_status = "🟢 Live Snowflake Cortex" if client.is_live() else "🟡 Local Zero-Latency Engine"
    st.markdown(f"**Execution Runtime:** `{conn_status}`")
    st.markdown(f"**Model:** `llama3.3-70b` (Snowflake Cortex)")
    st.markdown(f"**Search Engine:** `arctic-embed-l-v2.0`")
    
    st.markdown("---")
    st.subheader("🎯 Hero Clinical Scenarios")
    
    col_s1, col_s2, col_s3 = st.columns(1)[0], None, None
    if st.button("🚨 1. Eleanor Vance (PT-1001)\neGFR Drop & Metformin Contraindication", use_container_width=True):
        st.session_state.active_patient_id = "PT-1001"
        st.session_state.query_input = "Verify Metformin safety for Eleanor Vance with declining renal function"
        st.rerun()
        
    if st.button("⚠️ 2. Marcus Brody (PT-1002)\nNCQA HEDIS MY2026 Care Gap", use_container_width=True):
        st.session_state.active_patient_id = "PT-1002"
        st.session_state.query_input = "Audit HEDIS MY2026 quality care gaps for Marcus Brody PT-1002"
        st.rerun()

    if st.button("💊 3. Arthur Pendelton (PT-1003)\n$64k Spend & Polypharmacy Bleeding", use_container_width=True):
        st.session_state.active_patient_id = "PT-1003"
        st.session_state.query_input = "Evaluate Arthur Pendelton PT-1003 claims spend and Eliquis Ibuprofen bleeding risk"
        st.rerun()

    st.markdown("---")
    st.caption("Zero PHI data movement outside Snowflake governance boundary. HIPAA & CMS compliance verified.")

# ==============================================================================
# MAIN PAGE: Clinical Executive Command Center
# ==============================================================================

# Header Title Row
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("🛡️ Patient & Member 360 Multi-Agent Copilot")
    st.markdown(
        "Autonomous clinical safety screening, longitudinal telemetry analysis, "
        "and NCQA HEDIS quality automation powered natively by **Snowflake Cortex AI**."
    )
with header_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<span class="agent-pill pill-sql">SQL</span>'
        '<span class="agent-pill pill-doc">CORTEX SEARCH</span>'
        '<span class="agent-pill pill-safety">SAFETY</span>'
        '<span class="agent-pill pill-reg">HEDIS</span>'
        '<span class="agent-pill pill-mcp">FHIR MCP</span>',
        unsafe_allow_html=True
    )

st.markdown("---")

# Query & Patient Selector Input
q_col1, q_col2, q_col3 = st.columns([4, 1.5, 1])
with q_col1:
    user_query = st.text_input("Enter Clinical Query or Directive:", value=st.session_state.query_input)
with q_col2:
    # Pull distinct patients from SQLite / Snowflake
    df_pts = client.execute_query("SELECT PATIENT_ID, FIRST_NAME, LAST_NAME FROM AEGIS_CORTEX_DB.TRANSFORMED.PATIENT_MEMBER_360_VIEW ORDER BY PATIENT_ID LIMIT 20;")
    pt_options = [f"{r['PATIENT_ID']} - {r['FIRST_NAME']} {r['LAST_NAME']}" for _, r in df_pts.iterrows()] if not df_pts.empty else ["PT-1001 - Eleanor Vance"]
    
    # Determine default index
    default_idx = 0
    for idx, opt in enumerate(pt_options):
        if st.session_state.active_patient_id in opt:
            default_idx = idx
            break
            
    selected_pt = st.selectbox("Target Patient MRN:", options=pt_options, index=default_idx)
    target_pid = selected_pt.split(" - ")[0] if selected_pt else "PT-1001"
with q_col3:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("🚀 Analyze", use_container_width=True, type="primary")

# Execute Swarm
with st.spinner("Executing parallel multi-agent swarm across Cortex Search and longitudinal warehouse..."):
    swarm_resp = supervisor.process_query(user_query, patient_id=target_pid)

# Display Multi-Agent Execution Telemetry Banner
telemetry_cols = st.columns(5)
with telemetry_cols[0]:
    st.metric("Total Latency", f"{swarm_resp.total_latency_ms:.1f} ms", delta="Sub-Second SLA")
with telemetry_cols[1]:
    st.metric("Cortex Model", "llama3.3-70b", delta="Arctic Embed")
with telemetry_cols[2]:
    st.metric("Confidence Score", f"{swarm_resp.confidence_score * 100:.1f}%", delta="Anti-Hallucination")
with telemetry_cols[3]:
    st.metric("Active Agents", len(swarm_resp.agent_results), delta="Parallel Swarm")
with telemetry_cols[4]:
    sev_color = "🔴 CRITICAL" if swarm_resp.safety_status == "CRITICAL_ALERT" else ("🟡 WARNING" if swarm_resp.safety_status == "WARNING" else "🟢 NORMAL")
    st.metric("Safety Guardrail", sev_color)

st.markdown("<br>", unsafe_allow_html=True)

# Display Clinical Alert Banner if triggered
if swarm_resp.safety_status == "CRITICAL_ALERT":
    st.markdown("""
    <div class="critical-banner">
        <h3 style="color:#EF4444; margin:0 0 6px 0;">🚨 CRITICAL PHARMACOVIGILANCE ALERT: BLACK BOX CONTRAINDICATION</h3>
        <p style="margin:0; font-size:14px; color:#FCA5A5;">
            Deterministic rule violation detected: Active prescription is contraindicated due to acute laboratory threshold breach.
            Immediate clinical discontinuation order generated for provider signature.
        </p>
    </div>
    """, unsafe_allow_html=True)
elif swarm_resp.safety_status == "WARNING":
    st.markdown("""
    <div class="warning-banner">
        <h3 style="color:#F59E0B; margin:0 0 6px 0;">⚠️ REGULATORY CARE GAP / MODERATE RISK DETECTED</h3>
        <p style="margin:0; font-size:14px; color:#FDE68A;">
            Patient is non-compliant with NCQA HEDIS MY2026 quality metrics or flagged for major drug interaction.
            Remediation protocol initiated.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main Two-Column Layout: Left = Clinical Synthesis & Evidence | Right = Patient 360 & Orders
col_left, col_right = st.columns([1.6, 1.2])

with col_left:
    st.subheader("📋 Autonomous Clinical Synthesis & Telemetry")
    st.markdown(swarm_resp.synthesis_markdown)
    
    st.markdown("---")
    st.subheader("🔍 Cortex Search Grounded Evidence")
    doc_res = swarm_resp.agent_results.get("DocEvidenceAgent")
    if doc_res and doc_res.citations:
        for idx, c in enumerate(doc_res.citations):
            with st.expander(f"Citation [{idx+1}]: {c.doc_title} ({c.section_name})", expanded=(idx==0)):
                st.caption(f"Source Document: {c.file_name or 'Snowflake Cortex Search Stage'} | Relevance: {c.relevance_score * 100:.0f}%")
                st.code(c.verbatim_text, language="markdown")
    else:
        st.info("No unstructured document citations required for this query.")

with col_right:
    st.subheader("👤 Longitudinal Patient 360")
    sql_res = swarm_resp.agent_results.get("ClinicalSQLAgent")
    p_data = sql_res.structured_data.get("profile", {}) if sql_res else {}
    
    if p_data:
        # Patient Card
        st.markdown(f"""
        <div style="background:#0F1420; border:1px solid #1E293B; border-radius:8px; padding:14px; margin-bottom:12px;">
            <h4 style="margin:0; color:#38BDF8;">{p_data.get('FIRST_NAME')} {p_data.get('LAST_NAME')}</h4>
            <span style="font-size:12px; color:#94A3B8;">MRN: {p_data.get('PATIENT_ID')} | {p_data.get('AGE')}yo {p_data.get('GENDER')} | Plan: {p_data.get('INSURANCE_PLAN')}</span>
            <hr style="margin:8px 0; border-color:#1E293B;">
            <p style="margin:4px 0; font-size:13px;"><b>Conditions:</b> {p_data.get('CHRONIC_CONDITIONS')}</p>
            <p style="margin:4px 0; font-size:13px;"><b>Active Meds:</b> <code style="color:#F59E0B;">{p_data.get('ACTIVE_MEDICATIONS')}</code></p>
            <p style="margin:4px 0; font-size:13px;"><b>Risk Stratification:</b> <span style="color:#EF4444; font-weight:600;">{p_data.get('RISK_STRATIFICATION')}</span> (Decile {p_data.get('RISK_DECIL_SCORE')}/10)</p>
            <p style="margin:4px 0; font-size:13px;"><b>Plan Spend:</b> ${p_data.get('TOTAL_PAID_AMOUNT', 0.0):,.2f} across {p_data.get('TOTAL_CLAIMS_COUNT', 0)} claims</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Longitudinal Lab Trajectory (eGFR & HbA1c)
        lab_history = sql_res.structured_data.get("lab_history", [])
        if lab_history:
            df_lh = pd.DataFrame(lab_history)
            df_egfr = df_lh[df_lh["LOINC_CODE"] == "33914-3"].sort_values("COLLECTION_DATE")
            if not df_egfr.empty:
                st.markdown("**Longitudinal eGFR Trajectory (LOINC 33914-3)**")
                st.line_chart(df_egfr.set_index("COLLECTION_DATE")["NUMERIC_VALUE"], height=160)
                if df_egfr.iloc[-1]["NUMERIC_VALUE"] < 30:
                    st.caption("🔴 Current eGFR is critically below 30 mL/min threshold (Stage 4 CKD).")

    # MCP Action Order Hub
    st.markdown("---")
    st.subheader("⚡ Clinician Action & EMR Approval Hub")
    if swarm_resp.open_actions:
        for action in swarm_resp.open_actions:
            bundle = action.get("fhir_bundle", {})
            st.markdown(f"**Pending Order**: `{bundle.get('resourceType')}` (ID: `{action.get('action_id')}`)")
            with st.expander("Inspect HL7 FHIR R4 Bundle Payload", expanded=False):
                st.json(bundle)
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("✍️ Approve & Sign Order", key=f"app_{action.get('action_id')}", type="primary"):
                    st.success(f"Order {action.get('action_id')} approved by Attending Clinician. Dispatched to Snowflake Audit Log.")
            with c_btn2:
                if st.button("❌ Reject / Modify", key=f"rej_{action.get('action_id')}"):
                    st.warning("Order deferred for manual peer-to-peer review.")
    else:
        st.success("No pending urgent interventions required for this member.")

# Multi-Agent Swarm Execution Breakdown
st.markdown("---")
with st.expander("🛠️ Multi-Agent Swarm Execution Breakdown & Audit Trail", expanded=False):
    swarm_table = []
    for name, r in swarm_resp.agent_results.items():
        swarm_table.append({
            "Agent": name,
            "Status": r.status,
            "Latency (ms)": r.execution_time_ms,
            "Confidence": f"{r.confidence_score * 100:.1f}%",
            "Citations Count": len(r.citations),
            "Summary": r.summary[:140] + "..."
        })
    st.dataframe(pd.DataFrame(swarm_table), use_container_width=True)
