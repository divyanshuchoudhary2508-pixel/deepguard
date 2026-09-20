"""
Server-Side Forensic PDF Verification Report Generator for DeepGuard.
Uses ReportLab to compile enterprise verification reports with cryptographic SHA-256 hashes,
embedded visual evidence (Original, Grad-CAM++, Facial Mesh), and EXIF metadata.
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def compute_sha256(file_path: str) -> str:
    """Computes SHA-256 cryptographic hash of image file."""
    if not os.path.exists(file_path):
        return "N/A"
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()


def build_pdf_report(report_data: dict, original_img_path: str, heatmap_path: str, mesh_path: str, output_pdf_path: str) -> str:
    """
    Generates a formal PDF Forensic Verification Report using ReportLab.
    Returns absolute path of created PDF file.
    """
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom Color Palette
    c_navy = colors.HexColor("#0f172a")
    c_indigo = colors.HexColor("#6366f1")
    c_slate = colors.HexColor("#334155")
    c_red = colors.HexColor("#f43f5e")
    c_green = colors.HexColor("#10b981")
    c_light_bg = colors.HexColor("#f8fafc")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=c_navy,
        spaceAfter=2
    )
    sub_title_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=c_indigo,
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=c_navy,
        spaceBefore=8,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=c_slate,
        leading=12
    )
    badge_style = ParagraphStyle(
        'BadgeText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.white,
        alignment=1
    )

    # 1. Header Banner
    header_data = [
        [
            Paragraph("DEEPGUARD FORENSIC VERIFICATION REPORT", title_style),
            Paragraph("CONFIDENTIAL FORENSIC AUDIT", ParagraphStyle('RightText', parent=body_style, alignment=2, fontName='Helvetica-Bold', textColor=c_indigo))
        ],
        [
            Paragraph("EXPLAINABLE MEDIA INTEGRITY PROTOCOL &bull; IEEE TENCON 2024 BENCHMARK", sub_title_style),
            Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ParagraphStyle('RightTime', parent=body_style, alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[380, 160])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=c_indigo, spaceBefore=4, spaceAfter=12))

    # 2. SHA-256 & Audit Metadata Table
    sha256_hash = compute_sha256(original_img_path)
    meta_table_data = [
        [Paragraph("<b>Verification Report ID:</b>", body_style), Paragraph(f"<code>{report_data.get('report_id', 'DG-2026')}</code>", body_style)],
        [Paragraph("<b>Analyzed Target File:</b>", body_style), Paragraph(report_data.get('filename', 'Unknown'), body_style)],
        [Paragraph("<b>SHA-256 Hash:</b>", body_style), Paragraph(f"<font size=7><code>{sha256_hash}</code></font>", body_style)],
        [Paragraph("<b>Detection Architecture:</b>", body_style), Paragraph("DenseNet121 + FFT Spectral + Laplacian Seam Ensemble", body_style)]
    ]

    meta_table = Table(meta_table_data, colWidths=[140, 400])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light_bg),
        ('PADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 3. Model Assessment Outcome Box
    label = report_data.get('result_label', 'UNKNOWN')
    is_fake = "DEEPFAKE" in label or "MORPHED" in label or "SYNTHETIC" in label
    conf = report_data.get('confidence_percentage', 90.0)

    result_bg = c_red if is_fake else c_green
    res_box_data = [
        [
            Paragraph(f"ASSESSMENT OUTCOME: <b>{label}</b>", badge_style),
            Paragraph(f"CALIBRATED CONFIDENCE: <b>{conf}%</b>", badge_style)
        ]
    ]
    res_table = Table(res_box_data, colWidths=[330, 210])
    res_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), result_bg),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    story.append(res_table)
    story.append(Spacer(1, 14))

    # 4. Multi-Signal Forensic Details Table
    story.append(Paragraph("Multi-Signal Forensic Breakdown", section_heading))
    
    meta_info = report_data.get('metadata', {})
    lm_info = report_data.get('landmarks', {})

    forensic_data = [
        [
            Paragraph("<b>Signal Module</b>", ParagraphStyle('TableHeader', parent=body_style, fontName='Helvetica-Bold', textColor=colors.white)),
            Paragraph("<b>Extracted Findings & Risk Rating</b>", ParagraphStyle('TableHeader2', parent=body_style, fontName='Helvetica-Bold', textColor=colors.white))
        ],
        [
            Paragraph("<b>EXIF & C2PA Metadata</b>", body_style),
            Paragraph(f"Risk: <b>{meta_info.get('metadata_risk_level', 'N/A')}</b> &bull; Camera: {meta_info.get('camera_make', 'Unknown')} &bull; Software: {meta_info.get('software', 'None')}", body_style)
        ],
        [
            Paragraph("<b>2D Fourier Spectral Ratio</b>", body_style),
            Paragraph("High-frequency power attenuation analyzed (< 0.72 indicates synthetic generation)", body_style)
        ],
        [
            Paragraph("<b>Boundary Seam Texture</b>", body_style),
            Paragraph("Laplacian spatial variance ratio checked for face-body morphing / head splicing", body_style)
        ],
        [
            Paragraph("<b>68-Point Facial Geometry</b>", body_style),
            Paragraph(f"Detected Nodes: <b>{lm_info.get('landmarks_count', 0)}</b> &bull; Eye Symmetry: <b>{lm_info.get('eye_symmetry', 1.0)}</b> &bull; Jaw Warp: <b>{lm_info.get('jawline_warp_index', 0.0)}</b>", body_style)
        ]
    ]

    for_table = Table(forensic_data, colWidths=[170, 370])
    for_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), c_navy),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(for_table)
    story.append(Spacer(1, 14))

    # 5. Triple Visual Evidence Panels
    story.append(Paragraph("Visual Forensic Evidence Panels", section_heading))
    
    img_w, img_h = 165, 140
    img_cells = []

    def get_rl_image(p):
        if p and os.path.exists(p):
            try:
                return RLImage(p, width=img_w, height=img_h)
            except Exception:
                pass
        return Paragraph("Image unavailable", body_style)

    rl_orig = get_rl_image(original_img_path)
    rl_heat = get_rl_image(heatmap_path)
    rl_mesh = get_rl_image(mesh_path)

    images_data = [
        [Paragraph("<b>Original Input Image</b>", body_style), Paragraph("<b>Grad-CAM++ Attention Map</b>", body_style), Paragraph("<b>68-Point Facial Mesh Wireframe</b>", body_style)],
        [rl_orig, rl_heat, rl_mesh]
    ]

    img_table = Table(images_data, colWidths=[180, 180, 180])
    img_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('PADDING', (0,0), (-1,-1), 4)
    ]))
    story.append(img_table)
    story.append(Spacer(1, 16))

    # 6. Disclaimer & Citation Footer
    disclaimer_text = (
        "<b>Scientific Disclaimer:</b> DeepGuard is an AI-assisted digital forensic screening tool. "
        "Grad-CAM++ heatmaps and multi-signal metrics visualize model attention and physical anomalies for human verification. "
        "Based on IEEE TENCON 2024 Deepfake Detection Guidelines."
    )
    story.append(Paragraph(disclaimer_text, ParagraphStyle('Disclaimer', parent=body_style, fontSize=7, textColor=colors.HexColor("#64748b"))))

    # Build PDF Document
    doc.build(story)
    return output_pdf_path


build_pdf_certificate = build_pdf_report

