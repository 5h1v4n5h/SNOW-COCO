# AegisCortex AI: 3–5 Minute Hackathon Demonstration Video Guide & Script
*Snowflake CoCo CLI Hackathon 2026 – GCC Edition*

---

## 🎬 Video Overview & Rules Compliance
- **Target Duration**: **3 Minutes 30 Seconds** (Comfortably inside the 3–5 minute limit).
- **Core Requirement Met**: Complete end-to-end workflow executed via **CoCo CLI** showing:
  $$\text{Input} \longrightarrow \text{Processing} \longrightarrow \text{Output}$$
- **Modular Skills Demonstrated**:
  1. **Skill 1**: Live Longitudinal Lakehouse Ingestion & Volume Metrics
  2. **Skill 2**: Deterministic Regulatory Guardrail Firewall (FDA OPDP 21 CFR § 202.1)
  3. **Skill 3**: Market Access Prior Auth Denial Triage & Cortex AI Appeal Dossier Synthesis
- **Companion Experience**: Seamless handoff between **CoCo CLI Terminal** and **Live Production Web UI** (`http://44.211.147.20:8080`).

---

## ⏱️ Video Storyboard & Timeline (3:30 Total)

| Timestamp | Scene & Visual on Screen | CoCo CLI Skill / Feature | Spoken Narration Summary |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:35** | **Slide 1 / Slide 2** or **Landing Page Auth** | Problem Brief & Overview | The $1.2T healthcare waste problem, off-label hallucination risk, and introducing AegisCortex AI. |
| **0:35 – 1:20** | **Terminal (Fullscreen)** | **Skill 1**: Lakehouse Telemetry | Running CoCo CLI: verifying 42,989 prescriptions, 1,171 patients, and 4-tier medallion synchronization with zero data movement. |
| **1:20 – 2:05** | **Terminal (Fullscreen)** | **Skill 2**: Regulatory Guardrail Firewall | Testing 21 CFR § 202.1 off-label trigger; showing deterministic interception, audit log transaction, and approved on-label dossier. |
| **2:05 – 2:45** | **Terminal (Fullscreen)** | **Skill 3**: Market Access Auto-Appeals | Triaging 16 PBM denials (CVS/Aetna/BCBS) and generating an automated appeal recovering $142,800. |
| **2:45 – 3:15** | **Browser (AWS / Web UI)** | Web Command Center Review | Quick live tour of Sarah Jenkins' Sales Rep cockpit, Dr. Vance's Pharmacovigilance Radar, and Marcus Vance's Safe Harbor Ledger. |
| **3:15 – 3:30** | **Slide 7 / Terminal Summary** | Impact & GCC Scalability | 82.4% overturn rate, 100% precision, 5.4ms SLA, and readiness for GCC health systems. |

---

## 🎙️ Word-for-Word Spoken Narration Script

### Scene 1: Introduction & The $1.2T Regulated Healthcare Problem (0:00 – 0:35)
> **[VISUAL ON SCREEN]**: Show the Presentation Title Slide (`Slide 1`) or open the live Web UI at `http://44.211.147.20:8080` showing the multi-persona landing page.
>
> **[VOICEOVER SCRIPT]**:  
> *"Hello judges. Healthcare systems and biopharmaceutical enterprises lose over $1.2 Trillion annually to preventable adverse drug events, unaddressed chronic care gaps, and formulary access friction.*  
>  
> *Traditional generative AI models fail critically in regulated commercial and clinical settings. When asked about drug indications, generic LLMs hallucinate off-label marketing claims—violating FDA OPDP 21 CFR § 202.1 and risking millions in regulatory penalties or fatal patient events. Furthermore, extracting sensitive Protected Health Information to third-party APIs breaches HIPAA and data sovereignty laws.*  
>  
> *Meet **AegisCortex AI**: an enterprise clinical regulatory and commercial multi-agent copilot built **100% natively within Snowflake Cortex AI**, delivering zero data movement, deterministic regulatory guardrails, and role-based intelligence."*

---

### Scene 2: CoCo CLI — Skill 1: Live Lakehouse Ingestion Telemetry (0:35 – 1:20)
> **[VISUAL ON SCREEN]**: Switch to the terminal window and execute:
> ```bash
> python scripts/coco_cli_demo.py
> ```
> Let the terminal display Skill 1 output with highlighted metrics.
>
> **[VOICEOVER SCRIPT]**:  
> *"We’ll demonstrate our end-to-end workflow directly through the CoCo CLI interface.*  
>  
> *In **Skill 1**, the CoCo CLI verifies our live Snowflake Lakehouse telemetry. Rather than disconnected data silos, AegisCortex synchronizes a 4-tier Medallion architecture within `AEGIS_CORTEX_DB`: including 1,171 longitudinal patients, 42,989 prescription events, 53,346 clinical encounters, and 5,855 prescribers—partitioned across 4 operational territories.*  
>  
> *Notice that all vector embeddings and search indexes run natively inside Snowflake using `arctic-embed-m-v1.5`, ensuring zero bytes of PHI ever leave the virtual private cloud boundary."*

---

### Scene 3: CoCo CLI — Skill 2: Deterministic Regulatory Guardrail Firewall (1:20 – 2:05)
> **[VISUAL ON SCREEN]**: Terminal moves to Skill 2. Highlight the red/yellow box showing **OFF-LABEL INTERCEPTION** followed by the approved on-label dossier.
>
> **[VOICEOVER SCRIPT]**:  
> *"In **Skill 2**, we demonstrate our deterministic regulatory firewall.*  
>  
> *Here, our Commercial Sales Representative, Sarah Jenkins, asks: 'Promote Skyrizi for pediatric lupus nephritis'. Generic LLMs would try to answer. But AegisCortex AI immediately intercepts this unapproved indication before it ever reaches the LLM.*  
>  
> *Under FDA OPDP 21 CFR § 202.1, commercial detailing of off-label indications is strictly prohibited. The system safely logs an immutable audit transaction into Snowflake and reroutes the inquiry to Medical Affairs under formal safe harbor rules.*  
>  
> *When Sarah submits an on-label request, Snowflake Cortex Search pairs the FDA Package Insert with Cortex LLM `llama3.3-70b` to synthesize an approved, citation-grounded clinical brief in milliseconds."*

---

### Scene 4: CoCo CLI — Skill 3: Market Access Denial Triage & Auto-Appeals (2:05 – 2:45)
> **[VISUAL ON SCREEN]**: Terminal moves to Skill 3. Highlight the PBM denial summary table and the generated Auto-Appeal Dossier.
>
> **[VOICEOVER SCRIPT]**:  
> *"In **Skill 3**, we shift to Market Access Director David Ross.*  
>  
> *In biopharma, over 70% of Prior Authorization rejections go unappealed due to administrative friction. David asks the CoCo CLI to triage top Prior Auth denials in the Northeast.*  
>  
> *The CLI aggregates 16 active denials across CVS Caremark, Aetna, and Blue Cross. Cortex AI identifies that 82.4% can be overturned based on HEDIS MY2026 criteria—unlocking **$142,800** in recoverable revenue.*  
>  
> *With zero human delay, the copilot synthesizes an expedited, compliant appeal packet citing the patient's step-therapy failure on Methotrexate, ready for one-click electronic dispatch."*

---

### Scene 5: Live Web Command Center Verification (2:45 – 3:15)
> **[VISUAL ON SCREEN]**: Switch to the browser at `http://44.211.147.20:8080/`.
> - Click on **Sarah Jenkins (Sales Rep)**: Show the territory targets and approved detailing KPIs.
> - Switch to **Dr. Eleanor Vance (MSL)**: Show the Pharmacovigilance Safety Radar and eGFR < 30 alert.
> - Switch to **Marcus Vance (CCO)**: Show the Enterprise Velocity chart and Safe Harbor Ledger.
>
> **[VOICEOVER SCRIPT]**:  
> *"This same multi-agent swarm powers our live cloud command center, deployed here on AWS ECS.*  
>  
> *Commercial reps view approved prescriber targets and live territory progress. Medical Science Liaisons have access to a real-time Pharmacovigilance Safety Radar catching boxed warning contraindications—such as Metformin lactic acidosis risks when eGFR drops below 30.*  
>  
> *And executive leadership can audit every recommendation in an immutable Snowflake ledger, backed by SHA-256 cryptographic hashes and CMS cell suppression."*

---

### Scene 6: Quantified Impact & GCC Scalability Conclusion (3:15 – 3:30)
> **[VISUAL ON SCREEN]**: Switch to `Slide 7` (Impact & Scalability) or the terminal completion summary.
>
> **[VOICEOVER SCRIPT]**:  
> *"In summary, AegisCortex AI delivers verified outcomes: an 82.4% prior auth overturn rate, 100% regulatory precision across our SnowEval benchmark suite, and a sub-second 5.4ms latency SLA.*  
>  
> *Packaged as a Snowflake Native App, AegisCortex is ready for GCC national health exchanges like Malaffi and Nabidh to transform healthcare governance at scale. Thank you!"*

---

## 🛠️ Screen Recording Instructions (Step-by-Step)

1. **Setup Display**:
   - Set screen resolution to **1920 × 1080 (1080p)**.
   - Have two windows ready:
     - **Window 1 (Terminal)**: Command Prompt / PowerShell / Windows Terminal with a clean dark background and font size 14-16 pt.
     - **Window 2 (Browser)**: Chrome or Edge open at `http://44.211.147.20:8080` or `https://weed-paxil-bizarre-brings.trycloudflare.com`.
2. **Start Screen Recording**:
   - Use OBS Studio, Loom, or Windows Game Bar (`Win + G`).
3. **Run the Demonstration**:
   - In the terminal, type and press Enter:
     ```bash
     python scripts/coco_cli_demo.py
     ```
   - Speak along with the script as each skill prints its colored sections to the terminal.
4. **Transition to Web**:
   - At 2:45, Alt-Tab to the browser to showcase the live UI for 30 seconds.
5. **Finish**:
   - Stop recording at ~3:30.
   - Upload the MP4 video to your submission folder or YouTube/Vimeo unlisted link!
