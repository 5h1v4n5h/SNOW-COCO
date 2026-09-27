"""
Multi-Agent SDLC Swarm for Enterprise Pharma Copilot
Borrowing the Autonomous Multi-Agent SDLC Swarm Paradigm from AI Trading,
integrated with the Leaked Claude Fable 5.1 System Prompt Engine.
Connected to Omni Route (http://localhost:20128/v1).
"""

import os
import sys
import json
from openai import OpenAI

# Ensure UTF-8 console output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

OMNI_ROUTE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:20128/v1")
OMNI_ROUTE_KEY = os.getenv("OPENAI_API_KEY", "sk-79a85f2cf92e6562-869abd-a0735450")
MODEL_NAME = os.getenv("SWARM_MODEL", "auto/coding")

client = OpenAI(
    base_url=OMNI_ROUTE_URL,
    api_key=OMNI_ROUTE_KEY
)

# Core Fable 5.1 Operating Principles extracted from claude-fable-5.1.md & Plan.md
FABLE_BASE_PROMPT = """
You are an autonomous engineering agent operating under the Claude Fable 5.1 standard.
CRITICAL OPERATING RULES:
1. REPORTING OUTCOMES: Report what actually happened, not what you intended. Never say something is done unless verified by evidence. Never quietly work around a failure.
2. DELIVERING WORK: Finish the whole task, not just easy parts. No placeholders, no stubs. Production grade only.
3. REASONING RIGOR: Think through dependencies, data flows, and edge cases before outputting code or specifications.
4. PHARMA DOMAIN COMPLIANCE: Adhere strictly to 21 CFR Part 11, HIPAA Safe Harbor, 21 CFR § 202.1 Fair Balance, and OPDP advertising guidelines.
"""

def call_agent(role_name: str, agent_instructions: str, user_prompt: str, max_tokens: int = 4096) -> str:
    print(f"\n=======================================================")
    print(f"🤖 AGENT ENGAGED: [{role_name}]")
    print(f"=======================================================")
    
    system_content = f"{FABLE_BASE_PROMPT}\n\nROLE: {role_name}\n\nSPECIALIZED INSTRUCTIONS:\n{agent_instructions}"
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=max_tokens
    )
    
    output = response.choices[0].message.content
    print(output)
    return output

def run_sdlc_pipeline():
    print(f"🚀 Initializing Enterprise Pharma Copilot SDLC Swarm...")
    print(f"📡 Routing via Omni Route endpoint: {OMNI_ROUTE_URL}")
    print(f"🧠 Swarm Model: {MODEL_NAME}")
    
    # ----------------------------------------------------
    # STAGE 1: SYSTEM ARCHITECT & PLANNER (Fable Plan Agent)
    # ----------------------------------------------------
    architect_instructions = """
    You are the Lead Solutions Architect.
    Design the complete technical architecture for the Enterprise Pharma Copilot to be hosted on Snowpark Container Services (SPCS).
    The solution must replace Streamlit with:
    1. Modern Containerized React (Vite + Vanilla CSS / Tailwind + Rich Aesthetic) Frontend.
    2. FastAPI Backend acting as an Enterprise Copilot Gateway.
    3. Integration with Snowflake 4-Layer Pharma Lakehouse:
       - MDM (MDM_HCP_MASTER, MDM_HCO_MASTER)
       - Commercial Alignment (DIM_TERRITORY, MAP_HCP_TERRITORY_ALIGNMENT)
       - Market Access (FACT_FORMULARY_TIER_COVERAGE, FACT_PA_DENIALS)
       - Longitudinal Prescriptions (FACT_PRESCRIPTION_EVENTS)
    4. Snowpark Container Services Multi-Container Specification (spcs_service_spec.yaml).
    Provide a detailed, step-by-step implementation plan with critical files and container specs.
    """
    
    architect_task = """
    Create the technical architecture specification and SPCS multi-container service specification for the Enterprise Pharma Copilot.
    Include container definitions, port mappings, environment variables, Snowflake endpoints, and the API contract between React and FastAPI.
    """
    
    arch_output = call_agent("Lead Architect & Planner (Fable)", architect_instructions, architect_task)
    
    # Save Architecture Spec
    os.makedirs("docs", exist_ok=True)
    with open("docs/spcs_architecture_spec.md", "w", encoding="utf-8") as f:
        f.write(arch_output)
    print("\n✅ Saved: docs/spcs_architecture_spec.md")
    
    # ----------------------------------------------------
    # STAGE 2: BACKEND FASTAPI ENGINEER
    # ----------------------------------------------------
    backend_instructions = """
    You are the Senior Backend Engineer.
    Design the production-grade FastAPI service (`api/main.py`) that serves the React frontend and connects to Snowflake.
    Endpoints required:
    - GET /api/health: Health check and SPCS readiness.
    - GET /api/kpis: Macro commercial KPIs (TRx, NRx, Target HCPs, PA Denial Rate, Net Revenue).
    - GET /api/territories: Territory alignment list with AOI, Rep, and Prescriber counts.
    - GET /api/hcp/{hcp_id}: Golden record details for an HCP including alignment, specialty, decile, and recent Rx volume.
    - GET /api/market-access/denials: Prior Authorization rejection diagnostics (rejection codes, recoverable revenue).
    - POST /api/copilot/query: Enterprise Copilot prompt processing with OPDP Compliance & Fair Balance firewall interception.
    Write clean, robust, asynchronous FastAPI code with Pydantic models.
    """
    
    backend_task = f"""
    Based on the architecture defined by the Architect:
    {arch_output[:1000]}...
    
    Implement the complete FastAPI application in python.
    """
    
    backend_output = call_agent("Senior Backend Engineer (FastAPI/SPCS)", backend_instructions, backend_task)
    
    # Save Backend Implementation
    os.makedirs("api", exist_ok=True)
    with open("api/main_spcs.py", "w", encoding="utf-8") as f:
        f.write(backend_output)
    print("\n✅ Saved: api/main_spcs.py")
    
    # ----------------------------------------------------
    # STAGE 3: REGULATORY & OPDP COMPLIANCE OFFICER
    # ----------------------------------------------------
    compliance_instructions = """
    You are the Regulatory Compliance & OPDP Reviewer.
    Review the Copilot architecture and backend endpoints for:
    1. 21 CFR § 202.1 Fair Balance adherence (equal prominence of risks and benefits).
    2. Medical Affairs / MSL Firewall (Strict interception of off-label queries with routing to Unsolicited Medical Information Requests - MIR).
    3. Patient Privacy & HIPAA Safe Harbor ($N >= 11$ cell suppression on query outputs).
    Produce the formal Regulatory Compliance Report and security validation checklist.
    """
    
    compliance_task = "Audit the Enterprise Pharma Copilot design and specify the exact regex and logic rules for the OPDP Compliance Guardrail."
    
    compliance_output = call_agent("Regulatory & OPDP Compliance Reviewer", compliance_instructions, compliance_task)
    
    with open("docs/regulatory_compliance_audit.md", "w", encoding="utf-8") as f:
        f.write(compliance_output)
    print("\n✅ Saved: docs/regulatory_compliance_audit.md")
    
    print("\n🎉 SDLC Multi-Agent Swarm execution complete!")

if __name__ == "__main__":
    run_sdlc_pipeline()
