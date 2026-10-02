"""
Evidence PDF Generator for HACTM.
Uses ReportLab to produce clean, professional PDF reports for Security Evidence exports.
"""

import io
import os
from datetime import datetime, timezone
from typing import Any, Dict, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically for 'Page X of Y' header and footer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Top Header on pages > 1
        if self._pageNumber > 1:
            self.setLineWidth(0.5)
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.line(36, 756, 576, 756)
            self.drawString(36, 762, "HACTM — Structured Security Evidence Report")
            self.drawRightString(576, 762, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))

        # Bottom Footer on all pages
        self.setLineWidth(0.5)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.line(36, 45, 576, 45)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawString(36, 32, "CONFIDENTIAL & PROPRIETARY — HIERARCHICAL ADAPTIVE CYBER TRUST MESH")
        self.drawRightString(576, 32, page_text)
        self.restoreState()


def generate_evidence_pdf(report_data: Dict[str, Any]) -> bytes:
    """
    Generates a PDF document in bytes from report_data.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom typography & color styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=3,
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        spaceAfter=8,
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155'),
    )
    header_col_style = ParagraphStyle(
        'HeaderColStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#FFFFFF'),
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("Structured Security Evidence Report", title_style))
    story.append(Paragraph("Hierarchical Adaptive Cyber Trust Mesh (HACTM) — Automated Evidence Audit Artifact", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=10))

    # Metadata Table
    report_id = report_data.get("report_id", "RPT-EVD-UNKNOWN")
    gen_time = report_data.get("generated_at", "")
    if isinstance(gen_time, datetime):
        gen_time_str = gen_time.strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        gen_time_str = str(gen_time)

    filters = report_data.get("filters", {})
    filter_strs = []
    if filters.get("entity_id"): filter_strs.append(f"Entity: {filters['entity_id']}")
    if filters.get("event_type"): filter_strs.append(f"Type: {filters['event_type']}")
    if filters.get("source"): filter_strs.append(f"Source: {filters['source']}")
    if filters.get("min_risk") is not None: filter_strs.append(f"Min Risk: {filters['min_risk']}")
    filter_desc = ", ".join(filter_strs) if filter_strs else "None (All stored evidence in scope)"

    meta_table_data = [
        [
            Paragraph("<b>Report ID:</b>", body_style),
            Paragraph(f"<font face='Courier'>{report_id}</font>", body_style),
            Paragraph("<b>Generated:</b>", body_style),
            Paragraph(gen_time_str, body_style),
        ],
        [
            Paragraph("<b>Applied Filters:</b>", body_style),
            Paragraph(filter_desc, body_style),
            Paragraph("<b>Total Matching:</b>", body_style),
            Paragraph(f"<b>{report_data.get('evidence_count', 0)} records</b>", body_style),
        ],
    ]
    meta_table = Table(meta_table_data, colWidths=[85, 205, 85, 165])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Summary Section
    summary = report_data.get("summary", {})
    story.append(Paragraph("1. Executive Evidence Summary", heading_style))

    sev_dist = summary.get("severity_distribution", {})
    avg_risk = summary.get("average_cyber_risk_score", 0.0)
    high_count = summary.get("high_risk_events_count", 0)
    total_count = report_data.get("evidence_count", 0)

    summary_table_data = [
        [
            Paragraph("<b>Total Records</b>", body_style),
            Paragraph("<b>Avg Cyber Risk</b>", body_style),
            Paragraph("<b>High / Critical Alerts</b>", body_style),
            Paragraph("<b>Severity Breakdown</b>", body_style),
        ],
        [
            Paragraph(f"<font size=11><b>{total_count}</b></font>", body_style),
            Paragraph(f"<font size=11 color='#0284C7'><b>{avg_risk:.4f}</b></font>", body_style),
            Paragraph(f"<font size=11 color='#E11D48'><b>{high_count}</b></font>", body_style),
            Paragraph(
                f"Low: {sev_dist.get('LOW', 0)} | Med: {sev_dist.get('MEDIUM', 0)}<br/>"
                f"High: {sev_dist.get('HIGH', 0)} | Crit: {sev_dist.get('CRITICAL', 0)}",
                body_style
            ),
        ]
    ]
    summary_table = Table(summary_table_data, colWidths=[110, 110, 140, 180])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FFFFFF')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Evidence Records Table
    story.append(Paragraph("2. Audited Evidence Records", heading_style))

    records = report_data.get("records", [])
    if not records:
        story.append(Paragraph("<i>No evidence records matched the selected filters.</i>", body_style))
    else:
        table_headers = [
            Paragraph("<b>Event ID</b>", header_col_style),
            Paragraph("<b>Type</b>", header_col_style),
            Paragraph("<b>Source / Agent</b>", header_col_style),
            Paragraph("<b>Target Entity</b>", header_col_style),
            Paragraph("<b>Severity</b>", header_col_style),
            Paragraph("<b>Risk Score</b>", header_col_style),
            Paragraph("<b>Timestamp</b>", header_col_style),
        ]
        rec_rows = [table_headers]

        for rec in records:
            e_id = rec.get("event_id") if isinstance(rec, dict) else getattr(rec, "event_id", "")
            e_type = rec.get("event_type") if isinstance(rec, dict) else getattr(rec, "event_type", "")
            e_agent = (rec.get("agent_id") or rec.get("source") or "N/A") if isinstance(rec, dict) else (getattr(rec, "agent_id", None) or getattr(rec, "source", None) or "N/A")
            e_entity = rec.get("entity_id") if isinstance(rec, dict) else getattr(rec, "entity_id", "")
            e_sev = rec.get("severity") if isinstance(rec, dict) else getattr(rec, "severity", "LOW")
            e_risk = rec.get("risk_score") if isinstance(rec, dict) else getattr(rec, "risk_score", 0.0)
            e_ts = rec.get("timestamp") if isinstance(rec, dict) else getattr(rec, "timestamp", "")

            if isinstance(e_ts, datetime):
                e_ts_str = e_ts.strftime("%Y-%m-%d %H:%M")
            else:
                e_ts_str = str(e_ts)[:16]

            sev_color = "#059669" if e_sev == "LOW" else "#D97706" if e_sev == "MEDIUM" else "#DC2626"

            row = [
                Paragraph(f"<font face='Courier' color='#0284C7'><b>{e_id}</b></font>", body_style),
                Paragraph(str(e_type), body_style),
                Paragraph(f"<font face='Courier'>{e_agent[:18]}</font>", body_style),
                Paragraph(f"<font face='Courier'>{e_entity[:18]}</font>", body_style),
                Paragraph(f"<font color='{sev_color}'><b>{e_sev}</b></font>", body_style),
                Paragraph(f"<b>{float(e_risk):.4f}</b>", body_style),
                Paragraph(f"<font size=7.5>{e_ts_str}</font>", body_style),
            ]
            rec_rows.append(row)

        records_table = Table(rec_rows, colWidths=[85, 65, 90, 100, 55, 60, 85])
        records_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ]))
        story.append(records_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
