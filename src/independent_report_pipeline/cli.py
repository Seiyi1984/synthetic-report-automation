"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the independent synthetic report pipeline."
    )
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run = run_pipeline(args.input_pdf, args.output_dir)
    print(
        json.dumps(
            {
                "status": run.status,
                "manifest": run.manifest_path.name,
                "report": run.report_path.name if run.report_path else None,
                "error_code": run.error_code,
            },
            sort_keys=True,
        )
    )
    return 0 if run.status == "SUCCESS" else 2
