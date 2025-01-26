#!/usr/bin/env python

import datetime
import subprocess

from csvprogs.square import square, remove_dups
from tests import NVDA


def test_dict_square():
    rows = [
        {
            "time": "2010-01-01T00:00:00",
            "y": 1.90,
            },
        {
            "time": "2010-01-01T00:00:01",
            "y": 1.94,
            },
        {
            "time": "2010-01-01T00:00:02",
            "y": 1.88,
            },
        {
            "time": "2010-01-01T00:00:03",
            "y": 1.90,
            },
        ]
    exp_rows = [
        {
            "time": "2010-01-01T00:00:00",
            "y": 1.90,
            },
        {
            "time": "2010-01-01T00:00:01",
            "y": 1.90,
            },
        {
            "time": "2010-01-01T00:00:01",
            "y": 1.94,
            },
        {
            "time": "2010-01-01T00:00:02",
            "y": 1.94,
            },
        {
            "time": "2010-01-01T00:00:02",
            "y": 1.88,
            },
        {
            "time": "2010-01-01T00:00:03",
            "y": 1.88,
            },
        {
            "time": "2010-01-01T00:00:03",
            "y": 1.90,
            },
        ]
    result = list(square(remove_dups(iter(rows), "time", ["y"]), "time", ["y"]))
    assert result == exp_rows, result

def test_empty_square():
    rows = []
    exp_rows = []
    result = list(square(iter(rows), "time", ["y"]))
    assert result == exp_rows, result

def test_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.square",
        "-a", NVDA], stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0
