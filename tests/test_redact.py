from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from faultscribe.redact import redact_file, redact_text
from faultscribe.report import InputError


class RedactionTests(unittest.TestCase):
    # All values in these tests are intentionally synthetic and non-functional.
    def test_common_patterns_are_replaced(self) -> None:
        source = (
            "contact=synthetic.user@example.test\n"
            "password=not_a_real_secret_123\n"
            "path=/Users/synthetic-user/work/demo\n"
            "aws=AKIA1234567890ABCDEF\n"
        )
        redacted, counts = redact_text(source)
        self.assertNotIn("synthetic.user@example.test", redacted)
        self.assertNotIn("not_a_real_secret_123", redacted)
        self.assertNotIn("/Users/synthetic-user", redacted)
        self.assertGreaterEqual(counts["email"], 1)
        self.assertGreaterEqual(counts["assigned_secret"], 1)

    def test_false_positive_boundary_words_stay(self) -> None:
        source = "The tokenizer is useful; compass points north; passwordless login is enabled.\n"
        redacted, counts = redact_text(source)
        self.assertEqual(redacted, source)
        self.assertEqual(sum(counts.values()), 0)

    def test_known_limitation_opaque_value_is_not_claimed_safe(self) -> None:
        source = "opaque_payload=qwerTYUIopASDFghJKLzXCVBnm123456\n"
        redacted, _ = redact_text(source)
        self.assertEqual(redacted, source)

    def test_empty_file_creates_separate_empty_output_and_preserves_original(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "synthetic-empty.log"
            original.write_text("", encoding="utf-8")
            output, preview, _ = redact_file(original)
            self.assertNotEqual(original, output)
            self.assertEqual(original.read_text(encoding="utf-8"), "")
            self.assertEqual(preview, "")
            self.assertEqual(output.read_text(encoding="utf-8"), "")

    def test_original_is_not_modified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "synthetic.log"
            original_text = "email=synthetic.user@example.test\n"
            original.write_text(original_text, encoding="utf-8")
            output, _, _ = redact_file(original)
            self.assertEqual(original.read_text(encoding="utf-8"), original_text)
            self.assertNotEqual(output.read_text(encoding="utf-8"), original_text)

    def test_refuses_same_output_and_damaged_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            broken = Path(directory) / "broken.log"
            broken.write_bytes(b"\xff")
            with self.assertRaisesRegex(InputError, "UTF-8"):
                redact_file(broken)
            good = Path(directory) / "good.log"
            good.write_text("synthetic", encoding="utf-8")
            with self.assertRaisesRegex(InputError, "different"):
                redact_file(good, good)
