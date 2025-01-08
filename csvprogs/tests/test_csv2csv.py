import csv
import io

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

def test_csv2csv():
    inp = csv.DictReader(io.StringIO(INPUT))
    out = csv.DictWriter(io.StringIO(), fieldnames=["time", "close"])
    csvprogs.csv2csv.csv2csv(inp, out, out.fieldnames)
    assert out.getvalue() == COMMA_EXPECTED

    inp = csv.DictReader(io.StringIO(INPUT))
    out = csv.DictWriter(io.StringIO(), delimiter="\t", fieldnames=inp.fieldnames)
    csvprogs.csv2csv.csv2csv(inp, out, inp.fieldnames)
    assert out.getvalue() == TAB_EXPECTED
