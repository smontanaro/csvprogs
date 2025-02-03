#!/usr/bin/env python3

import io
import subprocess

from tests import SPY_CSV


def test_atr():
    expected = open("tests/data/SPY-atr.csv", "rb").read()
    out = io.StringIO()
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.atr",
        "-c", "High,Low,Close", SPY_CSV],
        stdout=subprocess.PIPE, stderr=None)
    assert result.stdout == expected
