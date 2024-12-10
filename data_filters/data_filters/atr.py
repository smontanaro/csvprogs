#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
compute average true range metric
----------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2023-09-09
:Copyright: Skip Montanaro 2023
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -n val ] [ -s sep ] [ -o name ]

OPTIONS
=======

-n val   number of elements in the average (default 14)
-d name  column containing date/time (default "Date")
-c cols  columns for high,low,close (comma-separated, default: High,Low,Close)
-o name  name of output column (default "atr")
-s sep   use sep as the field separator (default is comma)

DESCRIPTION
===========

Data are read from stdin, the ATR is computed and appended
to the end of the values, then printed to stdout.

The ATR definition is from:

  https://www.investopedia.com/terms/a/atr.asp

SEE ALSO
========

* mvavg
* ewma
"""

import argparse
import csv
import os
import sys

import dateutil.parser

PROG = os.path.basename(sys.argv[0])

def main():
    parser = argparse.ArgumentParser(prog=f"{PROG}")
    parser.add_argument("--days", "-n", default=14,
                        help="length of the atr calculation")
    parser.add_argument("--outcol", "-o", default="atr",
                        help="Output column")
    parser.add_argument("--date", "-d", default="Date",
                        help="Date column")
    parser.add_argument("--columns", "-c", default="High,Low,Close",
                        help="columns containing high, low & close prices")
    parser.add_argument("--delimiter", "-s", default=",",
                        help="input and output field delimiter")
    args = parser.parse_args()

    outcol = args.outcol
    datecol = args.date
    length = args.days
    sep = args.delimiter
    cols = args.columns.split(",")
    assert len(cols) == 3

    date = None
    atrs = [None] * length
    high = low = close = None
    tr = None
    rdr = csv.DictReader(sys.stdin, delimiter=sep)
    fnames = rdr.fieldnames[:]
    fnames.append(outcol)
    wtr = csv.DictWriter(sys.stdout, delimiter=sep, fieldnames=fnames)
    wtr.writeheader()
    for row in rdr:
        if date is None:
            # first record, just save the close price
            close = float(row[cols[2]])
        else:
            high = float(row[cols[0]])
            low = float(row[cols[1]])
        date = dateutil.parser.parse(row[datecol]).date()
        if high is None:
            continue
        hl = high - low
        lc = abs(low - close)
        hc = abs(high - close)

        # today's close is tomorrow's prev close
        close = float(row[cols[2]])

        tr_today = max(hl, lc, hc)
        atrs.append(tr_today)
        atrs.pop(0)
        if None in atrs:
            continue
        if tr is None:
            tr = sum(atrs) / len(atrs)
        else:
            tr = (tr * (len(atrs) - 1) + tr_today) / len(atrs)
        row[outcol] = tr
        wtr.writerow(row)
    return 0

def usage(msg=None):
    if msg:
        print(msg, file=sys.stderr)
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main())
