#!/usr/bin/env python

import csv
import tempfile
from test.support.script_helper import (spawn_python, kill_python)
import unittest

FIRST = [
    ["time", "close"],
    ["2015-04-15T15:00", "26.98"],
    ["2015-04-16T15:00", "27.04"],
    ["2015-04-17T15:00", "27.77"],
]

SECOND = [
    ["time", "position"],
    ["2015-04-15T12:00", "1"],
    ["2015-04-15T12:30", "-1"],
    ["2015-04-15T12:45", "1"],
    ["2015-04-15T14:45", "-1"],
    ["2015-04-16T09:30", "1"],
]

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
        with tempfile.NamedTemporaryFile(mode="w+") as first:
            with tempfile.NamedTemporaryFile(mode="w+") as second:
                writer = csv.writer(first.file)
                writer.writerows(FIRST)
                first.file.flush()
                writer = csv.writer(second.file)
                writer.writerows(SECOND)
                second.file.flush()
                p = spawn_python('src/csvprogs/csvmerge.py',
                                 '-k', 'time', first.name, second.name)
                return kill_python(p)

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
            p = spawn_python('src/csvprogs/csvfill.py',
                             '-k', 'position', merged.name)
            data = kill_python(p)
            self.assertEqual(data, FILLED)

if __name__ == "__main__":
    unittest.main()
