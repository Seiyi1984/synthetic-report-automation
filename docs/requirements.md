# Requirements

Status: Human Owner accepted

## REQ-01 - Clean-room isolation

The system shall be implemented in a new repository with no imported version-control history. Implementation, specifications, fixtures, tests, documentation, and evidence shall be based only on requirements and synthetic specifications defined for this project.

## REQ-02 - Synthetic input and generic parsing

The system shall provide one independently created synthetic laboratory PDF input and one generic parser that converts it into the repository-defined normalized data model.

## REQ-03 - Deterministic report pipeline

For identical source revision, dependency versions, execution platform, configuration, and input bytes, the system shall produce identical normalized data, report bytes, and success-manifest bytes.

## REQ-04 - Fail-closed data handling

Missing required fields, duplicate result identifiers, malformed rows, and invalid values shall prevent report generation and produce an explicit traceable failure result. The system shall not guess, ignore, or silently replace invalid input.

## REQ-05 - Manifest and integrity controls

Successful runs shall produce a machine-readable manifest containing version, specification, input, normalized-data, output, status, and SHA-256 evidence. Failed runs shall produce a failure manifest and shall not be represented as successful.

## REQ-06 - Synthetic verification set

The project shall provide five independently created synthetic verification cases covering a valid input, repeat-run determinism, a missing required field, a duplicate result code, and a malformed numeric value.

## REQ-07 - Requirements-to-tests traceability

Each accepted requirement shall be mapped to identified verification tests or review checks. Results shall distinguish PASS, FAIL, and not-run states.

## REQ-08 - Public documentation

The project shall provide a README, architecture description, requirements-to-tests traceability record, and validation summary. Documentation shall not imply production, clinical, or regulatory validation.

## REQ-09 - Reproducible local execution

The project shall provide documented local commands to generate the synthetic input, execute the parser and report pipeline, produce manifests and checksums, and run verification tests.

## REQ-10 - Protected external boundary

The implementation shall not use an external production repository as an implementation reference, dependency, test oracle, or comparison baseline. The project shall remain local with no push or publication unless separately authorized by the Human Owner.
