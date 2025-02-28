#!/usr/bin/env python

"ewma tests"

import csv
import io
import math
import subprocess

from csvprogs.ewma import ewma

EPS = 1e-7

INPUT = """\
date,weight,hr,O2
2024-09-07,179.8,50,95
2024-09-08,180.4,48,96
2024-09-09,181.4,51,96
2024-09-10,182.8,54,93
2024-09-11,180.8,53,95
2024-09-12,182.0,47,95
2024-09-13,182.6,51,96
2024-09-14,182.4,53,94
2024-09-15,
2024-09-16,181.8,53,94
2024-09-17,181.8,57,96
2024-09-18,183.4
2024-09-19,183.6
2024-09-20,185.4,55,95
2024-09-21,184.8,48,95
2024-09-22,183.0,53,96
2024-09-23,184.0
2024-09-24,182.0,52,96
2024-09-25,182.8,53,95
2024-09-26,180.8,50,94
2024-09-27,182.6
2024-09-28,183.6,48,96
2024-09-29,
2024-09-30,
2024-10-01,
2024-10-02,
2024-10-03,
2024-10-04,
2024-10-05,
2024-10-06,
2024-10-07,
2024-10-08,
2024-10-09,
2024-10-10,
2024-10-11,
2024-10-12,
2024-10-13,
2024-10-14,
2024-10-15,
2024-10-16,
2024-10-17,
2024-10-18,
2024-10-19,
2024-10-20,
2024-10-21,
2024-10-22,
2024-10-23,182
2024-10-24,183.8,55,96
2024-10-25,181.0,51,96
2024-10-26,181.0,51,97
2024-10-27,181.0,55,96
2024-10-28,182.8,52,96
2024-10-29,183.2,49,96
2024-10-30,182.6,52,95
2024-10-31,182.8,53,94
2024-11-01,182.6,48,94
2024-11-02,183.6,48,95
2024-11-03,182.6
2024-11-04,181.0,56
2024-11-05,180.6,59
2024-11-06,181.6,53
2024-11-07,182.8,45
2024-11-08,182.0,49
2024-11-09,181.8,48
2024-11-10,182.0,46
2024-11-11,183.0,45
2024-11-12,181.8,46
"""

def test_basic_ewma():
    input_file = io.StringIO(INPUT)
    rdr = csv.DictReader(input_file)
    result = ewma(rdr, "weight", "ewma", 0.1, 1)
    assert math.isnan(result[8]["ewma"])

    input_file.seek(0)
    rdr = csv.DictReader(input_file)
    result = ewma(rdr, "weight", "ewma", 0.1, 2)
    assert not math.isnan(result[8]["ewma"])

def test_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.ewma",
        "-f", "weight"], check=True,
        stdout=subprocess.PIPE, stderr=None,
        input=bytes(INPUT, encoding="utf-8"))
    rdr = list(csv.DictReader(io.StringIO(result.stdout.decode("utf-8"))))
    assert rdr[8]["ewma"] != "nan"

def test_bad_gap():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.ewma",
        "-f", "weight", "--gap=-1"], check=False,
        stdout=subprocess.PIPE, stderr=None,
        input=bytes(INPUT, encoding="utf-8"))
    assert result.returncode != 0

def test_trailing_blanks():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.ewma",
        "-f", "O2", "--gap=5"], check=False,
        stdout=subprocess.PIPE, stderr=None,
        input=bytes(INPUT, encoding="utf-8"))
    assert result.returncode == 0
    rdr = csv.DictReader(io.StringIO(result.stdout.decode("utf-8")))
    dates = {row["date"]: row for row in rdr}
    assert float(dates["2024-11-02"]["ewma"]) - 95.53292969 < EPS
    assert dates["2024-11-03"]["ewma"] == ""
