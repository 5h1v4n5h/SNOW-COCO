# DESIGN.md: AegisCortex AI Design System
*Clinical Intelligence Command Center Specification*

## 1. Design Read & Philosophy
- **Design Read**: Mission-critical Clinical & Regulatory Intelligence Platform for GCC healthcare leaders, clinicians, and health plans. High visual clarity, deterministic trust signals, and zero generic AI slop.
- **Dials**: `DESIGN_VARIANCE: 7` | `MOTION_INTENSITY: 6` | `VISUAL_DENSITY: 8`
- **Typography**: 
  - Primary UI: `Geist Sans`, `Inter`, `-apple-system`, sans-serif
  - Telemetry & Data / Codes: `Geist Mono`, `JetBrains Mono`, monospace
  - Heading Display: `Plus Jakarta Sans` / `Geist Sans` (Bold, tight tracking `-0.02em`)

---

## 2. Color Palette & Semantic Tokens

```css
:root {
  /* Surfaces */
  --bg-primary: #07090E;         /* Deep void slate */
  --bg-surface: #0E131F;         /* Elevated card surface */
  --bg-surface-elevated: #161D2E;/* Popovers & Modals */
  --bg-surface-glass: rgba(14, 19, 31, 0.75);

  /* Borders & Dividers */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-prominent: rgba(41, 181, 232, 0.25);
  --border-active: #29B5E8;

  /* Brand Accents */
  --snowflake-blue: #29B5E8;     /* Snowflake Primary Cyan */
  --snowflake-glow: rgba(41, 181, 232, 0.15);
  --cortex-indigo: #6366F1;      /* Cortex AI Secondary */

  /* Clinical Status Semantics */
  --clinical-safe: #10B981;       /* Safe / HEDIS Compliant */
  --clinical-safe-bg: rgba(16, 185, 129, 0.12);
  --clinical-warning: #F59E0B;    /* Overdue screening / Care Gap */
  --clinical-warning-bg: rgba(245, 158, 11, 0.12);
  --clinical-critical: #EF4444;   /* Contraindication / Black Box Warning */
  --clinical-critical-bg: rgba(239, 68, 68, 0.15);
  
  /* Text */
  --text-primary: #F8FAFC;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
  --text-accent: #38BDF8;
}
```

---

## 3. Component Design Patterns

### A. Patient Telemetry Header & Risk Sparklines
- Grid layout with patient avatar, demographic badge, real-time risk score pill (`HIGH RISK - 84/100`), and sparkline graphs for eGFR trajectory (highlighting the slope drop from 52 to 28 mL/min).

### B. Live Multi-Agent Orchestration Canvas
- Step-by-step parallel pipeline indicator:
  - `[Supervisor Triage]` → `[SQL Agent]` + `[Doc Search Agent]` → `[Safety & Pharmacovigilance]` → `[Consensus Synthesis]`.
  - Visual status pill: Animated pulse for active agent, checkmark for completed agent with execution latency (e.g. `240ms`).

### C. Citation Pill & Interactive Evidence Drawer
- Formatted as: `[Doc: Metformin_FDA_Insert.pdf, p. 4]` with a distinct cyan-accented badge.
- **Interaction**: Clicking any citation opens the side-drawer showing the exact document page, bounding box preview, and raw excerpt with verified confidence score.

### D. MCP Clinical Action Hub
- Interactive action cards:
  - `Physician Prescription Override Alert` (Pre-filled with ICD-10, LOINC eGFR, and FDA citation)
  - `HEDIS Care Gap Scheduling Ticket` (Direct Slack / Jira / EHR webhook payload)
  - Includes `Dispatch Action` button with simulated audit ledger confirmation.

---

## 4. Anti-Slop Check & Discipline
- ❌ No centered hero with empty generic copy.
- ❌ No purple/pink generic AI gradient meshes.
- ❌ No ungrounded chat responses without citations.
- ✅ Dense, high-value clinical metrics visible immediately upon load.
- ✅ Instant interactive filter by patient, condition, risk decile, and doctor.
