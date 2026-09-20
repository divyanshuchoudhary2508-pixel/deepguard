"""
DeepGuard AI — Startup Pitch PDF Generator
Generates a premium, styled PDF pitch document using ReportLab.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

# ── Color Palette ──────────────────────────────────────────────────────────
DEEP_NAVY     = HexColor("#0D1B2A")
ELECTRIC_BLUE = HexColor("#1A6EFF")
CYAN_ACCENT   = HexColor("#00C6FF")
LIGHT_BG      = HexColor("#F5F8FF")
CARD_BG       = HexColor("#EBF1FF")
DARK_TEXT     = HexColor("#1A1A2E")
MID_TEXT      = HexColor("#4A4A6A")
WHITE         = HexColor("#FFFFFF")
SUCCESS_GREEN = HexColor("#00C48C")
WARNING_RED   = HexColor("#FF4B6E")
GOLD          = HexColor("#FFB800")
BORDER        = HexColor("#C8D8F0")

OUTPUT_PATH = r"C:\Users\sushi\Downloads\DeepGuard_Startup_Pitch.pdf"
W, H = A4  # 595.27 x 841.89 pts


# ── Custom Page Template ────────────────────────────────────────────────────
class PitchCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        self._doc_title = kwargs.pop("doc_title", "DeepGuard AI")
        self._total_pages = 0
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        self._total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page()
            super().showPage()
        super().save()

    def _draw_page(self):
        page_num = self._pageNumber
        # Top header bar
        self.setFillColor(DEEP_NAVY)
        self.rect(0, H - 18*mm, W, 18*mm, fill=1, stroke=0)
        self.setFillColor(ELECTRIC_BLUE)
        self.rect(0, H - 18*mm, 4*mm, 18*mm, fill=1, stroke=0)

        self.setFillColor(WHITE)
        self.setFont("Helvetica-Bold", 9)
        self.drawString(10*mm, H - 12*mm, "🛡  DeepGuard AI")
        self.setFont("Helvetica", 7.5)
        self.setFillColor(CYAN_ACCENT)
        self.drawString(45*mm, H - 12*mm, "Startup Pitch Document — Confidential")

        # Page number top-right
        self.setFillColor(HexColor("#AABBDD"))
        self.setFont("Helvetica", 7.5)
        self.drawRightString(W - 10*mm, H - 12*mm, f"Page {page_num} / {self._total_pages}")

        # Bottom footer bar
        self.setFillColor(DEEP_NAVY)
        self.rect(0, 0, W, 12*mm, fill=1, stroke=0)
        self.setFillColor(HexColor("#8899BB"))
        self.setFont("Helvetica", 7)
        self.drawString(10*mm, 4.5*mm, "© 2026 DeepGuard AI — Confidential & Proprietary — Not for Distribution")
        self.setFillColor(CYAN_ACCENT)
        self.drawRightString(W - 10*mm, 4.5*mm, "deepguard.ai")


# ── Style Definitions ───────────────────────────────────────────────────────
def get_styles():
    base = getSampleStyleSheet()

    styles = {
        "cover_title": ParagraphStyle("cover_title",
            fontName="Helvetica-Bold", fontSize=38, textColor=WHITE,
            leading=46, alignment=TA_LEFT),

        "cover_tagline": ParagraphStyle("cover_tagline",
            fontName="Helvetica-Oblique", fontSize=14, textColor=CYAN_ACCENT,
            leading=20, alignment=TA_LEFT),

        "cover_meta": ParagraphStyle("cover_meta",
            fontName="Helvetica", fontSize=10, textColor=HexColor("#AABBDD"),
            leading=16, alignment=TA_LEFT),

        "section_header": ParagraphStyle("section_header",
            fontName="Helvetica-Bold", fontSize=16, textColor=DEEP_NAVY,
            leading=22, spaceBefore=14, spaceAfter=4,
            borderPadding=(0, 0, 4, 0)),

        "subsection_header": ParagraphStyle("subsection_header",
            fontName="Helvetica-Bold", fontSize=11.5, textColor=ELECTRIC_BLUE,
            leading=16, spaceBefore=10, spaceAfter=3),

        "body": ParagraphStyle("body",
            fontName="Helvetica", fontSize=9.5, textColor=DARK_TEXT,
            leading=15, alignment=TA_JUSTIFY, spaceAfter=5),

        "body_bold": ParagraphStyle("body_bold",
            fontName="Helvetica-Bold", fontSize=9.5, textColor=DARK_TEXT,
            leading=15, spaceAfter=5),

        "bullet": ParagraphStyle("bullet",
            fontName="Helvetica", fontSize=9.5, textColor=DARK_TEXT,
            leading=15, leftIndent=14, bulletIndent=4, spaceAfter=3),

        "caption": ParagraphStyle("caption",
            fontName="Helvetica-Oblique", fontSize=8, textColor=MID_TEXT,
            leading=11, alignment=TA_CENTER),

        "highlight": ParagraphStyle("highlight",
            fontName="Helvetica-Bold", fontSize=11, textColor=ELECTRIC_BLUE,
            leading=17, alignment=TA_CENTER, spaceBefore=6, spaceAfter=6),

        "table_header": ParagraphStyle("table_header",
            fontName="Helvetica-Bold", fontSize=8.5, textColor=WHITE,
            leading=12, alignment=TA_CENTER),

        "table_cell": ParagraphStyle("table_cell",
            fontName="Helvetica", fontSize=8.5, textColor=DARK_TEXT,
            leading=12, alignment=TA_LEFT),

        "table_cell_center": ParagraphStyle("table_cell_center",
            fontName="Helvetica", fontSize=8.5, textColor=DARK_TEXT,
            leading=12, alignment=TA_CENTER),

        "callout": ParagraphStyle("callout",
            fontName="Helvetica-Bold", fontSize=10, textColor=DEEP_NAVY,
            leading=15, leftIndent=12, rightIndent=12,
            spaceBefore=8, spaceAfter=8),

        "toc_item": ParagraphStyle("toc_item",
            fontName="Helvetica", fontSize=10, textColor=DARK_TEXT,
            leading=17, leftIndent=8),
    }
    return styles


# ── Helpers ─────────────────────────────────────────────────────────────────
def section_divider(styles, number, title):
    """Blue-accented section header with number badge."""
    data = [[
        Paragraph(f"<font color='#{ELECTRIC_BLUE.hexval()[2:]}'>{'0'+str(number) if number < 10 else str(number)}</font>",
                  ParagraphStyle("num", fontName="Helvetica-Bold", fontSize=22,
                                 textColor=ELECTRIC_BLUE, leading=26, alignment=TA_CENTER)),
        Paragraph(title, styles["section_header"])
    ]]
    t = Table(data, colWidths=[18*mm, None])
    t.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (0, 0), 0),
        ("RIGHTPADDING",  (0, 0), (0, 0), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
    ]))
    return [t, HRFlowable(width="100%", thickness=1.5, color=ELECTRIC_BLUE, spaceAfter=8)]


def callout_box(text, styles, bg=CARD_BG, border=ELECTRIC_BLUE):
    """Styled callout/info box."""
    data = [[Paragraph(text, styles["callout"])]]
    t = Table(data, colWidths=[W - 40*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("LINEAFTER",     (0, 0), (0, -1), 3, border),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t


def styled_table(headers, rows, styles, col_widths=None, col_colors=None):
    """Styled data table with alternating rows."""
    header_row = [Paragraph(h, styles["table_header"]) for h in headers]
    data = [header_row]
    for row in rows:
        data.append([Paragraph(str(c), styles["table_cell"]) for c in row])

    t = Table(data, colWidths=col_widths, repeatRows=1)
    ts = [
        ("BACKGROUND",    (0, 0), (-1, 0), DEEP_NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8.5),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, CARD_BG]),
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    t.setStyle(TableStyle(ts))
    return t


def metric_cards(metrics, styles):
    """3-column metric highlight cards."""
    cells = []
    for label, value, sub in metrics:
        card_data = [[
            Paragraph(f"<font size='20'><b>{value}</b></font>", ParagraphStyle(
                "mv", fontName="Helvetica-Bold", fontSize=20, textColor=ELECTRIC_BLUE,
                leading=24, alignment=TA_CENTER)),
        ], [
            Paragraph(f"<b>{label}</b>", ParagraphStyle(
                "ml", fontName="Helvetica-Bold", fontSize=8.5, textColor=DARK_TEXT,
                leading=12, alignment=TA_CENTER)),
        ], [
            Paragraph(sub, ParagraphStyle(
                "ms", fontName="Helvetica", fontSize=7.5, textColor=MID_TEXT,
                leading=10, alignment=TA_CENTER)),
        ]]
        card = Table(card_data, colWidths=[(W - 50*mm) / 3])
        card.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), CARD_BG),
            ("BOX",           (0, 0), (-1, -1), 1, BORDER),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        cells.append(card)

    wrapper = Table([cells], colWidths=[(W - 50*mm) / 3] * len(metrics),
                    hAlign="LEFT")
    wrapper.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return wrapper


# ── Cover Page ──────────────────────────────────────────────────────────────
def build_cover(c, styles):
    """Draws full-bleed dark cover page directly on canvas."""
    c.setFillColor(DEEP_NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Decorative geometric shapes
    c.setFillColor(ELECTRIC_BLUE)
    c.setFillAlpha(0.12)
    c.circle(W - 20*mm, H - 30*mm, 80*mm, fill=1, stroke=0)
    c.setFillAlpha(0.07)
    c.circle(W - 10*mm, H*0.3, 55*mm, fill=1, stroke=0)
    c.setFillAlpha(1.0)

    # Left accent stripe
    c.setFillColor(ELECTRIC_BLUE)
    c.rect(0, 0, 5*mm, H, fill=1, stroke=0)

    # Logo badge
    c.setFillColor(ELECTRIC_BLUE)
    c.roundRect(18*mm, H - 45*mm, 30*mm, 14*mm, 4, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(21*mm, H - 40.5*mm, "\u26e8  DeepGuard")

    # Main title
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 42)
    c.drawString(18*mm, H - 85*mm, "DeepGuard AI")
    c.setFillColor(CYAN_ACCENT)
    c.setFont("Helvetica-Bold", 17)
    c.drawString(18*mm, H - 100*mm, "Startup Pitch Document")

    # Tagline
    c.setFillColor(HexColor("#AABBDD"))
    c.setFont("Helvetica-Oblique", 12.5)
    c.drawString(18*mm, H - 116*mm, '"See Through the Fake. Protect What\'s Real."')

    # Horizontal rule
    c.setStrokeColor(ELECTRIC_BLUE)
    c.setLineWidth(1.5)
    c.line(18*mm, H - 124*mm, W - 18*mm, H - 124*mm)

    # Meta info block
    meta = [
        ("Sector",   "AI Security  |  Digital Forensics  |  Trust & Safety"),
        ("Stage",    "Pre-Seed"),
        ("Ask",      "\u20b91.5 Crore  (\u2248 $180,000 USD)"),
        ("Date",     "September 2026"),
        ("Version",  "1.0  —  Confidential"),
    ]
    y = H - 138*mm
    for label, value in meta:
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(CYAN_ACCENT)
        c.drawString(18*mm, y, label.upper() + ":")
        c.setFont("Helvetica", 9.5)
        c.setFillColor(WHITE)
        c.drawString(48*mm, y, value)
        y -= 9*mm

    # Bottom confidence strip
    c.setFillColor(ELECTRIC_BLUE)
    c.rect(0, 22*mm, W, 12*mm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(W / 2, 27*mm,
        "Built on IEEE TENCON 2024 Research  \u2022  "
        "Multi-Signal Forensic AI  \u2022  Enterprise-Grade  \u2022  Court-Admissible")

    # Footer
    c.setFillColor(HexColor("#556688"))
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(W / 2, 10*mm,
        "Confidential — For Accredited Investors Only — Not for Public Distribution")

    c.showPage()


# ── Document Body ────────────────────────────────────────────────────────────
def build_body(doc, styles):
    story = []
    sp = lambda n=6: Spacer(1, n)

    # ── TOC ──
    story += section_divider(styles, 0, "Table of Contents")
    toc_items = [
        ("01", "Executive Summary"),
        ("02", "The Problem"),
        ("03", "The Solution: DeepGuard"),
        ("04", "Technology & Architecture"),
        ("05", "Product Features"),
        ("06", "Market Opportunity"),
        ("07", "Competitive Landscape"),
        ("08", "Business Model & Revenue Streams"),
        ("09", "Go-To-Market Strategy"),
        ("10", "Traction & Validation"),
        ("11", "Team"),
        ("12", "Financial Projections"),
        ("13", "The Ask"),
        ("14", "Appendix: Research Foundation"),
    ]
    for num, title in toc_items:
        story.append(Paragraph(
            f"<font color='#1A6EFF'><b>{num}</b></font>  &nbsp; {title}",
            styles["toc_item"]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 01 EXECUTIVE SUMMARY
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 1, "Executive Summary")

    story += [
        Paragraph("<b>Company:</b> DeepGuard AI &nbsp;&nbsp; <b>Tagline:</b> <i>\"See Through the Fake. Protect What's Real.\"</i>", styles["body"]),
        Paragraph("<b>Stage:</b> Pre-Seed / Seed &nbsp;&nbsp; <b>Sector:</b> AI Security, Digital Forensics, Trust & Safety", styles["body"]),
        sp(8),
    ]

    story.append(callout_box(
        "DeepGuard is the world's first multi-signal, explainable deepfake forensics platform — "
        "combining the accuracy of deep neural networks with the interpretability of physical forensic science. "
        "Every analysis session produces a court-admissible Forensic Verification Report with SHA-256 cryptographic proof.",
        styles
    ))
    story.append(sp(10))

    story.append(metric_cards([
        ("Global KYC Fraud (2025)", "$4.6B", "Caused by synthetic AI faces"),
        ("Total Addressable Market", "$24.4B", "Across 4 target verticals"),
        ("Pre-Seed Ask", "₹1.5 Cr", "18 months runway"),
    ], styles))
    story.append(sp(10))

    story.append(Paragraph(
        "DeepGuard is built on peer-reviewed IEEE TENCON 2024 research and goes far beyond black-box detection: "
        "it delivers <b>multi-signal forensic evidence, neural attention heatmaps (Grad-CAM++), 68-point facial geometry analysis, "
        "2D Fourier spectral fingerprinting, EXIF metadata intelligence,</b> and an <b>active learning human override engine</b> — "
        "all through a seamless enterprise REST API and glassmorphism web dashboard.",
        styles["body"]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 02 THE PROBLEM
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 2, "The Problem")

    story.append(Paragraph("2.1  The Synthetic Media Crisis", styles["subsection_header"]))
    bullets_crisis = [
        "Deepfake pornography has destroyed careers of public figures and private individuals worldwide.",
        "Synthetic KYC fraud using AI-generated faces cost global banks over <b>$4.6 billion</b> in 2025 (Deloitte, 2025).",
        "Political disinformation campaigns with synthetic face-swapped videos influenced elections in 3+ countries.",
        "Insurance fraud using AI-manipulated photographic evidence is rising at <b>34% year-over-year</b>.",
        "Morphed photo attacks are being used to bypass border control and biometric identity systems globally.",
    ]
    for b in bullets_crisis:
        story.append(Paragraph(f"<bullet>\u2022</bullet>{b}", styles["bullet"]))
    story.append(sp(8))

    story.append(Paragraph("2.2  The Critical Detection Failures", styles["subsection_header"]))
    problem_rows = [
        ["Black-Box Verdicts", "Tools say FAKE/REAL with no explanation", "Courts cannot use unexaminable AI verdicts"],
        ["No Physical Forensics", "Pure neural networks miss physical artefacts", "High false positive rates destroy user trust"],
        ["No Audit Trail", "No cryptographic proof of analysis session", "Legally inadmissible without chain-of-custody"],
        ["No Human-in-the-Loop", "Models cannot learn from expert corrections", "Drift and hallucinations accumulate over time"],
    ]
    story.append(styled_table(
        ["Critical Failure Mode", "Root Cause", "Industry Impact"],
        problem_rows, styles,
        col_widths=[52*mm, 65*mm, 58*mm]
    ))
    story.append(sp(10))

    story.append(callout_box(
        "⚠  95% of existing deepfake detection tools produce NO explainable forensic evidence. "
        "They are black-box classifiers. They cannot be used in a court of law, "
        "by law enforcement, or by compliance departments.",
        styles, bg=HexColor("#FFF0F3"), border=WARNING_RED
    ))
    story.append(sp(10))

    story.append(Paragraph("2.3  The Escalating Scale", styles["subsection_header"]))
    scale_rows = [
        ["2022", "14,000", "Niche threat"],
        ["2023", "96,000", "Growing threat"],
        ["2024", "1,200,000", "Mainstream threat"],
        ["2026 (Est.)", "12,000,000 / day", "Industrial-scale crisis"],
    ]
    story.append(styled_table(
        ["Year", "Deepfake Assets Published", "Threat Classification"],
        scale_rows, styles,
        col_widths=[40*mm, 65*mm, 65*mm]
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 03 THE SOLUTION
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 3, "The Solution: DeepGuard")

    story.append(callout_box(
        "DeepGuard does not just detect deepfakes — it PROVES them.\n"
        "Every analysis session produces legally auditable forensic evidence, not just a binary verdict.",
        styles
    ))
    story.append(sp(10))

    story.append(Paragraph("Every DeepGuard scan delivers:", styles["body_bold"]))
    deliverables = [
        ("Neural Probability Score", "Calibrated DenseNet121 confidence from 0–100%"),
        ("Grad-CAM++ Heatmap", "Visual neural attention map highlighting suspicious facial regions"),
        ("68-Point Facial Geometry Mesh", "Anatomical impossibility detection — jaw warp, eye asymmetry"),
        ("2D Fourier Spectral Fingerprint", "Invisible GAN/Diffusion model signature in frequency domain"),
        ("EXIF & C2PA Metadata Audit", "Exposes AI generation software, missing metadata, GPS anomalies"),
        ("SHA-256 Cryptographic Hash", "Binds the analysed file to its forensic report permanently"),
        ("Forensic PDF Verification Report", "Court-admissible, timestamped, digitally signed evidence document"),
    ]
    for icon_label, desc in deliverables:
        story.append(Paragraph(
            f"<bullet>\u2713</bullet><b>{icon_label}</b>  —  {desc}",
            styles["bullet"]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 04 TECHNOLOGY & ARCHITECTURE
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 4, "Technology & Architecture")

    story.append(Paragraph("4.1  Multi-Signal Ensemble Engine", styles["subsection_header"]))
    signal_rows = [
        ["Signal 1", "DenseNet121 Neural Feature Map", "6.96M params, transfer-learned, 40k+ images trained", "High"],
        ["Signal 2", "2D Fourier FFT Spectral Analysis", "High-freq power ratio < 0.72 = GAN signature", "High"],
        ["Signal 3", "Head-Body Laplacian Seam Analysis", "Detects face-swap splicing boundary artefacts", "Medium"],
        ["Signal 4", "EXIF & C2PA Metadata Inspector", "Strips AI tool signatures, missing GPS/camera data", "Medium"],
        ["Signal 5", "68-Point Facial Geometry Mesh", "Eye symmetry score, jawline warp index", "Medium"],
        ["Signal 6", "Active Learning Override Engine", "SHA-256 DB locks expert corrections permanently", "Critical"],
    ]
    story.append(styled_table(
        ["#", "Signal Layer", "Detection Mechanism", "Weight"],
        signal_rows, styles,
        col_widths=[12*mm, 48*mm, 82*mm, 20*mm]
    ))
    story.append(sp(10))

    story.append(Paragraph("4.2  Neural Architecture Specifications", styles["subsection_header"]))
    arch_rows = [
        ["Backbone Model", "DenseNet121 (ImageNet pretrained)"],
        ["Input Resolution", "224 × 224 × 3 pixels"],
        ["Classification Head", "GAP → BatchNorm → Dropout(0.4) → Dense(256, ReLU) → Dense(1, Sigmoid)"],
        ["Loss Function", "Binary Cross-Entropy"],
        ["Phase 1 Optimizer", "Adam  |  lr = 1×10⁻³  |  Frozen backbone"],
        ["Phase 2 Optimizer", "Adam  |  lr = 1×10⁻⁵  |  Top 30 layers unfrozen"],
        ["Training Dataset", "40,000+ balanced real/fake face images (CelebA + Deepfake Faces)"],
        ["Training Hardware", "2× NVIDIA Tesla T4 GPUs with MirroredStrategy (Kaggle)"],
        ["Precision", "Mixed FP16  (Tensor Core accelerated)"],
        ["Explainability Method", "Sharpened Grad-CAM++ on last DenseNet convolutional block"],
    ]
    story.append(styled_table(
        ["Parameter", "Specification"],
        arch_rows, styles,
        col_widths=[60*mm, 105*mm]
    ))
    story.append(sp(8))

    story.append(Paragraph("4.3  Technology Stack", styles["subsection_header"]))
    stack_rows = [
        ["Backend", "Python 3.12, Flask, TensorFlow 2.20, OpenCV"],
        ["AI / ML", "DenseNet121, MediaPipe, Grad-CAM++, NumPy, SciPy"],
        ["Forensics", "piexif (EXIF parsing), ReportLab (PDF), hashlib SHA-256"],
        ["Frontend", "Vanilla JS, CSS3 Glassmorphism, Lucide Icons"],
        ["Infrastructure", "Flask REST API — GPU Cloud compatible (Kaggle / GCP / AWS)"],
        ["Security", "SHA-256 cryptographic hashing, JSON feedback persistence store"],
    ]
    story.append(styled_table(
        ["Layer", "Technologies"],
        stack_rows, styles,
        col_widths=[40*mm, 125*mm]
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 05 PRODUCT FEATURES
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 5, "Product Features")

    story.append(Paragraph("5.1  DeepGuard Web Dashboard", styles["subsection_header"]))
    features = [
        "Single image upload (drag-and-drop) — supports JPG, PNG, WEBP",
        "Full multi-signal forensic scan completing in under 10 seconds",
        "Grad-CAM++ neural attention heatmap with 3-way view toggle (Original | Heatmap | Facial Mesh)",
        "Calibrated confidence gauge with animated verdict banner (DEEPFAKE / AUTHENTIC)",
        "EXIF metadata card: camera make/model, software, GPS, color space, creation timestamp",
        "68-Point Facial Geometry card: eye symmetry score, jawline warp index, landmark count",
        "SHA-256 hash of analysed file displayed in UI and embedded in PDF report",
        "Downloadable Forensic PDF Verification Report (court-style, timestamped)",
        "Human feedback buttons (Agree / Disagree + Override) with active learning persistence",
        "Pre-loaded sample image library for quick demonstration",
    ]
    for f in features:
        story.append(Paragraph(f"<bullet>\u2022</bullet>{f}", styles["bullet"]))
    story.append(sp(8))

    story.append(Paragraph("5.2  REST API Endpoints (B2B Integration Ready)", styles["subsection_header"]))
    api_rows = [
        ["POST", "/api/predict", "Full forensic analysis of uploaded image. Returns JSON with all signal scores."],
        ["GET",  "/api/health", "System health check, model name, and loaded status."],
        ["GET",  "/api/samples", "List of available pre-loaded sample images."],
        ["POST", "/api/feedback", "Submit human expert correction for active learning update."],
        ["GET",  "/api/download-report/<filename>", "Download generated forensic PDF report by filename."],
    ]
    story.append(styled_table(
        ["Method", "Endpoint", "Description"],
        api_rows, styles,
        col_widths=[18*mm, 65*mm, 82*mm]
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 06 MARKET OPPORTUNITY
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 6, "Market Opportunity")

    story.append(Paragraph("6.1  Total Addressable Market (TAM)", styles["subsection_header"]))
    tam_rows = [
        ["AI Content Authentication & Trust", "$4.1 Billion", "31.4% CAGR"],
        ["Digital Forensics Software", "$6.9 Billion", "13.2% CAGR"],
        ["Biometric & Identity Verification", "$9.8 Billion", "19.7% CAGR"],
        ["KYC / AML Compliance Technology", "$3.6 Billion", "22.1% CAGR"],
        ["Total Addressable Market", "$24.4 Billion", "—"],
    ]
    t = styled_table(
        ["Market Segment", "Market Size (2026)", "Projected CAGR"],
        tam_rows, styles,
        col_widths=[90*mm, 50*mm, 25*mm]
    )
    story.append(t)
    story.append(sp(8))

    story.append(metric_cards([
        ("TAM", "$24.4B", "Total Addressable Market"),
        ("SAM", "$3.2B", "Serviceable Addressable Market"),
        ("SOM (Yr 3)", "$48M", "Obtainable Market Target"),
    ], styles))
    story.append(sp(10))

    story.append(Paragraph("6.2  Regulatory Pull Factors", styles["subsection_header"]))
    reg_items = [
        "🏛  <b>EU AI Act (2025)</b>: Mandates disclosure of AI-generated content — creates global compliance demand.",
        "🏛  <b>India DPDP Act (2023–26)</b>: Digital personal data protection enforcement creating KYC compliance need.",
        "🏛  <b>US DEFIANCE Act (2024)</b>: Makes non-consensual deepfake images a federal offense — creates legal evidence demand.",
        "📈  <b>AI Tool Proliferation</b>: Midjourney, Sora, Stable Diffusion making synthetic faces trivially generatable.",
    ]
    for r in reg_items:
        story.append(Paragraph(r, styles["bullet"]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 07 COMPETITIVE LANDSCAPE
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 7, "Competitive Landscape")

    story.append(Paragraph("7.1  Competitive Matrix", styles["subsection_header"]))
    comp_rows = [
        ["Sensity AI",               "✓", "✗", "✗", "✓", "✗", "✗", "✗"],
        ["Microsoft Video Auth.",    "✓", "✗", "✗", "✗", "✗", "✗", "✗"],
        ["Hive Moderation",          "✓", "✗", "✗", "✓", "✗", "✗", "✗"],
        ["Reality Defender",         "✓", "~", "✗", "✓", "✗", "~", "✗"],
        ["FotoForensics",            "✓", "~", "✗", "✗", "✗", "✗", "✗"],
        ["🛡 DeepGuard (Us)",        "✓", "✓", "✓", "✓", "✓", "✓", "✓"],
    ]
    t = styled_table(
        ["Competitor", "Detection", "Explainability", "Forensic PDF", "API", "Human Loop", "Multi-Signal", "India Focus"],
        comp_rows, styles,
        col_widths=[42*mm, 20*mm, 26*mm, 23*mm, 14*mm, 20*mm, 22*mm, 18*mm]
    )
    story.append(t)
    story.append(sp(10))

    story.append(Paragraph("7.2  DeepGuard's Unfair Advantages", styles["subsection_header"]))
    advantages = [
        ("<b>Explainability-First:</b>", "Only platform producing court-admissible forensic PDF reports with cryptographic audit trails."),
        ("<b>Multi-Signal Convergence:</b>", "5 independent physical and neural forensic signals — not just one neural network."),
        ("<b>Active Learning Moat:</b>", "System gets smarter with every human correction — a competitive moat that deepens over time."),
        ("<b>Research-Backed Credibility:</b>", "Built on IEEE TENCON 2024 peer-reviewed methodology — critical for enterprise procurement."),
        ("<b>India-First Design:</b>", "Pricing, compliance alignment, and support designed for India — a 1.4B person opportunity ignored by competitors."),
    ]
    for title, desc in advantages:
        story.append(Paragraph(f"<bullet>\u2192</bullet>{title} {desc}", styles["bullet"]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 08 BUSINESS MODEL
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 8, "Business Model & Revenue Streams")

    story.append(Paragraph("8.1  SaaS Tiered Subscription Model", styles["subsection_header"]))
    pricing_rows = [
        ["Starter",      "Freelancers, Journalists",  "₹999 / month",    "500 scans",    "Web dashboard, basic PDF report"],
        ["Professional", "SMEs, Agencies",            "₹4,999 / month",  "5,000 scans",  "REST API, advanced forensics, EXIF audit"],
        ["Enterprise",   "Banks, Corporates",         "₹24,999 / month", "Unlimited",    "On-premise, SLA, custom branding, support"],
        ["Government",   "Law Enforcement, Courts",   "Custom",          "Custom",       "Air-gapped deployment, legal certification"],
    ]
    story.append(styled_table(
        ["Plan", "Target Customer", "Price", "API Calls", "Key Features"],
        pricing_rows, styles,
        col_widths=[25*mm, 40*mm, 30*mm, 22*mm, 48*mm]
    ))
    story.append(sp(10))

    story.append(Paragraph("8.2  Unit Economics (Year 2 Projections)", styles["subsection_header"]))
    story.append(metric_cards([
        ("LTV : CAC Ratio", "10.3x", "₹1,86,000 LTV / ₹18,000 CAC"),
        ("Gross Margin", "78%", "SaaS software margin"),
        ("Target Churn", "< 3%/mo", "Monthly customer churn rate"),
    ], styles))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 09 GO-TO-MARKET
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 9, "Go-To-Market Strategy")

    gtm_phases = [
        ("Phase 1  —  Foundation (Months 1–6): Credibility & Early Adopters", [
            "Submit DeepGuard's multi-signal methodology as IEEE/ACM extension paper.",
            "Open source forensic signal layer on GitHub to drive developer inbound interest.",
            "Partner with BOOM, AltNews, AFP Fact-Check India — free Professional plans for case studies.",
            "Deploy at Smart India Hackathon 2026, IIT Bombay Techfest for user/talent recruitment.",
            "Free tier deployments at Marwadi University, IIT Gandhinagar, BITS Pilani.",
        ]),
        ("Phase 2  —  Revenue (Months 6–18): B2B Enterprise Sales", [
            "BFSI Vertical: Direct sales to compliance teams at HDFC, ICICI, Axis Bank for KYC fraud prevention.",
            "Government Contracts: Approach MeiTY and state Cyber Crime Cells for procurement.",
            "Insurance Vertical: Partner with IRDAI-regulated insurers for photographic claims verification.",
            "API Ecosystem: List on AWS Marketplace India, integrate with IDfy, DigiLocker, AuthBridge.",
        ]),
        ("Phase 3  —  Scale (Months 18–36): Geographic Expansion", [
            "Southeast Asia: Singapore, Malaysia, Indonesia — high digital fraud incidence.",
            "MENA Region: UAE, Saudi Arabia — government digital transformation programs.",
            "US/EU Enterprise: Media companies, legal tech firms, content platforms (Shutterstock, Adobe, Reuters).",
        ]),
    ]
    for phase_title, phase_bullets in gtm_phases:
        story.append(Paragraph(phase_title, styles["subsection_header"]))
        for b in phase_bullets:
            story.append(Paragraph(f"<bullet>\u2022</bullet>{b}", styles["bullet"]))
        story.append(sp(6))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 10 TRACTION & VALIDATION
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 10, "Traction & Validation")

    story.append(Paragraph("10.1  Technical Milestones Completed", styles["subsection_header"]))
    milestones = [
        ["Core DenseNet121 neural detection engine", "✓ Complete"],
        ["Grad-CAM++ neural attention heatmap generation", "✓ Complete"],
        ["68-point MediaPipe facial geometry mesh overlay", "✓ Complete"],
        ["EXIF / C2PA metadata inspector module", "✓ Complete"],
        ["2D Fourier FFT spectral frequency analyser", "✓ Complete"],
        ["Head-body Laplacian seam variance detection", "✓ Complete"],
        ["SHA-256 Active Learning human feedback engine", "✓ Complete"],
        ["ReportLab Forensic PDF report generator", "✓ Complete"],
        ["Flask REST API (5 endpoints)", "✓ Complete"],
        ["2× Tesla T4 GPU Kaggle MirroredStrategy training pipeline", "✓ Complete"],
        ["DenseNet121 model trained on 40,000+ images", "✓ Complete"],
        ["Full-stack web dashboard (glassmorphism UI)", "✓ Complete"],
    ]
    t = styled_table(
        ["Milestone", "Status"],
        milestones, styles,
        col_widths=[140*mm, 25*mm]
    )
    story.append(t)
    story.append(sp(10))

    story.append(Paragraph("10.2  Pilot Roadmap", styles["subsection_header"]))
    pilots = [
        ["Month 1–2", "3 journalism organizations", "BOOM, AltNews, The Wire", "Free pilot → case study"],
        ["Month 3–4", "1 private bank KYC team", "HDFC or Kotak", "Paid PoC — ₹2L"],
        ["Month 5–6", "1 state cyber crime cell", "Gujarat Cyber Crime Cell", "Government MoU"],
    ]
    story.append(styled_table(
        ["Timeline", "Target", "Example Org", "Type"],
        pilots, styles,
        col_widths=[22*mm, 50*mm, 50*mm, 43*mm]
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 11 TEAM
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 11, "Team")

    story.append(callout_box(
        "Founder & CTO: Divyanshu Choudhary\n\n"
        "Architect of the DeepGuard full-stack platform (backend, frontend, ML pipeline, forensic systems). "
        "Implemented IEEE TENCON 2024 research into a production-grade explainable AI system. "
        "Deep expertise in TensorFlow, Flask, MediaPipe, computer vision, and digital forensics. "
        "Trained multi-GPU deep learning models on cloud infrastructure (Kaggle 2× T4, GCP).\n\n"
        "Kaggle: divyanshuchoudhary25",
        styles
    ))
    story.append(sp(10))

    story.append(Paragraph("Advisors Sought", styles["subsection_header"]))
    advisor_rows = [
        ["Academic Advisor", "Faculty from IEEE TENCON 2024 team (Marwadi University)", "Research credibility & publication pipeline"],
        ["Legal Advisor", "Digital forensics / cyber law specialist", "Legal admissibility & IP filing strategy"],
        ["Enterprise Sales Advisor", "Former BFSI compliance technology sales executive", "Enterprise procurement network access"],
    ]
    story.append(styled_table(
        ["Role", "Profile", "Value Add"],
        advisor_rows, styles,
        col_widths=[40*mm, 72*mm, 53*mm]
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 12 FINANCIAL PROJECTIONS
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 12, "Financial Projections")

    story.append(Paragraph("12.1  5-Year Revenue Projections", styles["subsection_header"]))
    rev_rows = [
        ["Year 1", "₹18 Lakh",    "12",    "3",   "-120%  (Investment Phase)"],
        ["Year 2", "₹1.2 Crore",  "65",    "8",   "-25%"],
        ["Year 3", "₹6.5 Crore",  "280",   "22",  "+18%"],
        ["Year 4", "₹24 Crore",   "900",   "55",  "+32%"],
        ["Year 5", "₹80 Crore",   "2,800", "130", "+41%"],
    ]
    story.append(styled_table(
        ["Year", "ARR", "Customers", "Headcount", "EBITDA Margin"],
        rev_rows, styles,
        col_widths=[20*mm, 32*mm, 30*mm, 28*mm, 55*mm]
    ))
    story.append(sp(10))

    story.append(Paragraph("12.2  Use of Funds — ₹1.5 Crore Pre-Seed", styles["subsection_header"]))
    uof_rows = [
        ["Product & Engineering", "₹60 Lakh", "40%", "2 senior engineers for 12 months"],
        ["Cloud Infrastructure", "₹22 Lakh", "15%", "GPU training, API hosting, CDN"],
        ["Enterprise Sales & BD", "₹30 Lakh", "20%", "1 BD hire, events, direct outreach"],
        ["Legal & Compliance", "₹12 Lakh", "8%", "IP filing, data licensing agreements"],
        ["Marketing & Community", "₹11 Lakh", "7%", "Developer evangelism, content, SEO"],
        ["Working Capital", "₹15 Lakh", "10%", "18-month runway buffer"],
    ]
    story.append(styled_table(
        ["Allocation", "Amount", "%", "Details"],
        uof_rows, styles,
        col_widths=[50*mm, 30*mm, 15*mm, 70*mm]
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 13 THE ASK
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 13, "The Ask")

    story.append(callout_box(
        "Pre-Seed Round:  ₹1.5 Crore  (≈ $180,000 USD)\n\n"
        "Instrument: SAFE (Simple Agreement for Future Equity) or Convertible Note\n"
        "Valuation Cap: ₹8 Crore     |     Discount Rate: 20% on Series A\n"
        "Use Period: 18 Months",
        styles
    ))
    story.append(sp(10))

    story.append(Paragraph("Beyond Capital — What We Are Looking For", styles["subsection_header"]))
    asks = [
        "Access to BFSI / Government procurement networks in India.",
        "Legal tech / forensics domain expertise from advisor or partner.",
        "Cloud infrastructure credits (AWS, GCP, or Azure for India).",
        "Introduction to Tier 1 VC ecosystem for Series A (Elevation, Peak XV, Accel India).",
    ]
    for a in asks:
        story.append(Paragraph(f"<bullet>\u2022</bullet>{a}", styles["bullet"]))
    story.append(sp(10))

    story.append(Paragraph("Why Now?", styles["subsection_header"]))
    story.append(Paragraph(
        "Three irreversible forces are converging simultaneously:", styles["body"]))
    reasons = [
        ("<b>Supply:</b>", "AI generative models (Sora, Flux, Stable Diffusion 3) have made creating photorealistic fake faces trivially easy and free."),
        ("<b>Regulatory Demand:</b>", "EU AI Act, India DPDP Act, US DEFIANCE Act are creating compliance mandates that organizations must address NOW."),
        ("<b>Research Timing:</b>", "Our IEEE TENCON 2024 foundation gives us 12–18 months of scientific credibility ahead of the next wave of startups."),
    ]
    for title, desc in reasons:
        story.append(Paragraph(f"<bullet>\u2192</bullet>{title} {desc}", styles["bullet"]))
    story.append(sp(10))

    story.append(callout_box(
        "The window to establish category leadership in AI-powered deepfake forensics in India "
        "is open RIGHT NOW. It will not stay open.",
        styles, bg=HexColor("#EBF5FF"), border=ELECTRIC_BLUE
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 14 APPENDIX
    # ═══════════════════════════════════════════════════════════
    story += section_divider(styles, 14, "Appendix: Research Foundation")

    story.append(Paragraph("IEEE TENCON 2024 Citation", styles["subsection_header"]))
    story.append(callout_box(
        'Sunil, R., Mer, P., Diwan, A., & Parmar, P. (2024). "Deepfake Detection in Digital Images using '
        'Data Augmentation and Layer Unfreezing across Various Deep Learning Models." '
        'IEEE TENCON 2024 — IEEE Region 10 Conference. Marwadi University, Rajkot, India.',
        styles, bg=CARD_BG
    ))
    story.append(sp(10))

    story.append(Paragraph("Paper-to-Product Alignment", styles["subsection_header"]))
    align_rows = [
        ["DenseNet121 achieves highest accuracy across 5 tested architectures", "DenseNet121 selected as primary backbone"],
        ["2-phase layer unfreezing improves fine-tuning by 11.2%", "Phase 1 (frozen) + Phase 2 (unfreeze top 30 layers)"],
        ["Data augmentation reduces overfitting on limited datasets", "RandomFlip, RandomRotation, RandomZoom in Keras graph"],
        ["Grad-CAM visualization improves expert trust in model decisions", "Sharpened Grad-CAM++ overlaid on original image"],
    ]
    story.append(styled_table(
        ["Paper Finding", "DeepGuard Implementation"],
        align_rows, styles,
        col_widths=[85*mm, 80*mm]
    ))
    story.append(sp(10))

    story.append(Paragraph("DeepGuard Extensions Beyond the Paper", styles["subsection_header"]))
    extensions = [
        "Multi-Signal Physical Forensics (FFT, Laplacian seam, facial geometry, EXIF/C2PA)",
        "SHA-256 Cryptographic Evidence Chain for legal chain-of-custody",
        "Active Learning Human Override System with permanent fingerprint database",
        "Enterprise ReportLab PDF Forensic Report Generation",
        "REST API with 5 documented endpoints for B2B integration",
        "GPU-Distributed Training Pipeline (2× T4 MirroredStrategy, mixed precision)",
        "Full-stack production web application (Flask backend + glassmorphism frontend)",
    ]
    for ext in extensions:
        story.append(Paragraph(f"<bullet>\u2022</bullet>{ext}", styles["bullet"]))

    return story


# ── Main PDF Builder ─────────────────────────────────────────────────────────
def build_pdf():
    import io, tempfile
    print(f"Building DeepGuard Startup Pitch PDF -> {OUTPUT_PATH}")
    styles = get_styles()

    # ── Step 1: Render cover page to a temp file ──
    cover_tmp = OUTPUT_PATH + ".cover_tmp.pdf"
    cover_c = PitchCanvas(cover_tmp, pagesize=A4, doc_title="DeepGuard AI")
    build_cover(cover_c, styles)
    cover_c.save()   # flushes to cover_tmp

    # ── Step 2: Render body pages to a BytesIO buffer ──
    from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

    body_buf = io.BytesIO()

    class BodyDoc(BaseDocTemplate):
        def __init__(self, filename, **kwargs):
            super().__init__(filename, **kwargs)
            frame = Frame(
                18*mm, 18*mm,
                W - 36*mm,
                H - 18*mm - 14*mm,
                id="main"
            )
            self.addPageTemplates([PageTemplate(id="body", frames=[frame])])

    doc = BodyDoc(
        body_buf,
        pagesize=A4,
        title="DeepGuard AI -- Startup Pitch",
        author="Divyanshu Choudhary",
        subject="DeepGuard AI Pre-Seed Pitch",
    )
    story = build_body(doc, styles)
    doc.build(story, canvasmaker=PitchCanvas)

    # ── Step 3: Merge cover + body ──
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        from PyPDF2 import PdfReader, PdfWriter

    writer = PdfWriter()

    cover_reader = PdfReader(cover_tmp)
    for page in cover_reader.pages:
        writer.add_page(page)

    body_buf.seek(0)
    body_reader = PdfReader(body_buf)
    for page in body_reader.pages:
        writer.add_page(page)

    writer.add_metadata({
        "/Title": "DeepGuard AI -- Startup Pitch Document",
        "/Author": "Divyanshu Choudhary",
        "/Subject": "Pre-Seed Investment Pitch -- Confidential",
        "/Keywords": "DeepGuard, Deepfake Detection, AI Security, Digital Forensics",
        "/Creator": "DeepGuard PDF Generator v1.0",
    })

    with open(OUTPUT_PATH, "wb") as f:
        writer.write(f)

    # Cleanup temp file
    os.remove(cover_tmp)

    size_kb = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"PDF saved! Size: {size_kb:.1f} KB  |  Location: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()

