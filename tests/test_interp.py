#!/usr/bin/env python3

import io
import subprocess

from tests import SPY_DAILY


def test_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.interp",
        "-f", "Close-SPY", "-x", "Date", SPY_DAILY],
        stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0
