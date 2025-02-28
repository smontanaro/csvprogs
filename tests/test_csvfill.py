#!/usr/bin/env python

import subprocess
import tempfile

from tests import NVDA, FIRST, SECOND, MERGED, FILLED

def merge_helper(first, second):
    result = subprocess.run(["./venv/bin/python", "-m",
        "csvprogs.csvmerge", "-k", "time", first, second],
        stdout=subprocess.PIPE, stderr=None)
    return result.stdout

def test_fill():
    data = merge_helper(FIRST, SECOND).decode("ascii")
    with tempfile.NamedTemporaryFile(mode="w+") as merged:
        merged.file.write(data)
        merged.file.flush()
        result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvfill",
            "-k", "position", merged.name], stdout=subprocess.PIPE,
            stderr=None)
        with open(FILLED, "rb") as filled:
            assert result.stdout == filled.read()

def test_bad_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvfill",
        "-k", "date", NVDA, NVDA, NVDA], stdout=subprocess.PIPE, stderr=None)
    assert result.returncode != 0
