#!/usr/bin/env python

"correlation tests"

import csv
import io
import subprocess

from tests import NVDA, RANDOM_CSV

EPS = 1e-7


def test_cli_c():
    result = subprocess.run(["python", "-m", "csvprogs.corr",
        "-f", "bid,ask", NVDA, "/dev/stdout"], check=True,
        stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0
    corr = float(result.stdout.strip())
    assert abs(corr - 0.98374687) < EPS

    result = subprocess.run(["python", "-m", "csvprogs.corr",
        "-f", "random,seq", RANDOM_CSV, "/dev/stdout"], check=True,
            stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0
    corr = float(result.stdout.strip())
    assert abs(corr - -0.206735) < EPS
