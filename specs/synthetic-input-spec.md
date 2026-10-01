# Synthetic input specification 1.0

## Purpose

This specification defines the only accepted input format for the portfolio MVP. It was invented for this repository and is not intended to represent a real laboratory, vendor, product, assay, or reporting standard.

## Document form

The input is a text-based PDF. After text extraction, each non-empty line is interpreted independently.

The document must begin with:

```text
SYNTHETIC LABORATORY INPUT
```

The required metadata lines use `KEY: VALUE` syntax:

```text
SPEC_VERSION: 1.0
LAB_ID: LAB-SYN-001
REPORT_ID: RPT-SYN-0001
SUBJECT_ID: SUBJECT-SYN-0001
COLLECTED_DATE: 2030-01-15
```

Required metadata keys may appear in any order but must appear exactly once. Unknown metadata keys are rejected.

## Result rows

The result section begins with this exact header:

```text
RESULT|CODE|NAME|VALUE|UNIT|REF_LOW|REF_HIGH
```

Each following row has seven pipe-separated fields:

```text
RESULT|ALPHA|Marker Alpha|4.2|arb.u.|1.0|5.0
```

The section ends with:

```text
END_RESULTS
```

Rules:

- `CODE`, `NAME`, and `UNIT` must be non-empty ASCII text.
- `VALUE`, `REF_LOW`, and `REF_HIGH` must be finite decimal numbers.
- `REF_LOW` must not exceed `REF_HIGH`.
- Every `CODE` must be unique within the document.
- At least one result row is required.
- Content after `END_RESULTS` is rejected.

## Normalized status

For each result:

- `LOW` when `VALUE < REF_LOW`;
- `NORMAL` when `REF_LOW <= VALUE <= REF_HIGH`;
- `HIGH` when `VALUE > REF_HIGH`.

## Fail-closed behavior

Missing fields, duplicates, malformed rows, unknown metadata, unsupported specification versions, invalid dates, non-finite numbers, and ambiguous structure must stop report generation. The pipeline records a failure manifest and does not infer a replacement value.
