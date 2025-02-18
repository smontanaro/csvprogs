import csv
import io
import os
import subprocess
import sys
import tempfile

from csvprogs.csvplot import plot, Options
from tests import NVDA, VRTX_CSV, RANDOM_CSV

def test_plot():
    fd, fname = tempfile.mkstemp()
    try:
        options = Options()
        options.fields = [["time", "last", "l", "red", "legend", "-", ""]]
        options.x_label = "X axis label"
        options.block = False
        options.plot_file = fname
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
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot", "-l", "legend",
        '-f', 'time,last,l,r', '-f', 'time,bid,r,b', "--noblock", "--left_label", "left",
        "--right_label", "right", "-b", "time,last,135.07,lightgreen",
        "-Y", "0:100,0:100",
        "--format", "%Y-%m", NVDA],
        stdout=subprocess.PIPE, stderr=None, env=env)
    assert result.returncode == 0

def test_cli_nondate():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot",
        '-f', 'i,random', "--noblock", "--format", '%.0f',
        "-Y", "0:1", "-X", "0:10",
        RANDOM_CSV],
        stdout=subprocess.PIPE, stderr=None)
    assert result.returncode == 0

def test_cli_bg():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot", "-L",
        "--verbose", '-f', 'Date,Close,l,r', "-b", "Date,% Change,-1:+1,lightgreen",
        "--noblock", "--right_label", "right", "-B", "Agg", "--xkcd",
        "-X", "2025-01-02T06:00:00.000Z,today",
        VRTX_CSV],
        stdout=subprocess.PIPE, stderr=None)
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
