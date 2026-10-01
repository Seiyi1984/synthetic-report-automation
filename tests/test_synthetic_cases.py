from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from independent_report_pipeline.manifest import sha256_file
from independent_report_pipeline.parser import parse_pdf
from independent_report_pipeline.pipeline import run_pipeline

from support import VALID_LINES, without_prefix, write_fixture_pdf


class SyntheticCaseTests(unittest.TestCase):
    def test_syn_01_valid_input_produces_normalized_report_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_pdf = root / "input.pdf"
            write_fixture_pdf(input_pdf, VALID_LINES)
            normalized = parse_pdf(input_pdf)
            self.assertEqual(normalized.report_id, "RPT-SYN-0001")
            self.assertEqual([item.status for item in normalized.results], ["NORMAL", "HIGH", "LOW"])

            run = run_pipeline(input_pdf, root / "output")
            self.assertEqual(run.status, "SUCCESS")
            self.assertTrue(run.report_path and run.report_path.is_file())
            self.assertTrue(run.normalized_path and run.normalized_path.is_file())
            manifest = json.loads(run.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "SUCCESS")
            self.assertEqual(manifest["input"]["sha256"], sha256_file(input_pdf))
            self.assertEqual(manifest["outputs"][0]["sha256"], sha256_file(run.report_path))

    def test_syn_02_repeated_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_pdf = root / "input.pdf"
            write_fixture_pdf(input_pdf, VALID_LINES)
            first = run_pipeline(input_pdf, root / "first")
            second = run_pipeline(input_pdf, root / "second")
            self.assertEqual(first.status, "SUCCESS")
            self.assertEqual(second.status, "SUCCESS")
            self.assertEqual(first.report_path.read_bytes(), second.report_path.read_bytes())
            self.assertEqual(first.normalized_path.read_bytes(), second.normalized_path.read_bytes())
            self.assertEqual(first.manifest_path.read_bytes(), second.manifest_path.read_bytes())

    def test_syn_03_missing_required_field_fails_closed(self) -> None:
        self._assert_failure(without_prefix("SUBJECT_ID:"), "MISSING_FIELD")

    def test_syn_04_duplicate_result_code_fails_closed(self) -> None:
        lines = list(VALID_LINES)
        lines.insert(-1, "RESULT|ALPHA|Another Alpha|2.0|arb.u.|1.0|5.0")
        self._assert_failure(tuple(lines), "DUPLICATE_RESULT")

    def test_syn_05_malformed_numeric_value_fails_closed(self) -> None:
        lines = tuple(
            line.replace("RESULT|BETA|Marker Beta|8.4|", "RESULT|BETA|Marker Beta|not-a-number|")
            for line in VALID_LINES
        )
        self._assert_failure(lines, "INVALID_NUMBER")

    def _assert_failure(self, lines: tuple[str, ...], expected_code: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_pdf = root / "input.pdf"
            output_dir = root / "output"
            write_fixture_pdf(input_pdf, lines)
            run = run_pipeline(input_pdf, output_dir)
            self.assertEqual(run.status, "FAILED")
            self.assertEqual(run.error_code, expected_code)
            self.assertIsNone(run.report_path)
            self.assertFalse((output_dir / "synthetic-report.pdf").exists())
            manifest = json.loads(run.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "FAILED")
            self.assertEqual(manifest["failure"]["code"], expected_code)


if __name__ == "__main__":
    unittest.main()
