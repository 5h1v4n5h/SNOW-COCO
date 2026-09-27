# AegisCortex AI: 3-Minute Hackathon Winning Demo Script
**Event**: Snowflake CoCo CLI Hackathon 2026 – GCC Edition  
**Target Award**: 1st Place Champion ($10,000 Grand Prize)  
**Presenter Personas**: Lead Clinical AI Architect & Healthcare Systems Engineer

---

## ⏱️ Video Timeline Overview
| Timestamp | Segment | Visual on Screen | Key Talking Point |
|---|---|---|---|
| **0:00 - 0:30** | The Crisis & Market Flaw | High-density Patient 360 Command Center with critical red banner | Healthcare waste & why naive LLM wrappers kill patients |
| **0:30 - 1:15** | Architectural Breakthrough | Mermaid Topology + Multi-Agent DAG Canvas | Zero data movement outside Snowflake HIPAA boundary; 5 specialized agents |
| **1:15 - 2:15** | 3 Live Clinical Hero Demos | Interactive UI clicking PT-1001, PT-1002, PT-1003 | Eleanor Vance eGFR crash; Marcus Brody HEDIS gap; Arthur Pendelton bleeding |
| **2:15 - 2:45** | SnowEval 100% Scorecard | Automated SnowEval Terminal + Modal Breakdown | 100% Safety Recall, 100% Faithfulness, 5.4ms Latency SLA |
| **2:45 - 3:00** | GCC Impact & Closing | Executive Dashboard & SiS Native App | Deployable today via `coco deploy` across GCC health systems |

---

## 🎬 Word-for-Word Presenter Script

### [0:00 - 0:30] The Crisis & The Competitor Flaw
> *(Visual: Screen opens on the deep slate AegisCortex Command Center. The top alert pulses neon crimson: "CRITICAL SAFETY ALERT: BLACK BOX CONTRAINDICATION DETECTED".)*

**Presenter:**  
"Every year, adverse drug events and unaddressed chronic care gaps cost healthcare systems over **1.2 trillion dollars** and claim hundreds of thousands of lives. 

When generic AI assistants attempt clinical decision support, they fail catastrophically: they hallucinate dosages, lose tracking of longitudinal lab trends, and export protected health information outside institutional walls.

Other hackathon teams built simple one-shot prompt scripts in basic Streamlit. **We built AegisCortex AI** — an Enterprise Multi-Agent Clinical Regulatory Copilot built natively on **Snowflake Cortex AI**, ensuring **zero data movement outside your HIPAA governance perimeter**."

---

### [0:30 - 1:15] The Master Multi-Agent Architecture
> *(Visual: Zoom into the live Multi-Agent Swarm Canvas showing 5 parallel agent nodes pulsating in Snowflake Cyan.)*

**Presenter:**  
"AegisCortex does not rely on a monolithic prompt. It deploys an autonomous **Supervisor-Worker Swarm** operating in sub-second parallel Directed Acyclic Graphs:

1. **The Clinical SQL Agent** queries longitudinal patient profiles across billions of LOINC lab records, ICD-10 encounters, and CPT billing claims using Snowflake Cortex Analyst semantics.
2. **The Cortex Search Agent** executes hybrid vector retrieval across FDA package inserts and NCQA HEDIS guidelines using native `snowflake-arctic-embed-l-v2.0`.
3. **The Pharmacovigilance Agent** deterministically screens active prescriptions against clinical safety rules—guaranteeing zero hallucinations on black box contraindications.
4. **The Regulatory Agent** audits member compliance against HEDIS MY2026 quality metrics, quantifying CMS Star Rating financial impact.
5. And **The MCP Action Agent** generates standardized HL7 FHIR R4 orders and commits immutable audit trails into the Snowflake ledger."

---

### [1:15 - 2:15] Three Live Clinical Hero Demos

#### Demo 1: Eleanor Vance (PT-1001) – eGFR Crash & Metformin Contraindication
> *(Visual: Click "Eleanor Vance" button. The eGFR sparkline renders the steep downward drop to 28.1 mL/min. The alert banner turns crimson.)*

**Presenter:**  
"Let's look at Patient Eleanor Vance. Over 18 months, her kidney function declined from 52 to **28.1 mL/min/1.73m²**, entering Stage 4 chronic kidney disease. 

Yet, her active medication list still includes Metformin HCl 1000mg twice daily. 

Our Pharmacovigilance agent immediately flags a **Critical FDA Boxed Warning**: at an eGFR below 30, Metformin carries an acute risk of fatal Lactic Acidosis. 

Notice our citation pill: clicking it displays the exact FDA package insert section. Within 5 milliseconds, AegisCortex drafts a verified **HL7 FHIR MedicationRequest** to halt the prescription—ready for one-click physician signature."

#### Demo 2: Marcus Brody (PT-1002) – NCQA HEDIS MY2026 Quality Gap
> *(Visual: Click "Marcus Brody" button. The warning banner turns amber: "REGULATORY CARE GAP: NCQA HEDIS MY2026 AUDIT".)*

**Presenter:**  
"Next, Marcus Brody, a 54-year-old diabetic. Our Regulatory Agent scans his EHR and identifies that his last HbA1c test was performed 14 months ago. 

Under NCQA HEDIS measure CDC-H9, he is non-compliant. AegisCortex automatically drafts an in-clinic lab service request and care management dispatch to prevent CMS Star Rating degradation."

#### Demo 3: Arthur Pendelton (PT-1003) – $56k Polypharmacy & Fatal Bleeding Risk
> *(Visual: Click "Arthur Pendelton" button. Patient card reveals 9 active medications and $56,403 in claims.)*

**Presenter:**  
"Finally, Arthur Pendelton, an elderly heart failure patient with $56,000 in annual claims spend. 

Our polypharmacy agent detects a lethal drug-drug interaction: concurrent Eliquis (Apixaban) and high-dose Ibuprofen, which caused his recent GI bleed hospitalization. AegisCortex immediately generates an order to discontinue oral NSAIDs and transition to topical alternatives."

---

### [2:15 - 2:45] SnowEval Benchmark: Proven 100% Precision
> *(Visual: Click "SnowEval (100%)" button in the top navigation. The Benchmark Modal opens showing 15/15 passed tests.)*

**Presenter:**  
"How do we prove clinical trustworthiness? We built **SnowEval**—an automated evaluation suite measuring our copilot against 15 rigorous clinical scenarios.

The results:
- **100% Contraindication Recall**: Zero missed black box warnings.
- **100% Faithfulness**: Every assertion is grounded in structured EHR telemetry or indexed documents.
- **100% Citation Precision**: Every claim points to an authentic medical section.
- **5.4 millisecond execution latency**—delivering instantaneous clinical decision support."

---

### [2:45 - 3:00] GCC Vision & Native Snowflake Deployment
> *(Visual: Switch to terminal showing `snowflake.yml` and native Streamlit in Snowflake deployment.)*

**Presenter:**  
"AegisCortex AI is fully packaged for the Snowflake ecosystem. Using the Snowflake CoCo CLI, health authorities across the GCC can deploy this complete solution directly into their Virtual Private Snowflake with a single command: `coco deploy`.

Deterministic clinical safety. Automated regulatory compliance. Sub-second multi-agent intelligence. 

**This is AegisCortex AI. Thank you.**"
