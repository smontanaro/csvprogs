#!/usr/bin/env python

import csv
import subprocess
import tempfile
import unittest

FIRST = """\
time,close\r
2015-04-15T15:00,26.98\r
2015-04-16T15:00,27.04\r
2015-04-17T15:00,27.77\r
"""

SECOND = """\
time,position\r
2015-04-15T12:00,1\r
2015-04-15T12:30,-1\r
2015-04-15T12:45,1\r
2015-04-15T14:45,-1\r
2015-04-16T09:30,1\r
"""

MERGED = b"""\
time,close,position\r
2015-04-15T12:00,,1\r
2015-04-15T12:30,,-1\r
2015-04-15T12:45,,1\r
2015-04-15T14:45,,-1\r
2015-04-15T15:00,26.98,\r
2015-04-16T09:30,,1\r
2015-04-16T15:00,27.04,\r
2015-04-17T15:00,27.77,\r
"""

FILLED = b"""\
time,close,position\r
2015-04-15T12:00,,1\r
2015-04-15T12:30,,-1\r
2015-04-15T12:45,,1\r
2015-04-15T14:45,,-1\r
2015-04-15T15:00,26.98,-1\r
2015-04-16T09:30,,1\r
2015-04-16T15:00,27.04,1\r
2015-04-17T15:00,27.77,1\r
"""

class _CSVTest(unittest.TestCase):
    def _merge_helper(self, first, second):
        with tempfile.NamedTemporaryFile(mode="w+") as file1:
            with tempfile.NamedTemporaryFile(mode="w+") as file2:
                file1.write(first)
                file2.write(second)
                file1.seek(0)
                file2.seek(0)
                result = subprocess.run(["./venv/bin/python", "-m",
                    "csvprogs.csvmerge", "-k", "time", file1.name, file2.name],
                    stdout=subprocess.PIPE, stderr=None)
                return result.stdout

class CSVMergeTest(_CSVTest):
    def test_merge(self):
        data = self._merge_helper(FIRST, SECOND)
        self.assertEqual(data, MERGED)

class CSVFillTest(_CSVTest):
    def test_fill(self):
        data = self._merge_helper(FIRST, SECOND).decode("ascii")
        with tempfile.NamedTemporaryFile(mode="w+") as merged:
            merged.file.write(data)
            merged.file.flush()
            result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvfill",
                "-k", "position", merged.name], stdout=subprocess.PIPE,
                stderr=None)
            self.assertEqual(result.stdout, FILLED)

if __name__ == "__main__":
    unittest.main()
