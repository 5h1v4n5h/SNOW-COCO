# Task List: Hackathon Submission Package, Slides & Video

## Phase 1: Clean Codebase & Production README

### Task 1: Clean Git Hygiene and Update `.gitignore`
**Description:** Configure `.gitignore` to omit `agency-agents/`, `agency-swarm/`, `system_prompts_leaks/`, `.claude-flow/`, `.claude/`, `.swarm/`, `Downloads/`, `synthea_sample/`, scratch folders, and large CSV dumps. Unstage any unwanted files.

**Acceptance criteria:**
- [x] `.gitignore` contains rules for all third-party repositories and large data dumps.
- [x] `git status` shows only clean, intentional project files (no `agency-agents`, `agency-swarm`, or ~120MB CSVs).

**Verification:**
- [x] Run `git status` to verify staged/untracked list is clean.

**Dependencies:** None  
**Files likely touched:**
- `.gitignore`

**Estimated scope:** Small (1 file)

---

### Task 2: Author Comprehensive Production `README.md`
**Description:** Write an exhaustive, high-impact `README.md` featuring the project overview, live demo URL (`https://weed-paxil-bizarre-brings.trycloudflare.com`), full Mermaid architecture diagram, 4 persona user flows, CoCo CLI skill showcase, and step-by-step deploy/run instructions.

**Acceptance criteria:**
- [x] Live demo link prominently displayed at top with clear call-to-action.
- [x] Clear project summary explaining the business and clinical problem.
- [x] Mermaid diagram illustrating Snowflake Lakehouse, Cortex AI, Multi-Agent Swarm, and Web/CLI layers.
- [x] Detailed description of the 4 role personas (Sales Rep, Market Access, MSL, CCO).
- [x] Clear instructions for local setup, CLI usage, and Snowflake deployment.

**Verification:**
- [x] Review markdown file and verify all sections, badges, and links.

**Dependencies:** Task 1  
**Files likely touched:**
- `README.md`

**Estimated scope:** Medium (1 file)

---

### Task 3: Git Commit and Push to GitHub
**Description:** Stage all clean files and commit with a structured semantic commit message, then push to `origin main`.

**Acceptance criteria:**
- [ ] Clean commit created.
- [ ] `git push origin main` executed successfully.

**Verification:**
- [ ] `git status` returns clean working tree.

**Dependencies:** Tasks 1, 2  
**Files likely touched:**
- Repository working tree

**Estimated scope:** Small (terminal commands)

---

## Checkpoint 1: Codebase & GitHub Cleanliness
- [x] Repository contains clean, relevant code without third-party agent dumps or binary artifacts.
- [x] `README.md` renders cleanly with live link, architecture, and user flows.

---

## Phase 2: Hackathon Presentation Slides Deck (`.pptx`)

### Task 4: Build Presentation Generator Using Hackathon Template
**Description:** Create a Python script (`scripts/generate_submission_deck.py`) that uses `python-pptx` to build a complete 7-slide submission deck matching `Prototype Submission Template _ CoCo CLI Hackathon GCC Edition.pptx` branding.

**Acceptance criteria:**
- [ ] Slide 1: Title & Team Details (AegisCortex AI, Shivansh Srivastava, Problem Statement).
- [ ] Slide 2: Problem Brief & Domain Context ($1.2T waste, compliance risk, disjointed workflows).
- [ ] Slide 3: Proposed Architecture & Modular CoCo CLI Skills (Snowflake Cortex AI, Lakehouse, Multi-Agent Swarm).
- [ ] Slide 4: Persona Matrix & Solution Capabilities.
- [ ] Slide 5: Website Review: Commercial & Market Access (incorporating screenshots from `COCO Hackathon/Sales rep` and `COCO Hackathon/Regional`).
- [ ] Slide 6: Website Review: Clinical Affairs & Executive Leadership (incorporating screenshots from `COCO Hackathon/National Medical Affairs` and `COCO Hackathon/Cheif_commercial_officer`).
- [ ] Slide 7: Impact Statement & Beyond the Demo (quantifiable metrics, 82% overturn, 100% compliance).

**Verification:**
- [ ] Script runs and outputs `Prototype_Submission_AegisCortex_AI_CoCo_Hackathon.pptx`.
- [ ] File inspected for valid shapes, text boxes, and embedded images.

**Dependencies:** None  
**Files likely touched:**
- `scripts/generate_submission_deck.py`
- `Prototype_Submission_AegisCortex_AI_CoCo_Hackathon.pptx`

**Estimated scope:** Medium (1 script + output deck)

---

## Checkpoint 2: Presentation Deck Ready
- [ ] Presentation generated and verified with 7 complete slides and embedded screenshots.

---

## Phase 3: 3–5 Minute Video Script & CoCo CLI Demonstration

### Task 5: Implement Automated CoCo CLI Interactive Workflow
**Description:** Create `scripts/coco_cli_demo.py` to run an automated, visually impressive terminal recording showing Input → Processing → Output across 3 modular skills: Ingestion/Metrics, Deterministic Guardrail Firewall, and Cortex AI Strategic Synthesis.

**Acceptance criteria:**
- [ ] CLI runs in automated demo mode with realistic typing/timing or prompt flags.
- [ ] Demonstrates Skill 1: Live Snowflake Lakehouse Ingestion & Volume Metrics.
- [ ] Demonstrates Skill 2: Deterministic Regulatory Guardrail Firewall (21 CFR § 202.1 & OPDP enforcement).
- [ ] Demonstrates Skill 3: Contextual Snowflake Cortex AI Synthesis (`llama3.3-70b`) translating metrics into concrete actions.

**Verification:**
- [ ] Execute `python scripts/coco_cli_demo.py` and confirm clean, error-free output.

**Dependencies:** None  
**Files likely touched:**
- `scripts/coco_cli_demo.py`

**Estimated scope:** Small to Medium (1 file)

---

### Task 6: Author Scene-by-Scene Video Guide & Voiceover Script
**Description:** Create `docs/HACKATHON_DEMO_VIDEO_GUIDE.md` containing a 3.5-minute scene-by-scene storyboard, screen recording visual cues, and a word-for-word spoken voiceover script.

**Acceptance criteria:**
- [ ] Timeline covers exactly 3 to 4 minutes (fits the 3-5 minute constraint).
- [ ] Clear visual instructions for what to show on screen at each second (CoCo CLI terminal recording vs. live Web UI interactions).
- [ ] High-impact, professional spoken script emphasizing GCC healthcare transformation, Snowflake Cortex AI, and autonomous multi-agent governance.

**Verification:**
- [ ] Review script word count and pacing (~450-550 words for 3.5 minutes).

**Dependencies:** Tasks 4, 5  
**Files likely touched:**
- `docs/HACKATHON_DEMO_VIDEO_GUIDE.md`

**Estimated scope:** Medium (1 file)

---

## Checkpoint 3: Complete Hackathon Package Ready
- [ ] Git repo clean and pushed.
- [ ] Submission PPTX finalized and visually reviewed.
- [ ] CoCo CLI workflow script operational.
- [ ] Video guide and script ready for immediate recording.
