"""
AegisCortex AI - Graphify Knowledge Graph Generator
Builds a complete, deterministic knowledge graph of the codebase,
agents, Snowflake architecture, guardrails, and data lakehouse assets.
Writes to graphify-out/graph.json and C:/graphify-out/graph.json for MCP server access.
"""

import os
import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAPH_DIR = PROJECT_ROOT / "graphify-out"
GRAPH_FILE = GRAPH_DIR / "graph.json"
SYS_GRAPH_DIR = Path("C:/graphify-out")
SYS_GRAPH_FILE = SYS_GRAPH_DIR / "graph.json"

nodes = [
    # Core Architecture & Orchestrator
    {
        "id": "core_orchestrator_aegissupervisor",
        "label": "AegisSupervisor (Swarm Queen)",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "core" / "orchestrator.py"),
        "description": "Master multi-agent DAG orchestrator, coordinates parallel retrieval, evaluation, and synthesis."
    },
    {
        "id": "core_snowflake_client_cortexclient",
        "label": "SnowflakeCortexClient",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "core" / "snowflake_client.py"),
        "description": "Unified dual-mode Snowflake Cortex AI and local SQLite data access client."
    },
    {
        "id": "core_guardrail_engine",
        "label": "ComplianceGuardrailEngine",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "core" / "guardrail_engine.py"),
        "description": "Deterministic regulatory firewall: HIPAA PII, OPDP 21 CFR § 202.1 Fair Balance, CMS N>=11."
    },
    # Specialized Agents
    {
        "id": "core_agents_sql_agent",
        "label": "ClinicalSQLAgent",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "core" / "agents" / "sql_agent.py"),
        "description": "Queries Patient 360, longitudinal labs, and claims spend from Snowflake lakehouse."
    },
    {
        "id": "core_agents_doc_agent",
        "label": "DocEvidenceAgent",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "core" / "agents" / "doc_agent.py"),
        "description": "Performs vector RAG search over clinical trials and FDA prescribing labels with verbatim citations."
    },
    {
        "id": "core_agents_safety_agent",
        "label": "PharmacovigilanceAgent",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "core" / "agents" / "safety_agent.py"),
        "description": "Detects black box contraindications (Metformin eGFR < 30) and DDI bleeding hazards (Eliquis + NSAID)."
    },
    {
        "id": "core_agents_regulatory_agent",
        "label": "RegulatoryAgent",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "core" / "agents" / "regulatory_agent.py"),
        "description": "Audits NCQA HEDIS MY2026 care gaps, calculates CMS Star Rating impacts, and cites guidelines."
    },
    {
        "id": "core_agents_mcp_action_agent",
        "label": "MCPActionAgent",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "core" / "agents" / "mcp_action_agent.py"),
        "description": "Dispatches EHR orders, Slack alerts, Jira tickets, and writes to APP.CLINICAL_ACTION_AUDIT_LOG."
    },
    # RuFlo Swarm Harness
    {
        "id": "ruflo_config",
        "label": "RuFlo Swarm Harness Config",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "ruflo.config.json"),
        "description": "Configures 7-agent hierarchical mesh swarm with OmniRoute LLM routing and vector memory."
    },
    {
        "id": "ruflo_mission_brief",
        "label": "RuFlo Mission Brief",
        "file_type": "document",
        "source_file": str(PROJECT_ROOT / "RUFLO_MISSION_BRIEF.md"),
        "description": "Complete production engineering spec, SPCS container instructions, and regulatory guardrails."
    },
    # Snowflake Data Lakehouse Models
    {
        "id": "snowflake_03_patient_360_views",
        "label": "PATIENT_MEMBER_360_VIEW",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "snowflake" / "03_patient_360_views.sql"),
        "description": "Snowflake transformed layer view aggregating patient profile, lab trajectories, and claims spend."
    },
    {
        "id": "snowflake_05_semantic_model",
        "label": "Cortex Analyst Semantic Model",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "snowflake" / "05_semantic_model.yaml"),
        "description": "YAML semantic model defining dimensions, metrics, and relationships for Snowflake Cortex Analyst."
    },
    {
        "id": "snowflake_06_load_large_synthetic",
        "label": "Large Synthetic Lakehouse DDL",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "snowflake" / "06_load_large_synthetic_data.sql"),
        "description": "Snowflake staging and bulk-copy loader for 10,000 synthetic patients and 132k lab records."
    },
    # Synthetic Data Lakehouse
    {
        "id": "data_generator_large_lakehouse",
        "label": "Large Synthetic Lakehouse Generator",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "data_generator" / "generate_large_synthetic_lakehouse.py"),
        "description": "Simulates 10,000 patients, 132k labs, 24k Rx, 40k claims, and 827 prior authorizations."
    },
    # SPCS Container & API Gateway
    {
        "id": "spcs_service_spec",
        "label": "SPCS Service Specification",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "spcs_service_spec.yaml"),
        "description": "Multi-container specification: NGINX frontend port 8080 and FastAPI backend port 8000."
    },
    {
        "id": "api_server",
        "label": "FastAPI Gateway Server",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "api" / "server.py"),
        "description": "Production REST API server exposing /health, /api/patients, /api/copilot/chat, /api/analyze."
    },
    {
        "id": "web_command_center",
        "label": "React 18 Command Center UI",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "web" / "index.html"),
        "description": "Production single-page web app with multi-persona context selector, eGFR charts, and RAG document viewer."
    },
    {
        "id": "eval_snow_eval",
        "label": "SnowEval Benchmark Suite",
        "file_type": "code",
        "source_file": str(PROJECT_ROOT / "eval" / "snow_eval.py"),
        "description": "15-scenario automated clinical benchmark measuring faithfulness, citation precision, and safety recall."
    }
]

edges = [
    # Orchestrator connections
    {"source": "core_orchestrator_aegissupervisor", "target": "core_agents_sql_agent", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "core_orchestrator_aegissupervisor", "target": "core_agents_doc_agent", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "core_orchestrator_aegissupervisor", "target": "core_agents_safety_agent", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "core_orchestrator_aegissupervisor", "target": "core_agents_regulatory_agent", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "core_orchestrator_aegissupervisor", "target": "core_agents_mcp_action_agent", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "core_orchestrator_aegissupervisor", "target": "core_snowflake_client_cortexclient", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0},
    # Agent to Data and Client
    {"source": "core_agents_sql_agent", "target": "core_snowflake_client_cortexclient", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "core_agents_doc_agent", "target": "core_snowflake_client_cortexclient", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "core_agents_sql_agent", "target": "snowflake_03_patient_360_views", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "core_agents_regulatory_agent", "target": "snowflake_03_patient_360_views", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0},
    # Guardrails and API Gateway
    {"source": "api_server", "target": "core_guardrail_engine", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "api_server", "target": "core_orchestrator_aegissupervisor", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "api_server", "target": "core_snowflake_client_cortexclient", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0},
    # SPCS and Frontend
    {"source": "spcs_service_spec", "target": "api_server", "relation": "implements", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "spcs_service_spec", "target": "web_command_center", "relation": "implements", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "web_command_center", "target": "api_server", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0},
    # Evaluation and Lakehouse
    {"source": "eval_snow_eval", "target": "core_orchestrator_aegissupervisor", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "data_generator_large_lakehouse", "target": "snowflake_06_load_large_synthetic", "relation": "implements", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "snowflake_06_load_large_synthetic", "target": "snowflake_03_patient_360_views", "relation": "implements", "confidence": "EXTRACTED", "confidence_score": 1.0},
    # RuFlo Coordination
    {"source": "ruflo_config", "target": "core_orchestrator_aegissupervisor", "relation": "implements", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "ruflo_mission_brief", "target": "spcs_service_spec", "relation": "implements", "confidence": "EXTRACTED", "confidence_score": 1.0}
]

hyperedges = [
    {
        "id": "he_clinical_copilot_pipeline",
        "label": "Multi-Agent Clinical Evaluation Pipeline",
        "nodes": [
            "core_orchestrator_aegissupervisor",
            "core_agents_sql_agent",
            "core_agents_doc_agent",
            "core_agents_safety_agent",
            "core_agents_regulatory_agent",
            "core_agents_mcp_action_agent"
        ],
        "relation": "form",
        "confidence": "EXTRACTED",
        "confidence_score": 1.0
    },
    {
        "id": "he_spcs_deployment_stack",
        "label": "Snowpark Container Services Stack",
        "nodes": [
            "spcs_service_spec",
            "api_server",
            "web_command_center",
            "core_snowflake_client_cortexclient"
        ],
        "relation": "form",
        "confidence": "EXTRACTED",
        "confidence_score": 1.0
    }
]

graph_data = {
    "nodes": nodes,
    "edges": edges,
    "hyperedges": hyperedges,
    "metadata": {
        "repo_name": "AegisCortex AI (SNOW COCO)",
        "version": "1.0.0",
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }
}

def build_graph():
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    with open(GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2)
    print(f"[OK] Knowledge graph generated at: {GRAPH_FILE} ({len(nodes)} nodes, {len(edges)} edges)")

    try:
        SYS_GRAPH_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(GRAPH_FILE, SYS_GRAPH_FILE)
        print(f"[OK] Copied knowledge graph to system MCP path: {SYS_GRAPH_FILE}")
    except Exception as e:
        print(f"[!] Warning copying to {SYS_GRAPH_DIR}: {e}")

if __name__ == "__main__":
    build_graph()
