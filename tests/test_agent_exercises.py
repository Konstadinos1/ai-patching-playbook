"""Exercise the reviewer CLI with synthetic records only."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "exercises" / "review.py"


class ReviewTests(unittest.TestCase):
    def run_reader(self, *args: str) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as directory:
            return subprocess.run(
                [sys.executable, str(SCRIPT), *args],
                cwd=directory,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=5,
            )

    def test_default_displays_all_cases_without_answers(self):
        result = self.run_reader()
        self.assertEqual(result.returncode, 0, result.stderr)
        for case_id in "ABCDE":
            self.assertIn(f"\n{case_id}. ", result.stdout)
        self.assertNotIn("Answer:", result.stdout)

    def test_judgments_match_case_evidence(self):
        expected = {"A": "denied", "B": "unknown", "C": "violation",
                    "D": "completed", "E": "completed"}
        for case_id, answer in expected.items():
            with self.subTest(case=case_id):
                result = self.run_reader(case_id, "--answer", answer)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"Answer: {answer}.", result.stdout)
                self.assertIn("Correct.", result.stdout)

    def test_denial_on_one_path_does_not_erase_disclosure(self):
        result = self.run_reader("C", "--answer", "denied")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Answer: violation.", result.stdout)

    def test_full_key_and_invalid_input(self):
        key = self.run_reader("--key")
        self.assertEqual(key.returncode, 0, key.stderr)
        self.assertEqual(key.stdout.count("Answer:"), 5)
        for args in (("--answer", "unknown"), ("Z",), ("B", "--answer", "other")):
            with self.subTest(args=args):
                self.assertEqual(self.run_reader(*args).returncode, 2)


if __name__ == "__main__":
    unittest.main()
