#!/usr/bin/env python

import datetime
import csv
from cStringIO import StringIO

from xform import xform

def test_basic_xform():
    inp = StringIO("""time,close
2015-04-15T15:00,26.98
2015-04-16T15:00,27.04
2015-04-17T15:00,27.77
""")
    outp = StringIO()
    rdr = csv.DictReader(inp, lineterminator="\n")
    wtr = csv.DictWriter(outp, rdr.fieldnames, lineterminator="\n")
    wtr.writeheader()

    def f(row):
        t = datetime.datetime.strptime(row["time"], "%Y-%m-%dT%H:%M")
        pre_t = t - datetime.timedelta(seconds=1)
        pre = [{"time": pre_t.strftime("%Y-%m-%dT%H:%M:%S"),
                "close": row["close"] - 0.01}]
        return (pre, [])

    xform(rdr, wtr, f, enumerate(rdr.fieldnames))

    exp = """time,close
2015-04-15T14:59:59,26.97
2015-04-15T15:00,26.98
2015-04-16T14:59:59,27.03
2015-04-16T15:00,27.04
2015-04-17T14:59:59,27.76
2015-04-17T15:00,27.77
"""

    outp = outp.getvalue()
    assert exp == outp, (exp, outp)
