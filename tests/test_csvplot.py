import csv
import subprocess
import time

from matplotlib import pyplot
from csvprogs.csvplot import plot, Options
from tests import NVDA, VRTX_CSV

def test_plot():
    options = Options()
    options.fields = [["time", "last", "l", "red", "legend", "-", ""]]

    with open(NVDA, "r", encoding="utf-8") as inp:
        rdr = csv.DictReader(inp)
        plot(options, rdr, block=False)
        time.sleep(0.25)
        pyplot.close()

def test_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot",
            '-f', 'time,last,l,r', '-f', 'time,bid,r,b', "--noblock"],
            stdout=subprocess.PIPE, stderr=None, input=open(NVDA, "rb").read())
    assert result.returncode == 0

def test_cli_bg():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvplot",
            '-f', 'Date,Close,l,r', "-b", "Date,% Change,-1:+1,lightgreen", "--noblock"],
            stdout=subprocess.PIPE, stderr=None, input=open(VRTX_CSV, "rb").read())
    assert result.returncode == 0
