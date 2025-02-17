#!/usr/bin/env python

import subprocess

from tests import FIRST, SECOND, MERGED

def test_bad_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvmerge",
        "-k", "date,time"], stdout=subprocess.PIPE, stderr=None)
    assert result.returncode != 0

def test_merge():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvmerge",
        "-k", "time", FIRST, SECOND], stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0
    with open(MERGED, "rb") as merged:
        assert result.stdout == merged.read()
