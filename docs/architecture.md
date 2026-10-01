# Architecture

## Overview

```text
synthetic PDF
     |
     v
PDF text extraction
     |
     v
strict parser and validation -----> failure manifest
     |
     v
immutable normalized model
     |
     +----> canonical normalized JSON
     |
     v
deterministic PDF renderer
     |
     v
success manifest with SHA-256 evidence
```

## Components

### Synthetic input generator

`scripts/generate_synthetic_input.py` creates the single committed example from literal values defined for this repository. ReportLab invariant mode and fixed document metadata avoid time-dependent bytes.

### Parser

`parser.py` extracts text with pypdf and recognizes only `specs/synthetic-input-spec.md`. It rejects unknown metadata, duplicate fields, malformed rows, duplicate result codes, invalid numbers, unsupported versions, and content outside the defined structure.

### Normalized model

`models.py` uses frozen dataclasses and `Decimal` values. Derived status is deterministic and serialized through a canonical dictionary representation.

### Pipeline

`pipeline.py` validates before rendering. A known input failure produces only a failure manifest. A valid input produces canonical JSON, a deterministic report PDF, and a success manifest.

### Integrity evidence

`manifest.py` uses SHA-256 for the input, normalized JSON, and report. Paths stored in manifests are repository-relative filenames rather than machine-specific absolute paths.

## Trust boundaries

- Input PDF content is untrusted data.
- Only the repository-owned synthetic format is accepted.
- No network, model, external service, database, office application, or production repository is required.
- The pipeline does not make clinical or diagnostic decisions.

## Determinism controls

- pinned direct dependencies;
- decimal rather than binary floating-point parsing;
- stable sorting by result code;
- canonical JSON with sorted keys and fixed separators;
- invariant PDF generation with fixed metadata;
- no wall-clock time, random identifiers, or absolute paths in outputs.

## Failure controls

- full parsing and validation precede report creation;
- validation failures use stable error codes;
- failure manifests use `FAILED`, never a success-like fallback;
- unexpected software exceptions are not converted into successful output.
