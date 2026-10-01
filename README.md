# Independent Synthetic Report Pipeline

A clean-room portfolio reimplementation of a small deterministic document-automation workflow. The project parses one independently specified synthetic laboratory PDF, validates and normalizes its data, produces a deterministic PDF report, and records content hashes in a machine-readable manifest.

The repository contains invented demonstration data only. It is not intended for clinical, diagnostic, production, or regulated use.

## What this MVP demonstrates

- one synthetic PDF input format;
- one generic text parser for the repository-owned format;
- an immutable normalized data model;
- deterministic PDF report generation;
- fail-closed handling for missing, duplicate, and malformed data;
- success and failure manifests with SHA-256 evidence;
- five synthetic verification cases;
- requirements-to-tests traceability.

## Quick start

Requirements: Python 3.11 or later and the packages pinned in `requirements.lock`.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.lock
.venv\Scripts\python.exe -m pip install -e .
.venv\Scripts\python.exe scripts\generate_synthetic_input.py
.venv\Scripts\synthetic-report.exe examples\input\synthetic_lab_report.pdf --output-dir output\example
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

The successful pipeline writes:

```text
output/example/
  normalized-data.json
  synthetic-report.pdf
  run-manifest.json
```

The root `output/` directory is excluded from version control. Curated synthetic evidence under `examples/output/` is committed for review. The example input can always be regenerated from the repository-owned synthetic specification.

## Failure behavior

The pipeline validates the complete input before creating a report. Missing required fields, duplicate result codes, malformed rows, and invalid numeric ranges produce a failure manifest and no report. Failure is explicit; missing data is never guessed or silently ignored.

## Evidence and design documents

- [Requirements](docs/requirements.md)
- [Synthetic input specification](specs/synthetic-input-spec.md)
- [Architecture](docs/architecture.md)
- [Traceability](docs/traceability.md)
- [Validation summary](docs/validation-summary.md)
- [Clean-room declaration](CLEAN_ROOM_DECLARATION.md)

## Reproducibility boundary

Determinism is evaluated for the same source revision, dependency versions, Python major/minor version, operating system, input bytes, and configuration. The generated report intentionally omits wall-clock timestamps and environment-specific absolute paths.

## Publication status

This portfolio is intended for public source review, but no public license is granted. Repository administration, publication, licensing, and release remain Human Owner decisions.
