#!/usr/bin/env python3

"usage..."

import csv
import datetime
import os
import subprocess
import sys
import tempfile

from csvprogs.common import usage, openi, as_days, ListyDict
from tests import RANDOM_CSV

INPUT = b"""\
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

EXPECTED = b"""\
time,close\r
2015-04-15T12:00,\r
2015-04-15T12:30,\r
2015-04-15T12:45,\r
2015-04-15T14:45,\r
2015-04-15T15:00,26.98\r
2015-04-16T09:30,\r
2015-04-16T15:00,27.04\r
2015-04-17T15:00,27.77\r
"""

EPS = 1e-7


def test_openio_stdin_stdout():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2csv",
        "-f", "time,close", "-n", "QUOTE_NONE"],
        input=INPUT, stdout=subprocess.PIPE, stderr=None)
    assert result.stdout == EXPECTED

def test_openio_files():
    (fd1, inf) = tempfile.mkstemp()
    (fd2, outf) = tempfile.mkstemp()
    try:
        f = os.fdopen(fd1, "wb")
        f.seek(0)
        f.write(INPUT)
        f.close()
        result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2csv",
            "-f", "time,close", "-n", "QUOTE_NONE", inf, outf])
        assert result.returncode == 0
        f = os.fdopen(fd2, "rb")
        f.seek(0)
        assert f.read() == EXPECTED
        f.close()
    finally:
        os.unlink(inf)
        os.unlink(outf)

def test_usage():
    usage_msg = usage(__doc__, globals(), msg="msg")
    assert "usage..." in usage_msg and "msg" in usage_msg

def test_openi():
    inf = tempfile.mktemp()
    try:
        with open(inf, "w") as fp1:
            fp1.write("hello\n")
        with openi(inf, "r") as fp2:
            assert not fp2.closed
        assert fp2.closed
    finally:
        os.unlink(inf)

def test_as_days():
    delta = datetime.timedelta(days=2, seconds=37000, microseconds=59)
    assert abs(as_days(delta) - 2.42824074) < EPS

def test_listy_dict():
    with open(RANDOM_CSV, encoding="ascii") as fp:
        rdr = csv.DictReader(fp)
        indexes = list(enumerate(rdr.fieldnames))
        for row in rdr:
            ld = ListyDict(row, indexes)
            assert ld.keys() == rdr.fieldnames
            assert len(ld) == 2
            assert "i" in ld
            for (i, k) in enumerate(iter(ld)):
                assert ld[i] == ld[k]
            ld["i"] = 2
            assert ld[0] == 2
            del ld["i"]
            assert "i" not in ld and 0 not in ld
