#!/usr/bin/env python

import datetime

from data_filters.square import square

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
    result = list(square(iter(rows), ["time"]))
    assert result == exp_rows, result

def test_empty_square():
    rows = []
    exp_rows = []
    result = list(square(iter(rows), ["y"]))
    assert result == exp_rows, result
