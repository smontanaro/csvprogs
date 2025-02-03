#!/usr/bin/env python3

import subprocess

from tests import SPY_DAILY

EPS = 1e-7

def test_atr():
    # generate basic statistics, then feed into sharpe calc
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.mean",
        "-f", "Close-SPY", SPY_DAILY],
        stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0

    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.sharpe"],
        stdout=subprocess.PIPE, stderr=None, input=result.stdout)
    assert result.returncode == 0
    assert abs(float(result.stdout.decode("utf-8")) - 33.42458471637126) < EPS
