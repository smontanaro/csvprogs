import csv
import io
import subprocess

from dateutil.parser import parse as dtparse

from csvprogs.bars import generate_bars
from tests import NVDA


def test_generate_bars():
    outf = io.StringIO()
    with open(NVDA) as inf:
        rdr = csv.DictReader(inf)
        wtr = csv.DictWriter(outf, fieldnames=rdr.fieldnames+["bar"])
        wtr.writeheader()
        generate_bars(rdr, wtr, "time", "last", "bar", 3600)
    outf.seek(0)
    rdr = csv.DictReader(outf)
    last = 0.0
    for row in rdr:
        dt = dtparse(row["time"])
        if row["bar"]:
            assert last == float(row["bar"]), row["time"]
            assert dt.minute == dt.second == dt.microsecond == 0, row
        elif row["last"]:
            last = float(row["last"])

def test_cli_bars():
    out = io.StringIO()
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.bars",
        "-b", "1h", "-n" "bar", "-t", "time", "-p", "last", NVDA],
        stdout=subprocess.PIPE, stderr=None)
    rdr = csv.DictReader(io.StringIO(result.stdout.decode("utf-8")))
    last = 0.0
    for row in rdr:
        dt = dtparse(row["time"])
        if row["bar"]:
            assert last == float(row["bar"]), row["time"]
            assert dt.hour == 10
            return
        elif row["last"]:
            last = float(row["last"])

def test_cli_bars_append():
    out = io.StringIO()
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.bars",
        "-a", "-b", "1h", "-n" "bar", "-t", "time", "-p", "last", NVDA],
        stdout=subprocess.PIPE, stderr=None)
    pfx = result.stdout[0:5]
    assert pfx and pfx != b"time,"
