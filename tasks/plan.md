# Implementation Plan: Hackathon Package, Submission Deck, & 3-5 Min Video

## 1. Overview
This plan implements the complete set of final deliverables for the **Snowflake CoCo CLI Hackathon 2026 – GCC Edition**:
1. **Clean Codebase & GitHub Repository**: Clean up unnecessary repositories/files (`agency-agents`, `agency-swarm`, large CSV dumps, scratch files), craft an exhaustive production `README.md` featuring live demo URL (`https://weed-paxil-bizarre-brings.trycloudflare.com`), multi-layer architecture, persona flows, and deploy instructions, and commit/push to GitHub.
2. **Submission Presentation Deck**: Transform `Prototype Submission Template _ CoCo CLI Hackathon GCC Edition.pptx` into a complete, professional hackathon deck featuring the problem statement, solution, proposed architecture, modular CoCo CLI skills, and a visual website review incorporating screenshots from `COCO Hackathon/`.
3. **3–5 Minute Video Demonstration & Script**: Provide a runnable end-to-end CLI demonstration script showing Input → Processing → Output across 2-3 modular CoCo skills, alongside a scene-by-scene word-for-word voiceover narration and recording guide.

---

## 2. Deliverable Architecture & Design Decisions

### Deliverable #1: Clean Package & GitHub Repository
- **Git Filter & Hygiene**:
  - Update `.gitignore` to cleanly exclude copied third-party repos (`agency-agents/`, `agency-swarm/`), `.claude-flow/`, `.claude/`, `.swarm/`, `system_prompts_leaks/`, bulky raw data (`data/synthetic_large/*.csv`), and non-project downloads.
  - Keep active source code: `core/`, `api/`, `web/`, `snowflake/`, `data_generator/`, `eval/`, `cortex_cli.py`, `snowflake.yml`, `requirements.txt`.
- **README Structure**:
  - High-impact header with live demo badge (`https://weed-paxil-bizarre-brings.trycloudflare.com`).
  - Executive summary and problem statement.
  - End-to-end Mermaid architecture diagram (Snowflake Lakehouse, Cortex LLM, Cortex Search, Multi-Agent Swarm, Role-Based API, Web UI).
  - 4 Persona User Flows (Field Sales Rep, Market Access Director, Medical Science Liaison, Chief Commercial Officer).
  - Step-by-step Quickstart & Deployment Guide (Local FastAPI, CoCo CLI, Snowflake Native App).

### Deliverable #2: Hackathon Submission Deck (`.pptx`)
- Retain the official hackathon template backgrounds and dimensions (`9144000` x `5143500` EMU, 16:9 widescreen).
- **Slide 1**: Title, Team Name, Problem Statement, Team Leader Name, Team Size.
- **Slide 2**: Problem Brief & Real-World Domain Context ($1.2T waste, compliance risk, fragmented data).
- **Slide 3**: Proposed Architecture & Modular CoCo CLI Skills (Snowflake Cortex AI, Lakehouse, Multi-Agent Swarm).
- **Slide 4**: The Solution & Persona Matrix (4 role-tailored operational workflows).
- **Slide 5**: Website Review – Commercial & Field Operations (Screenshots: Landing Page Auth, Field Intelligence Copilot, Detailing Targets, Market Access PBM Triage).
- **Slide 6**: Website Review – Clinical & Executive Governance (Screenshots: Pharmacovigilance Safety Radar, Scientific Exchange, Portfolio Velocity, Compliance Safe Harbor Ledger).
- **Slide 7**: Impact Statement & GCC Scalability (82% overturn rate, 100% compliance recall, 5.4ms SLA, native deployability).

### Deliverable #3: Video Demonstration & CoCo CLI Workflow
- **CoCo CLI Showcase**:
  - Build `scripts/coco_cli_demo.py` to run a polished, colored terminal workflow displaying:
    - Skill 1: Ingestion & Lakehouse Metric Verification.
    - Skill 2: Deterministic Regulatory Guardrail Firewall (Input -> 21 CFR § 202.1 check -> Interception/Denial -> Output).
    - Skill 3: Contextual Snowflake Cortex AI Strategic Synthesis (Input -> Role Context -> Cortex `llama3.3-70b` -> Structured Action Items).
- **Script & Visual Cue Sheet**:
  - 3.5-minute structured timing table.
  - Precise instructions on what to record on screen (CLI terminal vs. live Web UI).
  - Word-for-word voiceover text ready for recording or text-to-speech.

---

## 3. Work Breakdown Structure

### Phase 1: Repository Cleanup & README Production
- Audit git staged files and `.gitignore`.
- Write exhaustive `README.md` with live demo link, architecture diagram, persona workflows, and deployment commands.
- Commit clean codebase and verify remote push.

### Phase 2: PowerPoint Presentation Deck Generation
- Read template assets and background pictures from `Prototype Submission Template _ CoCo CLI Hackathon GCC Edition.pptx`.
- Programmatically generate `Prototype_Submission_AegisCortex_AI_CoCo_Hackathon.pptx` with high-resolution layout, typography, and embedded screenshots from `COCO Hackathon/`.
- Verify slide rendering and formatting.

### Phase 3: CoCo CLI Workflow Script & Video Production Guide
- Create `scripts/coco_cli_demo.py` for automated, visually stunning terminal screen recording.
- Write `docs/HACKATHON_DEMO_VIDEO_GUIDE.md` containing the 3-5 minute timestamped voiceover script and visual recording instructions.
- Validate end-to-end workflow execution.

---

## 4. Verification Checkpoints
- [ ] Checkpoint 1: Git repository contains only clean, relevant code without third-party dumps or large CSVs.
- [ ] Checkpoint 2: `README.md` is complete, beautifully formatted, and contains the working live link.
- [ ] Checkpoint 3: Generated `.pptx` opens cleanly with all slides populated and screenshots placed.
- [ ] Checkpoint 4: `scripts/coco_cli_demo.py` executes end-to-end without errors.
