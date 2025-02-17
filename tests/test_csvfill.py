#!/usr/bin/env python

import subprocess
import tempfile
import unittest

from tests import NVDA, FIRST, SECOND, MERGED, FILLED

class _CSVTest(unittest.TestCase):
    def _merge_helper(self, first, second):
        result = subprocess.run(["./venv/bin/python", "-m",
            "csvprogs.csvmerge", "-k", "time", first, second],
            stdout=subprocess.PIPE, stderr=None)
        return result.stdout

class CSVFillTest(_CSVTest):
    def test_fill(self):
        data = self._merge_helper(FIRST, SECOND).decode("ascii")
        with tempfile.NamedTemporaryFile(mode="w+") as merged:
            merged.file.write(data)
            merged.file.flush()
            result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvfill",
                "-k", "position", merged.name], stdout=subprocess.PIPE,
                stderr=None)
            with open(FILLED, "rb") as filled:
                self.assertEqual(result.stdout, filled.read())

def test_bad_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvfill",
        "-k", "date", NVDA, NVDA, NVDA], stdout=subprocess.PIPE, stderr=None)
    assert result.returncode != 0

if __name__ == "__main__":
    unittest.main()
