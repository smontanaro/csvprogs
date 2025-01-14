#!/usr/bin/env python3

import io
import subprocess

def test_atr():
    expected = open("tests/data/SPY-atr.csv", "rb").read()
    out = io.StringIO()
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.atr",
        "tests/data/SPY.csv"], stdout=subprocess.PIPE, stderr=None)
    assert result.stdout == expected
