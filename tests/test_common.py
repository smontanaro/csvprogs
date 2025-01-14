#!/usr/bin/env python3

import atexit
import os
import subprocess
import tempfile

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

def test_openio_stdin_stdout():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2csv",
        "-f", "time,close", "-n" "QUOTE_NONE"],
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
            "-f", "time,close", "-n" "QUOTE_NONE", inf, outf])
        f = os.fdopen(fd2, "rb")
        f.seek(0)
        assert f.read() == EXPECTED
        f.close()
    finally:
        os.unlink(inf)
        os.unlink(outf)
