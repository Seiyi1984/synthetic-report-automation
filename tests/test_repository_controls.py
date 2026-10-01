from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".toml", ".lock", ".gitignore"}
REQUIREMENT_IDS = {f"REQ-{number:02d}" for number in range(1, 11)}


class RepositoryControlTests(unittest.TestCase):
    def test_ctrl_01_clean_room_boundary_controls(self) -> None:
        self.assertTrue((PROJECT_ROOT / "CLEAN_ROOM_DECLARATION.md").is_file())
        self.assertFalse((PROJECT_ROOT / ".gitmodules").exists())
        for path in PROJECT_ROOT.rglob("*"):
            if ".git" in path.parts or path.name == "__pycache__":
                continue
            self.assertFalse(path.is_symlink(), f"Symlink not allowed: {path}")
            if path.is_file() and path.suffix in TEXT_SUFFIXES:
                text = path.read_text(encoding="utf-8")
                windows_absolute = re.search(r"(?i)[a-z]:\\+", text)
                external_markers = ("file:" + "//", "smb:" + "//")
                self.assertIsNone(
                    windows_absolute,
                    f"Absolute local filesystem reference in {path}",
                )
                self.assertFalse(
                    any(marker in text.lower() for marker in external_markers),
                    f"External filesystem reference in {path}",
                )

    def test_ctrl_02_every_requirement_has_traceability(self) -> None:
        requirements = (PROJECT_ROOT / "docs" / "requirements.md").read_text(encoding="utf-8")
        traceability = (PROJECT_ROOT / "docs" / "traceability.md").read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r"REQ-\d{2}", requirements)), REQUIREMENT_IDS)
        self.assertTrue(REQUIREMENT_IDS.issubset(set(re.findall(r"REQ-\d{2}", traceability))))
        for verification_id in (
            "TEST-SYN-01",
            "TEST-SYN-02",
            "TEST-SYN-03",
            "TEST-SYN-04",
            "TEST-SYN-05",
            "TEST-CTRL-01",
            "TEST-CTRL-02",
            "TEST-CTRL-03",
            "TEST-CTRL-04",
        ):
            self.assertIn(verification_id, traceability)

    def test_ctrl_03_required_public_documents_exist(self) -> None:
        required = (
            "README.md",
            "docs/architecture.md",
            "docs/requirements.md",
            "docs/traceability.md",
            "docs/validation-summary.md",
        )
        for relative in required:
            path = PROJECT_ROOT / relative
            self.assertTrue(path.is_file(), f"Missing document: {relative}")
        combined = "\n".join(
            (PROJECT_ROOT / relative).read_text(encoding="utf-8")
            for relative in required
        ).lower()
        self.assertIn("synthetic", combined)
        self.assertIn("not intended for clinical", combined)

    def test_ctrl_04_command_line_workflow(self) -> None:
        input_pdf = PROJECT_ROOT / "examples" / "input" / "synthetic_lab_report.pdf"
        self.assertTrue(input_pdf.is_file())
        with tempfile.TemporaryDirectory() as directory:
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "independent_report_pipeline",
                    str(input_pdf),
                    "--output-dir",
                    directory,
                ],
                cwd=PROJECT_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn('"status": "SUCCESS"', completed.stdout)
            self.assertTrue((Path(directory) / "run-manifest.json").is_file())
            self.assertTrue((Path(directory) / "synthetic-report.pdf").is_file())


if __name__ == "__main__":
    unittest.main()
