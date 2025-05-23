#!/usr/bin/env python

import csv
import io
import os.path
import subprocess
import tempfile

import pytest

from tests import RANDOM_CSV, VRTX_CSV


MODSTRING = """
from datetime import datetime, timedelta

def xform(row):
    t = datetime.strptime(row["time"], "%Y-%m-%dT%H:%M")
    pre_t = t - timedelta(seconds=1)
    pre = [{"time": pre_t.strftime("%Y-%m-%dT%H:%M:%S"),
            "close": row["close"] - 0.01}]
    return (pre, [])
"""


XFORMSTRING = """

def func1(row):
    import datetime, dateutil.parser
    t = dateutil.parser.parse(row["Date"])
    pre_t = t - datetime.timedelta(seconds=1)
    pre = [{"Date": pre_t.strftime("%Y-%m-%dT%H:%M:%S"),
            "OClose": row["Close"],
            "Close": row["Close"] - 0.01}]
    return (pre, [])

def func2(row):
    import datetime, dateutil.parser
    t = dateutil.parser.parse(row["Date"])
    pre_t = t - datetime.timedelta(seconds=1)
    pre = [{"Date": pre_t.strftime("%Y-%m-%dT%H:%M:%S"),
            "OClose": row["Close"],
            "Close": row["Close"] - 0.1}]
    return (pre, [])

__xform__ = "func2"
__xform_names__ = ["OClose"]
"""


CALLSTRING = """
from datetime import datetime, timedelta

class XForm:
    def __call__(self, row):
        t = datetime.strptime(row["time"], "%Y-%m-%dT%H:%M")
        pre_t = t - timedelta(seconds=1)
        pre = [{"time": pre_t.strftime("%Y-%m-%dT%H:%M:%S"),
                "close": row["close"] - 0.01}]
        return (pre, [])
xform = XForm()
"""

METHSTRING = """
from datetime import datetime, timedelta

class XForm:
    def xform(self, row):
        t = datetime.strptime(row["time"], "%Y-%m-%dT%H:%M")
        pre_t = t - timedelta(seconds=1)
        pre = [{"time": pre_t.strftime("%Y-%m-%dT%H:%M:%S"),
                "close": row["close"] - 0.01}]
        return (pre, [])
xf = XForm()
xform = xf.xform
"""


@pytest.mark.parametrize(("xstring",),
                         [(MODSTRING,), (CALLSTRING,), (METHSTRING,),])
def test_basic_xform(xstring):
    input_list = [
        ["time", "close"],
        ["2015-04-15T15:00", "26.98"],
        ["2015-04-16T15:00", "27.04"],
        ["2015-04-17T15:00", "27.77"],
    ]

    expected = b"""\
time,close,name1,name2\r
2015-04-15T14:59:59,26.97,,\r
2015-04-15T15:00,26.98,,\r
2015-04-16T14:59:59,27.029999999999998,,\r
2015-04-16T15:00,27.04,,\r
2015-04-17T14:59:59,27.759999999999998,,\r
2015-04-17T15:00,27.77,,\r
"""

    inp = io.StringIO()
    writer = csv.writer(inp)
    writer.writerows(input_list)
    raw_input = inp.getvalue()
    with tempfile.NamedTemporaryFile(mode="w+", dir="/tmp",
                                     suffix=".py") as xfile:
        xfile.file.write(xstring)
        xfile.file.flush()
        xfile.seek(0)
        modname = os.path.splitext(os.path.split(xfile.name)[1])[0]
        env = dict(os.environ)
        env["PYTHONPATH"] = "/tmp"
        result = subprocess.run(
            [
             "./venv/bin/python", "-m",
             "csvprogs.xform",
             "-F", f"{modname}.xform",
             "-p", "sample_global=1.0",
             "-c", "name1,name2",
            ],
            env=env, stdout=subprocess.PIPE, stderr=None,
            input=bytes(raw_input, encoding="utf-8"))
        assert result.stdout == expected


def test_f_xform():
    with open(VRTX_CSV, "rb") as f:
        data = f.read()
        result = subprocess.run(
            [
             "./venv/bin/python", "-m",
             "csvprogs.xform",
             "-f", XFORMSTRING,
             "-p", "sample_global=1.0",
            ],
            stdout=subprocess.PIPE, stderr=None, input=data)
        assert result.returncode == 0

def test_extra_f():
    with tempfile.NamedTemporaryFile(mode="w+", dir="/tmp",
                                     suffix=".py") as xfile:
        xfile.file.write(MODSTRING)
        xfile.file.flush()
        xfile.seek(0)
        modname = os.path.splitext(os.path.split(xfile.name)[1])[0]
        result = subprocess.run(
            [
             "./venv/bin/python", "-m",
             "csvprogs.xform",
             "-F", f"{modname}.xform",
             "-f", "lambda row: row['i']",
             "-p", "sample_global=1.0",
             RANDOM_CSV,
            ],
            stdout=subprocess.PIPE, stderr=None)
        assert result.stdout != 0

def test_missing_xform():
    result = subprocess.run(
        [
         "./venv/bin/python", "-m",
         "csvprogs.xform",
         "-p", "sample_global=1.0",
         RANDOM_CSV,
                            ],
        stdout=subprocess.PIPE, stderr=None)
    assert result.stdout != 0
