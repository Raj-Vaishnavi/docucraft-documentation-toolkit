import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "docucraft.py"
SPEC = importlib.util.spec_from_file_location("docucraft", SCRIPT)
docucraft = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = docucraft
SPEC.loader.exec_module(docucraft)


class MarkdownChecksTest(unittest.TestCase):
    def test_complete_document_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "guide.md"
            file.write_text("# Guide\n\n## Overview\n\n## Before you begin\n\n## Procedure\n\n## Troubleshooting\n", encoding="utf-8")
            self.assertEqual([], docucraft.check_markdown(file))

    def test_reports_missing_title_and_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "guide.md"
            file.write_text("## Overview\n", encoding="utf-8")
            codes = {f.code for f in docucraft.check_markdown(file)}
            self.assertIn("missing-title", codes)
            self.assertIn("missing-section", codes)

    def test_detects_broken_relative_link_and_ignores_external(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "guide.md"
            file.write_text("# Guide\n\n[missing](missing.md) [web](https://example.com)\n", encoding="utf-8")
            findings = docucraft.check_markdown(file, [], {})
            self.assertEqual(["broken-link"], [f.code for f in findings])
            self.assertEqual(3, findings[0].line)

    def test_detects_terminology_variant(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "guide.md"
            file.write_text("# Guide\n\nUse Safe Restore now.\n", encoding="utf-8")
            findings = docucraft.check_markdown(file, [], {"SafeRestore": ["Safe Restore"]})
            self.assertEqual("terminology", findings[0].code)

    def test_ignores_link_inside_fenced_code(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "guide.md"
            file.write_text("# Guide\n\n```md\n[bad](missing.md)\n```\n", encoding="utf-8")
            self.assertEqual([], docucraft.check_markdown(file, [], {}))


if __name__ == "__main__":
    unittest.main()
