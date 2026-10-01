"""Strict parser for the independently specified synthetic PDF format."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from pypdf import PdfReader

from .errors import PipelineInputError
from .models import NormalizedReport, NormalizedResult

TITLE = "SYNTHETIC LABORATORY INPUT"
RESULT_HEADER = "RESULT|CODE|NAME|VALUE|UNIT|REF_LOW|REF_HIGH"
END_MARKER = "END_RESULTS"
SUPPORTED_SPEC_VERSION = "1.0"
REQUIRED_FIELDS = (
    "SPEC_VERSION",
    "LAB_ID",
    "REPORT_ID",
    "SUBJECT_ID",
    "COLLECTED_DATE",
)


def _decimal(value: str, field_name: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise PipelineInputError(
            "INVALID_NUMBER", f"{field_name} must be a decimal number"
        ) from exc
    if not parsed.is_finite():
        raise PipelineInputError(
            "INVALID_NUMBER", f"{field_name} must be finite"
        )
    return parsed


def _extract_lines(pdf_path: Path) -> list[str]:
    if not pdf_path.is_file():
        raise PipelineInputError("INPUT_NOT_FOUND", "Input PDF was not found")
    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:
        raise PipelineInputError("INVALID_PDF", "Input is not a readable PDF") from exc
    if reader.is_encrypted:
        raise PipelineInputError("INVALID_PDF", "Encrypted PDFs are not accepted")
    lines: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        lines.extend(line.strip() for line in text.splitlines() if line.strip())
    if not lines:
        raise PipelineInputError("EMPTY_INPUT", "PDF contains no extractable text")
    return lines


def parse_pdf(pdf_path: Path) -> NormalizedReport:
    lines = _extract_lines(Path(pdf_path))
    if lines[0] != TITLE:
        raise PipelineInputError("INVALID_TITLE", "Synthetic input title is missing")

    metadata: dict[str, str] = {}
    results: list[NormalizedResult] = []
    seen_codes: set[str] = set()
    in_results = False
    ended = False

    for line in lines[1:]:
        if ended:
            raise PipelineInputError(
                "TRAILING_CONTENT", "Content after END_RESULTS is not accepted"
            )
        if line == RESULT_HEADER:
            if in_results:
                raise PipelineInputError("INVALID_STRUCTURE", "Duplicate result header")
            in_results = True
            continue
        if line == END_MARKER:
            if not in_results:
                raise PipelineInputError("INVALID_STRUCTURE", "END_RESULTS appears too early")
            ended = True
            continue
        if not in_results:
            if ":" not in line:
                raise PipelineInputError("INVALID_STRUCTURE", "Malformed metadata line")
            key, value = (part.strip() for part in line.split(":", 1))
            if key not in REQUIRED_FIELDS:
                raise PipelineInputError("UNKNOWN_FIELD", f"Unknown metadata field: {key}")
            if key in metadata:
                raise PipelineInputError("DUPLICATE_FIELD", f"Duplicate metadata field: {key}")
            if not value:
                raise PipelineInputError("MISSING_FIELD", f"Required field is empty: {key}")
            metadata[key] = value
            continue

        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 7 or parts[0] != "RESULT":
            raise PipelineInputError("MALFORMED_ROW", "Result row must contain seven fields")
        _, code, name, value_text, unit, low_text, high_text = parts
        if not all((code, name, unit)):
            raise PipelineInputError("MISSING_FIELD", "Result code, name, and unit are required")
        if code in seen_codes:
            raise PipelineInputError("DUPLICATE_RESULT", f"Duplicate result code: {code}")
        value = _decimal(value_text, f"{code}.VALUE")
        reference_low = _decimal(low_text, f"{code}.REF_LOW")
        reference_high = _decimal(high_text, f"{code}.REF_HIGH")
        if reference_low > reference_high:
            raise PipelineInputError(
                "INVALID_RANGE", f"Reference range is inverted for {code}"
            )
        seen_codes.add(code)
        results.append(
            NormalizedResult(
                code=code,
                name=name,
                value=value,
                unit=unit,
                reference_low=reference_low,
                reference_high=reference_high,
            )
        )

    missing = [field for field in REQUIRED_FIELDS if field not in metadata]
    if missing:
        raise PipelineInputError(
            "MISSING_FIELD", f"Missing required metadata: {', '.join(missing)}"
        )
    if metadata["SPEC_VERSION"] != SUPPORTED_SPEC_VERSION:
        raise PipelineInputError(
            "UNSUPPORTED_SPEC", "Only synthetic input specification 1.0 is accepted"
        )
    if not in_results or not ended:
        raise PipelineInputError("INVALID_STRUCTURE", "Result section is incomplete")
    if not results:
        raise PipelineInputError("MISSING_RESULTS", "At least one result is required")
    try:
        collected_date = date.fromisoformat(metadata["COLLECTED_DATE"])
    except ValueError as exc:
        raise PipelineInputError(
            "INVALID_DATE", "COLLECTED_DATE must use YYYY-MM-DD"
        ) from exc

    return NormalizedReport(
        spec_version=metadata["SPEC_VERSION"],
        lab_id=metadata["LAB_ID"],
        report_id=metadata["REPORT_ID"],
        subject_id=metadata["SUBJECT_ID"],
        collected_date=collected_date,
        results=tuple(sorted(results, key=lambda item: item.code)),
    )
