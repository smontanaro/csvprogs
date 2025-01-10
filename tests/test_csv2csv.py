import csv
import io

from csvprogs.csv2csv import csv2csv

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
