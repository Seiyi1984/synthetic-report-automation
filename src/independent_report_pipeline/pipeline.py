"""Deterministic orchestration with explicit success and failure manifests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import __version__
from .errors import PipelineInputError
from .manifest import sha256_bytes, sha256_file, write_canonical_json
from .parser import parse_pdf
from .report import render_report


@dataclass(frozen=True, slots=True)
class PipelineRun:
    status: str
    manifest_path: Path
    report_path: Path | None
    normalized_path: Path | None
    error_code: str | None = None


def _base_manifest(input_pdf: Path) -> dict[str, object]:
    return {
        "manifest_schema": "1.0",
        "pipeline_version": __version__,
        "input": {
            "filename": input_pdf.name,
            "sha256": sha256_file(input_pdf),
        },
    }


def run_pipeline(input_pdf: Path, output_dir: Path) -> PipelineRun:
    input_pdf = Path(input_pdf).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "run-manifest.json"
    report_path = output_dir / "synthetic-report.pdf"
    normalized_path = output_dir / "normalized-data.json"

    try:
        base = _base_manifest(input_pdf)
        normalized = parse_pdf(input_pdf)
    except PipelineInputError as exc:
        input_evidence: dict[str, str] = {"filename": input_pdf.name}
        if input_pdf.is_file():
            input_evidence["sha256"] = sha256_file(input_pdf)
        manifest = {
            "manifest_schema": "1.0",
            "pipeline_version": __version__,
            "status": "FAILED",
            "input": input_evidence,
            "failure": {"code": exc.code, "message": exc.message},
        }
        write_canonical_json(manifest_path, manifest)
        return PipelineRun(
            status="FAILED",
            manifest_path=manifest_path,
            report_path=None,
            normalized_path=None,
            error_code=exc.code,
        )

    write_canonical_json(normalized_path, normalized.to_dict())
    render_report(normalized, report_path)
    normalized_bytes = normalized_path.read_bytes()
    manifest = {
        **base,
        "status": "SUCCESS",
        "specification": normalized.spec_version,
        "normalized_data": {
            "filename": normalized_path.name,
            "sha256": sha256_bytes(normalized_bytes),
        },
        "outputs": [
            {"filename": report_path.name, "sha256": sha256_file(report_path)}
        ],
    }
    write_canonical_json(manifest_path, manifest)
    return PipelineRun(
        status="SUCCESS",
        manifest_path=manifest_path,
        report_path=report_path,
        normalized_path=normalized_path,
    )
