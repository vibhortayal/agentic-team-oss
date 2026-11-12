import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wc import count_words  # noqa: E402

WC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wc.py")


class CountWords(unittest.TestCase):
    def test_counts_words(self):
        self.assertEqual(count_words("one two  three\nfour"), 4)

    def test_empty_text_has_no_words(self):
        self.assertEqual(count_words(""), 0)

    def test_cli_prints_the_count(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("a b c")
        out = subprocess.run([sys.executable, WC, f.name], capture_output=True, text=True)
        os.unlink(f.name)
        self.assertEqual(out.stdout.strip(), "3")


if __name__ == "__main__":
    unittest.main()
