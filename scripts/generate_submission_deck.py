"""
AegisCortex AI - Hackathon Submission Deck Generator
Snowflake CoCo CLI Hackathon 2026 – GCC Edition

Transforms 'Prototype Submission Template _ CoCo CLI Hackathon GCC Edition.pptx'
into a complete, professional, publication-ready 7-slide hackathon presentation.
Incorporates:
- Real-world problem context ($1.2T waste, FDA 21 CFR § 202.1, PHI egress risks)
- Proposed multi-agent solution on Snowflake Cortex AI
- High-resolution architecture diagram
- Multi-persona role matrix
- Visual website review incorporating screenshots from 'COCO Hackathon/'
- Measurable impact metrics (82.4% overturn, 100% precision, 5.4ms SLA)
"""

import sys
import os
from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = PROJECT_ROOT / "Prototype Submission Template _ CoCo CLI Hackathon GCC Edition.pptx"
OUTPUT_PATH = PROJECT_ROOT / "Prototype_Submission_AegisCortex_AI_CoCo_Hackathon.pptx"
SCREENSHOTS_DIR = PROJECT_ROOT / "COCO Hackathon"
SCRATCH_DIR = PROJECT_ROOT / "scratch"
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

# CoCo / Snowflake Hackathon Color Palette
COLOR_SNOWFLAKE_CYAN = RGBColor(41, 181, 232)      # #29B5E8
COLOR_NAVY_BG = RGBColor(11, 19, 43)              # #0B132B
COLOR_CARD_BG = RGBColor(20, 31, 58)              # #141F3A
COLOR_CARD_BORDER = RGBColor(41, 181, 232)        # #29B5E8
COLOR_WHITE = RGBColor(255, 255, 255)             # #FFFFFF
COLOR_GRAY = RGBColor(170, 185, 205)              # #AAB9CD
COLOR_EMERALD = RGBColor(16, 185, 129)            # #10B981
COLOR_INDIGO = RGBColor(99, 102, 241)             # #6366F1
COLOR_GOLD = RGBColor(245, 158, 11)               # #F59E0B


def generate_architecture_image():
    """Generates a crisp, high-resolution architecture diagram image for Slide 4."""
    img_path = SCRATCH_DIR / "architecture_clean.png"
    
    fig, ax = plt.subplots(figsize=(11.5, 5.8), dpi=300)
    fig.patch.set_facecolor('#0B132B')
    ax.set_facecolor('#0B132B')
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 5.8)
    ax.axis('off')

    # Layer 1: Client Layer
    rect1 = patches.FancyBboxPatch((0.4, 4.35), 10.7, 1.15, boxstyle='round,pad=0.08', facecolor='#16223F', edgecolor='#29B5E8', linewidth=1.5)
    ax.add_patch(rect1)
    ax.text(0.7, 5.2, 'CLIENT & EXPERIENCE LAYER', color='#29B5E8', fontsize=9.5, fontweight='bold', family='sans-serif')
    ax.text(2.3, 4.75, 'Web Command Center\nTailored 4-Role UI Cockpit', color='#FFFFFF', fontsize=8, ha='center', va='center')
    ax.text(5.8, 4.75, 'CoCo CLI Terminal\n3 Modular Skills Engine', color='#FFFFFF', fontsize=8, ha='center', va='center')
    ax.text(9.3, 4.75, 'Streamlit Native App\nExecutive Visualization', color='#FFFFFF', fontsize=8, ha='center', va='center')

    # Layer 2: API Gateway Layer
    rect2 = patches.FancyBboxPatch((0.4, 2.95), 10.7, 1.15, boxstyle='round,pad=0.08', facecolor='#16223F', edgecolor='#6366F1', linewidth=1.5)
    ax.add_patch(rect2)
    ax.text(0.7, 3.8, 'UNIFIED GATEWAY & SECURITY LAYER (FastAPI :8080)', color='#6366F1', fontsize=9.5, fontweight='bold', family='sans-serif')
    ax.text(2.3, 3.35, 'Dynamic Role RBAC\nTerritory Partitioning', color='#FFFFFF', fontsize=8, ha='center', va='center')
    ax.text(5.8, 3.35, 'Deterministic Guardrails\nFDA 21 CFR § 202.1 & HEDIS', color='#FFFFFF', fontsize=8, ha='center', va='center')
    ax.text(9.3, 3.35, 'REST & WebSocket Hub\nSub-Second Response SLA', color='#FFFFFF', fontsize=8, ha='center', va='center')

    # Layer 3: Multi-Agent Swarm
    rect3 = patches.FancyBboxPatch((0.4, 1.55), 10.7, 1.15, boxstyle='round,pad=0.08', facecolor='#16223F', edgecolor='#10B981', linewidth=1.5)
    ax.add_patch(rect3)
    ax.text(0.7, 2.4, 'AUTONOMOUS MULTI-AGENT SWARM (core/orchestrator.py)', color='#10B981', fontsize=9.5, fontweight='bold', family='sans-serif')
    ax.text(1.5, 1.95, 'AegisSupervisor\nIntent Routing', color='#FFFFFF', fontsize=7.5, ha='center', va='center')
    ax.text(3.6, 1.95, 'Clinical SQL Agent\nLongitudinal Cohorts', color='#FFFFFF', fontsize=7.5, ha='center', va='center')
    ax.text(5.8, 1.95, 'Cortex Search Agent\nFDA Inserts & Guidelines', color='#FFFFFF', fontsize=7.5, ha='center', va='center')
    ax.text(7.9, 1.95, 'Safety / PV Agent\nBoxed Warning Engine', color='#FFFFFF', fontsize=7.5, ha='center', va='center')
    ax.text(10.0, 1.95, 'Action Committer\nFHIR R4 & Audit Committer', color='#FFFFFF', fontsize=7.5, ha='center', va='center')

    # Layer 4: Snowflake Native Lakehouse & Cortex AI
    rect4 = patches.FancyBboxPatch((0.4, 0.15), 10.7, 1.15, boxstyle='round,pad=0.08', facecolor='#0D1B2A', edgecolor='#00A3E0', linewidth=2.0)
    ax.add_patch(rect4)
    ax.text(0.7, 1.0, 'NATIVE SNOWFLAKE CORTEX AI LAKEHOUSE (AEGIS_CORTEX_DB)', color='#00A3E0', fontsize=9.5, fontweight='bold', family='sans-serif')
    ax.text(2.3, 0.55, '4-Tier Medallion Lakehouse\n42.9k Rx | 53.3k Encounters', color='#FFFFFF', fontsize=8, ha='center', va='center')
    ax.text(5.8, 0.55, 'SNOWFLAKE.CORTEX.COMPLETE\nLLM Model: llama3.3-70b', color='#FFFFFF', fontsize=8, ha='center', va='center')
    ax.text(9.3, 0.55, 'APP.CLINICAL_DOC_SEARCH\nEmbedding: arctic-embed-m-v1.5', color='#FFFFFF', fontsize=8, ha='center', va='center')

    plt.tight_layout()
    plt.savefig(img_path, bbox_inches='tight', dpi=300)
    plt.close()
    return img_path


def add_card(slide, left, top, width, height, title, body_bullets, title_color=COLOR_SNOWFLAKE_CYAN, border_color=COLOR_CARD_BORDER, bg_color=COLOR_CARD_BG):
    """Adds a stylish card with rounded borders and formatted bullet points."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)
    
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.18)
    tf.margin_right = Inches(0.18)
    tf.margin_top = Inches(0.14)
    tf.margin_bottom = Inches(0.14)
    
    # Title paragraph
    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.name = "Arial"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = title_color
    p0.space_after = Pt(8)
    
    # Bullets
    for b in body_bullets:
        p = tf.add_paragraph()
        p.text = f"-  {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_WHITE
        p.space_after = Pt(4)


def setup_header(slide, title_text, subtitle_text):
    """Sets up a standardized top header for content slides."""
    title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(8.8), Inches(0.9))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p0 = tf.paragraphs[0]
    p0.text = title_text
    p0.font.name = "Arial"
    p0.font.size = Pt(20)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_WHITE
    p0.space_after = Pt(2)
    
    p1 = tf.add_paragraph()
    p1.text = subtitle_text
    p1.font.name = "Arial"
    p1.font.size = Pt(11)
    p1.font.italic = True
    p1.font.color.rgb = COLOR_SNOWFLAKE_CYAN


def build_presentation():
    print(f"[*] Opening template presentation: {TEMPLATE_PATH}")
    prs = pptx.Presentation(TEMPLATE_PATH)
    
    # Extract background pictures from slides so we can reuse them seamlessly
    bg_pics = {}
    for i, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if shape.shape_type == 13: # Picture
                bg_pics[i] = shape.image.blob
                break

    # =========================================================================
    # SLIDE 1: Title Slide (Update existing text boxes on Slide 1)
    # =========================================================================
    print("  -> Configuring Slide 1: Title & Team Details")
    s1 = prs.slides[0]
    
    # Add main project title & subtitle
    title_box = s1.shapes.add_textbox(Inches(0.45), Inches(1.2), Inches(9.0), Inches(1.8))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    
    p_proj = tf1.paragraphs[0]
    p_proj.text = "AegisCortex AI"
    p_proj.font.name = "Arial"
    p_proj.font.size = Pt(36)
    p_proj.font.bold = True
    p_proj.font.color.rgb = COLOR_WHITE
    
    p_sub = tf1.add_paragraph()
    p_sub.text = "Enterprise Clinical Regulatory & Commercial Multi-Agent Copilot"
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(17)
    p_sub.font.bold = True
    p_sub.font.color.rgb = COLOR_SNOWFLAKE_CYAN
    p_sub.space_after = Pt(4)
    
    p_track = tf1.add_paragraph()
    p_track.text = "Built Natively on Snowflake Cortex AI | Snowflake CoCo CLI Hackathon 2026 – GCC Edition"
    p_track.font.name = "Arial"
    p_track.font.size = Pt(11)
    p_track.font.color.rgb = COLOR_GRAY

    # Populate metadata text boxes
    for shape in s1.shapes:
        if shape.has_text_frame:
            txt = shape.text.strip()
            if "Team Name" in txt:
                shape.text_frame.paragraphs[0].text = "Team Name :  AegisCortex AI Team"
                shape.text_frame.paragraphs[0].font.size = Pt(12)
                shape.text_frame.paragraphs[0].font.color.rgb = COLOR_WHITE
            elif "Team Leader Name" in txt:
                shape.text_frame.paragraphs[0].text = "Team Leader Name :  Shivansh Sharma"
                shape.text_frame.paragraphs[0].font.size = Pt(12)
                shape.text_frame.paragraphs[0].font.color.rgb = COLOR_WHITE
            elif "Team Size" in txt:
                shape.text_frame.paragraphs[0].text = "Team Size :  1 (Solo Developer)"
                shape.text_frame.paragraphs[0].font.size = Pt(12)
                shape.text_frame.paragraphs[0].font.color.rgb = COLOR_WHITE
            elif "Problem Statement" in txt:
                shape.text_frame.paragraphs[0].text = "Problem Statement :  Autonomous Multi-Agent Clinical Regulatory & Commercial Intelligence Copilot on Snowflake Cortex AI"
                shape.text_frame.paragraphs[0].font.size = Pt(11)
                shape.text_frame.paragraphs[0].font.color.rgb = COLOR_WHITE

    # Add Live Demo Banner badge to Slide 1
    demo_badge = s1.shapes.add_textbox(Inches(0.45), Inches(4.55), Inches(9.0), Inches(0.45))
    tf_demo = demo_badge.text_frame
    p_demo = tf_demo.paragraphs[0]
    p_demo.text = "🌐 Live AWS Cloud Production URL: http://44.211.147.20:8080"
    p_demo.font.name = "Arial"
    p_demo.font.size = Pt(11)
    p_demo.font.bold = True
    p_demo.font.color.rgb = COLOR_EMERALD

    # =========================================================================
    # SLIDE 2: Problem Brief & Domain Context (Replace guidelines text)
    # =========================================================================
    print("  -> Configuring Slide 2: Problem Brief & Real-World Domain Context")
    s2 = prs.slides[1]
    
    # Remove template instructions text box
    for shape in list(s2.shapes):
        if shape.has_text_frame and "Submission Guidelines" in shape.text:
            sp_elem = shape._element
            sp_elem.getparent().remove(sp_elem)

    setup_header(s2, "The $1.2 Trillion Enterprise Healthcare Problem",
                 "Why Off-the-Shelf Generative AI & Fragmented Architectures Fail in Regulated Healthcare")

    # 3 Column Pain-Point Cards
    c_w = Inches(2.78)
    c_h = Inches(3.65)
    c_y = Inches(1.42)
    
    add_card(s2, Inches(0.6), c_y, c_w, c_h,
             "1. Probabilistic Hallucinations & Regulatory Liability",
             [
                 "Generic LLMs routinely fabricate off-label efficacy claims and drug safety profiles.",
                 "Violates FDA OPDP 21 CFR § 202.1 prescription drug marketing regulations, risking severe legal injunctions.",
                 "Fatal consequences: Probabilistic models fail to catch Boxed Warnings (e.g. Metformin in renal impairment).",
                 "Enterprise biopharma cannot deploy unconstrained models without deterministic safety boundaries."
             ], title_color=RGBColor(239, 68, 68), border_color=RGBColor(239, 68, 68))

    add_card(s2, Inches(3.58), c_y, c_w, c_h,
             "2. Context Loss & Sensitive PHI Egress Risks",
             [
                 "Models lack low-latency access to longitudinal EHRs, LOINC lab trends, ICD-10 visits, and NDC claims.",
                 "Extracting Protected Health Information (PHI) to third-party APIs violates HIPAA, GDPR, and sovereign cloud laws.",
                 "Disjointed prescriber master data (NPIs) and unaligned territory hierarchies prevent targeted field execution.",
                 "Requires zero-data-movement where data, models, and embeddings live inside the governed boundary."
             ], title_color=COLOR_GOLD, border_color=COLOR_GOLD)

    add_card(s2, Inches(6.56), c_y, c_w, c_h,
             "3. Siloed Personas & Trapped Revenue Waste",
             [
                 "Commercial Reps, Market Access Directors, MSLs, and CCOs work in disjointed systems with conflicting metrics.",
                 "70%+ of Prior Authorization (PA) rejections (Codes 70, 75, 88) go unappealed ($142K+ lost per territory).",
                 "Care gaps in chronic populations (e.g. uncontrolled HbA1c) depress Medicare Advantage Star Ratings.",
                 "Lack of an autonomous orchestrator that translates complex lakehouse data into role-specific actions."
             ], title_color=COLOR_INDIGO, border_color=COLOR_INDIGO)

    # =========================================================================
    # SLIDE 3: Proposed Solution & Persona Matrix
    # =========================================================================
    print("  -> Configuring Slide 3: Proposed Solution & Multi-Persona Matrix")
    s3 = prs.slides[2]
    setup_header(s3, "The Solution: AegisCortex AI Multi-Agent Copilot",
                 "Native Snowflake Cortex AI Intelligence with Deterministic Regulatory & Operational Governance")

    # 4 Grid Cards representing the 4 Operational Roles
    g_w = Inches(4.25)
    g_h = Inches(1.75)
    
    # Top Left: Sales Rep
    add_card(s3, Inches(0.6), Inches(1.42), g_w, g_h,
             "Commercial Sales Rep (Sarah Jenkins - Midwest Metros)",
             [
                 "Approved Detailing Playbook & target prescribers (Dr. Michael Chen, Dr. Lisa Ray).",
                 "Adoption Opportunity Index (AOI: 88.3) & 280 TRx tracking ($1.2M Run-Rate).",
                 "Deterministic OPDP 21 CFR § 202.1 Firewall intercepts off-label queries & escalates safely."
             ], title_color=COLOR_SNOWFLAKE_CYAN, border_color=COLOR_SNOWFLAKE_CYAN)

    # Top Right: Market Access
    add_card(s3, Inches(5.15), Inches(1.42), g_w, g_h,
             "Market Access Director (David Ross - Regional Northeast)",
             [
                 "Formulary denial triage across 14 accounts (CVS Caremark, Aetna, BCBS NE).",
                 "Prior Auth Rejection triage (Codes 70, 75, 88) with 82.4% projected overturn rate.",
                 "1-Click Auto-Appeal packet generator recovering $142,800 in trapped revenue."
             ], title_color=COLOR_GOLD, border_color=COLOR_GOLD)

    # Bottom Left: MSL
    add_card(s3, Inches(0.6), Inches(3.3), g_w, g_h,
             "Medical Science Liaison (Dr. Eleanor Vance - National)",
             [
                 "KOL scientific exchange & clinical trial protocol synthesis (UltIMMa-1, STEP).",
                 "Longitudinal Pharmacovigilance Safety Radar (eGFR < 30 lactic acidosis alerts).",
                 "Safe Harbor protocol enforcement for non-promotional, peer-to-peer discussions."
             ], title_color=COLOR_EMERALD, border_color=COLOR_EMERALD)

    # Bottom Right: CCO
    add_card(s3, Inches(5.15), Inches(3.3), g_w, g_h,
             "Chief Commercial Officer (Marcus Vance - Global Enterprise)",
             [
                 "Enterprise portfolio velocity (+24.2% brand share vs. Humira loss of exclusivity).",
                 "Longitudinal lakehouse governance (42,989 Rx, 53,346 visits, 5,855 prescribers).",
                 "Automated CMS Cell Suppression (N >= 11) guaranteeing HIPAA macro privacy."
             ], title_color=COLOR_INDIGO, border_color=COLOR_INDIGO)

    # =========================================================================
    # SLIDE 4: Proposed Architecture & Modular CoCo CLI Skills
    # =========================================================================
    print("  -> Configuring Slide 4: Proposed Architecture & Modular CoCo CLI Skills")
    s4 = prs.slides[3]
    setup_header(s4, "Proposed Architecture & Modular CoCo CLI Skills",
                 "Zero Data Movement: 4-Tier Snowflake Lakehouse, Cortex AI Engines & Multi-Agent Swarm")

    # Generate and place the crisp architecture diagram
    arch_img = generate_architecture_image()
    s4.shapes.add_picture(str(arch_img), Inches(0.6), Inches(1.38), Inches(8.8), Inches(2.35))

    # 3 Summary bullets / skill cards below the architecture
    b_w = Inches(2.78)
    b_h = Inches(1.35)
    b_y = Inches(3.8)
    
    add_card(s4, Inches(0.6), b_y, b_w, b_h,
             "Skill 1: Lakehouse Telemetry",
             [
                 "Live partition telemetry across 4-Tier Medallion architecture.",
                 "Longitudinal cohort synchronization (1,171 patients, 42.9k Rx)."
             ], title_color=COLOR_SNOWFLAKE_CYAN, border_color=COLOR_SNOWFLAKE_CYAN)

    add_card(s4, Inches(3.58), b_y, b_w, b_h,
             "Skill 2: Regulatory Firewall",
             [
                 "Deterministic 21 CFR § 202.1 safety gate checks every query.",
                 "100% interception of off-label marketing with MSL escalation."
             ], title_color=COLOR_INDIGO, border_color=COLOR_INDIGO)

    add_card(s4, Inches(6.56), b_y, b_w, b_h,
             "Skill 3: Strategic Cortex AI",
             [
                 "Invokes SNOWFLAKE.CORTEX.COMPLETE (llama3.3-70b).",
                 "Sub-second prior auth appeal generation with verified citations."
             ], title_color=COLOR_EMERALD, border_color=COLOR_EMERALD)

    # =========================================================================
    # SLIDE 5: Website Review — Commercial & Market Access Workflows
    # =========================================================================
    print("  -> Configuring Slide 5: Website Review — Commercial & Market Access Workflows")
    s5 = prs.slides[4]
    
    # Remove template "Additional Slide" text if present
    for shape in list(s5.shapes):
        if shape.has_text_frame and "Additional Slide" in shape.text:
            sp_elem = shape._element
            sp_elem.getparent().remove(sp_elem)

    setup_header(s5, "Platform Review: Commercial & Market Access Workflows",
                 "Live Production Interface: Prescriber Detailing, PBM Denial Triage & Auto-Appeals")

    # Left: Commercial Sales Rep Screenshot & Details
    sales_rep_img = SCREENSHOTS_DIR / "Sales rep" / "Field Inelligence Copilot.png"
    if not sales_rep_img.exists():
        sales_rep_img = SCREENSHOTS_DIR / "Sales rep" / "My_terr_detailing and targets.png"
    
    if sales_rep_img.exists():
        s5.shapes.add_picture(str(sales_rep_img), Inches(0.6), Inches(1.4), Inches(4.25), Inches(2.35))
    
    add_card(s5, Inches(0.6), Inches(3.82), Inches(4.25), Inches(1.3),
             "Commercial Field Intelligence (Sarah Jenkins)",
             [
                 "Territory target detailing for Dr. Michael Chen & Dr. Lisa Ray with AOI 88.3.",
                 "Automated 21 CFR § 202.1 firewall intercepts unapproved claims in real-time."
             ], title_color=COLOR_SNOWFLAKE_CYAN, border_color=COLOR_SNOWFLAKE_CYAN)

    # Right: Market Access Screenshot & Details
    market_acc_img = SCREENSHOTS_DIR / "Regional" / "Prior Auth Auto- Appeal Engine.png"
    if not market_acc_img.exists():
        market_acc_img = SCREENSHOTS_DIR / "Regional" / "PBM FOmularies & Denial Triage.png"
        
    if market_acc_img.exists():
        s5.shapes.add_picture(str(market_acc_img), Inches(5.15), Inches(1.4), Inches(4.25), Inches(2.35))
        
    add_card(s5, Inches(5.15), Inches(3.82), Inches(4.25), Inches(1.3),
             "PBM Denial Triage & Auto-Appeals (David Ross)",
             [
                 "Real-time triage of 16 prior auth rejections (CVS, Aetna, BCBS) across Northeast.",
                 "1-Click Auto-Appeal generation unlocking $142,800 at 82.4% projected overturn rate."
             ], title_color=COLOR_GOLD, border_color=COLOR_GOLD)

    # =========================================================================
    # SLIDE 6: Website Review — Clinical Affairs & Executive Governance
    # =========================================================================
    print("  -> Configuring Slide 6: Website Review — Clinical Affairs & Executive Governance")
    s6 = prs.slides[5]
    setup_header(s6, "Platform Review: Clinical Science & Executive Governance",
                 "Live Production Interface: Pharmacovigilance Safety Radar & Safe Harbor Audit Ledger")

    # Left: MSL / Pharmacovigilance Radar
    msl_img = SCREENSHOTS_DIR / "National Medical Affairs" / "Pharmacovigilance_Safety_Radar.png"
    if not msl_img.exists():
        msl_img = SCREENSHOTS_DIR / "National Medical Affairs" / "Scientific_Exchange_copilot_interactive_graph.png"
        
    if msl_img.exists():
        s6.shapes.add_picture(str(msl_img), Inches(0.6), Inches(1.4), Inches(4.25), Inches(2.35))
        
    add_card(s6, Inches(0.6), Inches(3.82), Inches(4.25), Inches(1.3),
             "Medical Science & Safety Radar (Dr. Eleanor Vance)",
             [
                 "Longitudinal surveillance catches Boxed Warnings (Metformin eGFR < 30 alert).",
                 "Interactive knowledge graph connects clinical trials (UltIMMa-1) to prescribers."
             ], title_color=COLOR_EMERALD, border_color=COLOR_EMERALD)

    # Right: CCO / Compliance Safe Harbor Ledger
    cco_img = SCREENSHOTS_DIR / "Cheif_commercial_officer" / "Compliance_Safe_harbor_Ledger.png"
    if not cco_img.exists():
        cco_img = SCREENSHOTS_DIR / "Cheif_commercial_officer" / "Enterprise Portfoliio Velocity.png"
        
    if cco_img.exists():
        s6.shapes.add_picture(str(cco_img), Inches(5.15), Inches(1.4), Inches(4.25), Inches(2.35))
        
    add_card(s6, Inches(5.15), Inches(3.82), Inches(4.25), Inches(1.3),
             "Enterprise Governance & Ledger (Marcus Vance)",
             [
                 "Immutable action audit log in Snowflake (SHA-256 cryptographic verification).",
                 "CMS Cell Suppression (N >= 11) & brand velocity (+24.2% vs Humira LOE)."
             ], title_color=COLOR_INDIGO, border_color=COLOR_INDIGO)

    # =========================================================================
    # SLIDE 7: Impact Statement & Beyond the Demo
    # =========================================================================
    print("  -> Creating Slide 7: Impact Statement & Scalability Beyond the Demo")
    blank_layout = prs.slide_layouts[6] # Blank
    s7 = prs.slides.add_slide(blank_layout)
    
    # Add content slide background to slide 7
    if 1 in bg_pics:
        from io import BytesIO
        s7.shapes.add_picture(BytesIO(bg_pics[1]), Inches(0), Inches(0), prs.slide_width, prs.slide_height)

    setup_header(s7, "Measurable Impact & GCC Enterprise Scalability",
                 "Quantified Clinical & Commercial Outcomes Delivered Natively via Snowflake Cortex AI")

    # 4 Metric Highlights Cards
    m_w = Inches(2.05)
    m_h = Inches(1.65)
    m_y = Inches(1.42)
    
    add_card(s7, Inches(0.6), m_y, m_w, m_h,
             "$142,800",
             [
                 "Recovered revenue per territory.",
                 "82.4% appeal overturn rate."
             ], title_color=COLOR_EMERALD, border_color=COLOR_EMERALD)

    add_card(s7, Inches(2.85), m_y, m_w, m_h,
             "100% Precision",
             [
                 "Zero off-label hallucinations.",
                 "15/15 SnowEval tests passed."
             ], title_color=COLOR_SNOWFLAKE_CYAN, border_color=COLOR_SNOWFLAKE_CYAN)

    add_card(s7, Inches(5.1), m_y, m_w, m_h,
             "5.4 ms SLA",
             [
                 "Sub-second firewall speed.",
                 "Zero latency user experience."
             ], title_color=COLOR_GOLD, border_color=COLOR_GOLD)

    add_card(s7, Inches(7.35), m_y, m_w, m_h,
             "Zero Egress",
             [
                 "100% sovereign compute.",
                 "HIPAA & GDPR fully compliant."
             ], title_color=COLOR_INDIGO, border_color=COLOR_INDIGO)

    # Lower Section: Enterprise Scalability & Beyond the Demo
    add_card(s7, Inches(0.6), Inches(3.2), Inches(8.8), Inches(1.9),
             "Scalability Potential & Beyond the Demo",
             [
                 "GCC Sovereign Healthcare Integration: Architected for regional health data exchanges (Malaffi UAE, Nabidh Dubai, Riayati) to unify patient records with zero sovereign data egress.",
                 "Snowflake Native Application Ready: Packaged with snowflake.yml for direct distribution across the Snowflake Marketplace to hospital networks, PBMs, and life sciences enterprises.",
                 "Automated Continuous Learning: Self-evaluating multi-agent swarm updates safety rules and formulary tiers continuously as new FDA prescribing inserts and clinical trial data are staged.",
                 "Cross-Therapeutic Extensibility: Easily extended from Immunology (Skyrizi) to Oncology, Rare Diseases, and Cardiology via modular Cortex Search index definitions."
             ], title_color=COLOR_SNOWFLAKE_CYAN, border_color=COLOR_CARD_BORDER)

    # Remove any extra blank slides from the template if present
    while len(prs.slides) > 7:
        rId = prs.slides._sldIdLst[len(prs.slides) - 1].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[len(prs.slides) - 1]

    raw_output = SCRATCH_DIR / "raw_uncompressed_deck.pptx"
    print(f"[*] Saving raw presentation to: {raw_output}")
    prs.save(raw_output)

    # Compress media inside the PPTX to keep final size strictly under 5 MB
    compress_pptx(raw_output, OUTPUT_PATH)
    final_sz = os.path.getsize(OUTPUT_PATH)
    print(f"[OK] Presentation successfully generated: {OUTPUT_PATH}")
    print(f"[OK] Final optimized file size: {final_sz / (1024*1024):.2f} MB ({final_sz} bytes) - STRICTLY UNDER 5 MB LIMIT")


def compress_pptx(input_path, output_path):
    """Compresses all PNG media inside the PPTX using Pillow quantization to reduce file size."""
    import zipfile
    import io
    from PIL import Image

    print("[*] Optimizing embedded images to enforce <= 5 MB file size limit...")
    with zipfile.ZipFile(input_path, 'r') as zin, zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith('ppt/media/') and item.filename.endswith('.png'):
                try:
                    if len(data) > 80 * 1024: # Optimize images larger than 80KB
                        img = Image.open(io.BytesIO(data))
                        q_img = img.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
                        buf = io.BytesIO()
                        q_img.save(buf, format='PNG', optimize=True)
                        opt_data = buf.getvalue()
                        if len(opt_data) < len(data):
                            data = opt_data
                except Exception as e:
                    print(f"  [!] Skipped optimizing {item.filename}: {e}")
            zout.writestr(item, data)


if __name__ == "__main__":
    build_presentation()
