import csv
import io
import os
import subprocess
import sys
import tempfile

from csvprogs.csvplot import plot, Options
from tests import (NVDA, VRTX_CSV, RANDOM_CSV, BAD_DATE_1, BAD_DATE_2, EMPTY,
                   WEIGHT_CSV,)

def test_plot():
    fd, fname = tempfile.mkstemp()
    try:
        options = Options()
        options.fields = [["time", "last", "l", "red", "legend", "-", ""]]
        options.x_label = "X axis label"
        options.block = False
        options.plot_file = fname
        options.title = "test_plot"
        with open(NVDA, "r", encoding="utf-8") as inp:
            rdr = csv.DictReader(inp)
            plot(options, rdr, block=False)
    finally:
        os.close(fd)
        os.unlink(fname)

def test_cli():
    env = os.environ.copy()
    try:
        del env["DISPLAY"]
    except KeyError:
        pass
    for xrange in ("2019-01-01:2025-01-20", # > 5 years
                   "2021-01-01:2025-01-20", # > 2 years
                   "2023-01-01:2024-07-10", # > 1.5 years
                   "2025-01-17T08:30,2025-01-17T08:32", # < 10 minutes
                   "2025-01-17T08:30,2025-01-17T10:07", # < two hours
                   "today", # one day
                   "yesterday", # one day
    ):
        result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot",
            "-l", "legend", '-f', 'time,last,l,r', '-f', 'time,bid,r,b',
            "--noblock", "--left_label", "left", "--right_label", "right",
            "-b", "time,last,135.07,lightgreen", "-Y", "0:100,0:100",
            "-X", xrange, "-T", "test_cli", NVDA],
            stdout=subprocess.PIPE, stderr=None, env=env)
        assert result.returncode == 0

def test_cli_nondate():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot",
        '-f', 'i,random', "--noblock", "--format", '%.0f',
        "-Y", "0:1", "-X", "0:10", "-T", "test_cli_nondate",
        RANDOM_CSV],
        stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0

def test_missing_yval():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot",
        '-f', 'date,weight', "--noblock", "-X", "2025-01-01,yesterday",
        WEIGHT_CSV],
        stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0

def test_cli_bg():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot",
        "-L", "--verbose", '-f', 'Date,Close,l,r,_Close,-/3,;/2',
        "-b", "Date,% Change,-1:+1,lightgreen",
        "--noblock", "--right_label", "right", "-B", "Agg", "--xkcd",
        "-X", "2025-01-02T06:00:00.000Z,today", "-T", "test_cli_bg",
        VRTX_CSV],
        stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0

def test_bad_date_1():
    # two paths through bad date land, one we can recover from, one we can't.
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot",
        '-f', 'time,close', "-T", "test_bad_date_1", BAD_DATE_1],
        stdout=subprocess.PIPE, stderr=None)
    assert result.returncode != 0

def test_bad_date_2():
    # we know how to recover from invalid leap year dates.
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot",
        '-f', 'time,close', "-T", "test_bad_date_2", "--noblock", BAD_DATE_2],
        stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0

def test_bad_x_range():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot",
        '-f', 'time,last,l,r', "-X", "yesterday,today,today", NVDA],
        stdout=subprocess.PIPE, stderr=None)
    assert result.returncode != 0

def test_empty():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot",
        '-f', 'time,close', "--noblock", EMPTY],
        stdout=subprocess.PIPE, stderr=None)
    assert result.returncode != 0

def test_only_right_y():
    env = os.environ.copy()
    try:
        del env["DISPLAY"]
    except KeyError:
        pass
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot",
        '-f', 'time,bid,r,b', "--noblock", "--x_label", "x", NVDA],
        stdout=subprocess.PIPE, stderr=None, env=env)
    assert result.returncode == 0

def test_options():
    options = Options()
    save_stderr = sys.stderr
    try:
        sys.stderr = err = io.StringIO()
        options.debug_print()
        assert "sep: ," in err.getvalue()
    finally:
        sys.stderr = save_stderr
