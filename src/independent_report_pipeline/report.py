"""Deterministic PDF rendering for normalized synthetic data."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .models import NormalizedReport, decimal_text


def render_report(report: NormalizedReport, output_path: Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    page = canvas.Canvas(
        str(temporary),
        pagesize=A4,
        invariant=1,
        pageCompression=0,
    )
    page.setTitle("Synthetic Normalized Report")
    page.setAuthor("Independent Synthetic Report Pipeline")
    page.setCreator("Independent Synthetic Report Pipeline 0.1.0")
    width, height = A4

    page.setFont("Helvetica-Bold", 18)
    page.drawString(48, height - 55, "Synthetic Normalized Report")
    page.setFont("Helvetica", 9)
    page.drawRightString(width - 48, height - 52, "DEMONSTRATION ONLY")

    y = height - 90
    metadata = (
        ("Laboratory", report.lab_id),
        ("Report", report.report_id),
        ("Subject", report.subject_id),
        ("Collected", report.collected_date.isoformat()),
        ("Specification", report.spec_version),
    )
    for label, value in metadata:
        page.setFont("Helvetica-Bold", 10)
        page.drawString(48, y, f"{label}:")
        page.setFont("Helvetica", 10)
        page.drawString(120, y, value)
        y -= 16

    y -= 12
    columns = (48, 102, 235, 310, 365, 455)
    headers = ("Code", "Name", "Value", "Unit", "Reference", "Status")
    page.setFillColorRGB(0.15, 0.20, 0.28)
    page.rect(44, y - 5, width - 88, 20, fill=1, stroke=0)
    page.setFillColorRGB(1, 1, 1)
    page.setFont("Helvetica-Bold", 9)
    for x, header in zip(columns, headers):
        page.drawString(x, y + 1, header)
    y -= 22

    page.setFillColorRGB(0, 0, 0)
    page.setFont("Helvetica", 9)
    for item in report.results:
        values = (
            item.code,
            item.name,
            decimal_text(item.value),
            item.unit,
            f"{decimal_text(item.reference_low)} - {decimal_text(item.reference_high)}",
            item.status,
        )
        for x, value in zip(columns, values):
            page.drawString(x, y, value)
        page.setStrokeColorRGB(0.82, 0.84, 0.87)
        page.line(44, y - 5, width - 44, y - 5)
        y -= 20

    y -= 12
    counts = {status: 0 for status in ("LOW", "NORMAL", "HIGH")}
    for item in report.results:
        counts[item.status] += 1
    page.setFont("Helvetica-Bold", 10)
    page.drawString(48, y, "Summary")
    page.setFont("Helvetica", 10)
    page.drawString(
        110,
        y,
        f"LOW {counts['LOW']} | NORMAL {counts['NORMAL']} | HIGH {counts['HIGH']}",
    )

    page.setFont("Helvetica-Oblique", 8)
    page.setFillColorRGB(0.35, 0.35, 0.35)
    page.drawCentredString(
        width / 2,
        35,
        "Synthetic demonstration only - not for clinical or diagnostic use.",
    )
    page.showPage()
    page.save()
    temporary.replace(output_path)
