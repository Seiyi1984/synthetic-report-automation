"""Immutable normalized data model for the repository-owned synthetic format."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


def decimal_text(value: Decimal) -> str:
    """Return stable non-exponential decimal text."""

    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


@dataclass(frozen=True, slots=True)
class NormalizedResult:
    code: str
    name: str
    value: Decimal
    unit: str
    reference_low: Decimal
    reference_high: Decimal

    @property
    def status(self) -> str:
        if self.value < self.reference_low:
            return "LOW"
        if self.value > self.reference_high:
            return "HIGH"
        return "NORMAL"

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "name": self.name,
            "reference_high": decimal_text(self.reference_high),
            "reference_low": decimal_text(self.reference_low),
            "status": self.status,
            "unit": self.unit,
            "value": decimal_text(self.value),
        }


@dataclass(frozen=True, slots=True)
class NormalizedReport:
    spec_version: str
    lab_id: str
    report_id: str
    subject_id: str
    collected_date: date
    results: tuple[NormalizedResult, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "collected_date": self.collected_date.isoformat(),
            "lab_id": self.lab_id,
            "report_id": self.report_id,
            "results": [result.to_dict() for result in self.results],
            "spec_version": self.spec_version,
            "subject_id": self.subject_id,
        }
