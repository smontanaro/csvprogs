#!/usr/bin/env python

"regress tests"

import csv
import io
import subprocess

from tests import NVDA

EPS = 1e-7


def test_cli_c():
    with open(NVDA, "rb") as nvda:
        raw_input = nvda.read()
        result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.regress",
            "-f", "bid,ask", "--corr", NVDA, "/dev/stdout"], check=True,
            stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0
    corr = float(result.stdout.strip())
    assert abs(corr - 0.98374687) < EPS

def test_cli_csv():
    with open(NVDA, "rb") as nvda:
        result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.regress",
            "-f", "bid,ask", "--column", "reg", "--verbose"], check=True,
            stdout=subprocess.PIPE, stderr=None,
            input=nvda.read())
    assert result.returncode == 0
    output = list(csv.DictReader(io.StringIO(result.stdout.decode("utf-8"))))
    assert (abs(float(output[7]["reg"]) - 135.4728217) < EPS and
            abs(float(output[-1]["reg"]) - 137.7006059) < EPS)
