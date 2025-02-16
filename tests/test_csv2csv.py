import csv
import io
import subprocess
import sys

from csvprogs.csv2csv import csv2csv, QuoteAction
from tests import NVDA

INPUT = """\
time,close,position\r
2015-04-15T12:00,,1\r
2015-04-15T12:30,,-1\r
2015-04-15T12:45,,1\r
2015-04-15T14:45,,-1\r
2015-04-15T15:00,26.98,\r
2015-04-16T09:30,,1\r
2015-04-16T15:00,27.04,\r
2015-04-17T15:00,27.77,\r
"""

COMMA_EXPECTED = """\
time,close\r
2015-04-15T12:00,\r
2015-04-15T12:30,\r
2015-04-15T12:45,\r
2015-04-15T14:45,\r
2015-04-15T15:00,26.98\r
2015-04-16T09:30,\r
2015-04-16T15:00,27.04\r
2015-04-17T15:00,27.77\r
"""

TAB_EXPECTED = """\
time\tclose\tposition\r
2015-04-15T12:00\t\t1\r
2015-04-15T12:30\t\t-1\r
2015-04-15T12:45\t\t1\r
2015-04-15T14:45\t\t-1\r
2015-04-15T15:00\t26.98\t\r
2015-04-16T09:30\t\t1\r
2015-04-16T15:00\t27.04\t\r
2015-04-17T15:00\t27.77\t\r
"""

def test_csv2csv():
    rdr = csv.DictReader(io.StringIO(INPUT))
    out = io.StringIO()
    wtr = csv.DictWriter(out, fieldnames=["time", "close"])
    wtr.writeheader()
    csv2csv(rdr, wtr, wtr.fieldnames)
    assert out.getvalue() == COMMA_EXPECTED

    rdr = csv.DictReader(io.StringIO(INPUT))
    out = io.StringIO()
    wtr = csv.DictWriter(out, delimiter="\t", fieldnames=rdr.fieldnames)
    wtr.writeheader()
    csv2csv(rdr, wtr, wtr.fieldnames)
    assert out.getvalue() == TAB_EXPECTED

def test_new_quotes():
    if sys.version_info.minor >= 12:
        assert "NOTNULL" in QuoteAction.quotes
    else:
        assert "NOTNULL" not in QuoteAction.quotes

def test_append():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2csv",
        "-a", NVDA], stdout=subprocess.PIPE, stderr=None)
    rdr = csv.DictReader(io.StringIO(result.stdout.decode("utf-8")))
    assert rdr.fieldnames != ["time", "ask", "bid", "last"]

    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2csv",
        NVDA], stdout=subprocess.PIPE, stderr=None)
    rdr = csv.DictReader(io.StringIO(result.stdout.decode("utf-8")))
    assert rdr.fieldnames == ["time", "ask", "bid", "last"]

def test_bad_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csv2csv",
        "-a", NVDA, NVDA, NVDA], stdout=subprocess.PIPE, stderr=None)
    assert result.returncode != 0
