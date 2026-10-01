# Validation summary

Status: ENGINEERING VERIFICATION PASSED; HUMAN PUBLICATION REVIEW NOT RUN

Verification date: 2026-10-01

Environment: Windows, Python 3.12.14, pypdf 6.10.0, ReportLab 4.4.9

This summary records only checks executed against this clean-room repository. No production or external-system evidence is applicable to this project.

## Results

| Layer | Evidence | Status |
|---|---|---|
| Synthetic functional cases | TEST-SYN-01 through TEST-SYN-05 | PASS - 5/5 |
| Repository controls | TEST-CTRL-01 through TEST-CTRL-04 | PASS - 4/4 |
| Complete automated suite | `python -m unittest discover -s tests -p "test_*.py" -v` | PASS - 9/9 |
| Input reproducibility | Regenerate the input PDF and compare bytes | PASS - identical SHA-256 |
| PDF structural inspection | Both PDFs reopened with pypdf; each is one page, unencrypted, with extractable text | PASS |
| PDF visual inspection | Both PDFs rendered at 144 DPI and inspected for clipping, overlap, and legibility | PASS |
| Boundary scan | No email, credential assignment, private-key header, IP address, symlink, submodule, or absolute local path detected | PASS |
| Repository state | Independent Git repository with no imported history | PASS |
| Human publication approval | REVIEW-01 | NOT RUN |

## SHA-256 evidence

| Artifact | SHA-256 |
|---|---|
| `examples/input/synthetic_lab_report.pdf` | `3c0d17b6775e9b6ddddf3d7c168716ba26edc9dd286750b5bcd9e1e99018834b` |
| `examples/output/normalized-data.json` | `1be41a8ebebc418b5ead26e7b850c8baf4243bc9cfe91653948f7a9070a4e4d3` |
| `examples/output/synthetic-report.pdf` | `f27572c1171a2850ad0f375832573046a7b3cf5a0c511903befa491c948894c7` |
| `examples/output/run-manifest.json` | `3c3807321507eb72402ef756162a98b504ac6bd1b1843ec524bced0c915b08c0` |

## Boundaries and limitations

- PASS applies only to version 0.1.0 and the environment recorded above.
- Structural and visual PDF checks are separate from automated functional tests.
- No cross-platform execution, external deployment, production comparison, clinical review, regulatory validation, push, publication, or release was performed.
- REVIEW-01 remains an explicit Human Owner gate.
