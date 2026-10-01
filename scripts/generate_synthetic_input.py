"""Generate the single repository-owned synthetic PDF input."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

LINES = (
    "SYNTHETIC LABORATORY INPUT",
    "SPEC_VERSION: 1.0",
    "LAB_ID: LAB-SYN-001",
    "REPORT_ID: RPT-SYN-0001",
    "SUBJECT_ID: SUBJECT-SYN-0001",
    "COLLECTED_DATE: 2030-01-15",
    "RESULT|CODE|NAME|VALUE|UNIT|REF_LOW|REF_HIGH",
    "RESULT|ALPHA|Marker Alpha|4.2|arb.u.|1.0|5.0",
    "RESULT|BETA|Marker Beta|8.4|arb.u.|2.0|7.0",
    "RESULT|GAMMA|Marker Gamma|0.5|arb.u.|0.8|3.5",
    "END_RESULTS",
)


def write_pdf(path: Path, lines: tuple[str, ...] = LINES) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    page = canvas.Canvas(str(path), pagesize=A4, invariant=1, pageCompression=0)
    page.setTitle("Synthetic Laboratory Input")
    page.setAuthor("Independent Synthetic Report Pipeline")
    page.setCreator("Independent Synthetic Report Pipeline 0.1.0")
    _, height = A4
    page.setFont("Courier", 9)
    y = height - 55
    for line in lines:
        page.drawString(48, y, line)
        y -= 17
    page.showPage()
    page.save()


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    output = project_root / "examples" / "input" / "synthetic_lab_report.pdf"
    write_pdf(output)
    print(output)
