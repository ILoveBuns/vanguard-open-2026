import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from validate_package import validate  # noqa: E402


class ValidatePackageTests(unittest.TestCase):
    def test_current_package_passes(self):
        result = validate()
        self.assertLessEqual(result["main_words"], 2500)
        self.assertLessEqual(result["rationale_words"], 300)
        self.assertGreater(result["pdf_pages"], 0)

    def test_rejects_placeholder_identity(self):
        source = Path("entry.md").read_text()
        with tempfile.TemporaryDirectory() as directory:
            entry = Path(directory) / "entry.md"
            entry.write_text(source.replace("- Name: Ren Yi", "- Name: TODO"))
            with self.assertRaisesRegex(ValueError, "incomplete entrant fields"):
                validate(entry, Path("the-classroom-with-no-attention-score.pdf"))


if __name__ == "__main__":
    unittest.main()
