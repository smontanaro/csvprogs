#!/usr/bin/env python

import subprocess

from tests import FIRST, SECOND, MERGED, SECOND_SHORT, MERGED_SHORT, EMPTY

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

def test_merge_empty():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvmerge",
        "-k", "time", FIRST, EMPTY], stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0
    with open(FIRST, "rb") as merged:
        assert result.stdout.replace(b"\r\n", b"\n") == merged.read()

def test_merge_short():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvmerge",
        "-k", "time", FIRST, SECOND_SHORT], stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0
    with open(MERGED_SHORT, "rb") as merged:
        assert result.stdout == merged.read()
