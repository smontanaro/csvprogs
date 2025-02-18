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

import csv
import os
import sys

import dateutil.parser

from csvprogs.common import CSVArgParser, openpair, usage

PROG = os.path.basename(sys.argv[0])

def main():
    parser = CSVArgParser(prog=f"{PROG}", usage=usage(__doc__, globals()))
    parser.add_argument("--days", "-n", default=14,
                        help="length of the atr calculation")
    parser.add_argument("--outcol", default="atr",
                        help="Output column")
    parser.add_argument("--date", "-d", default="Date",
                        help="Date column")
    parser.add_argument("--columns", "-c", default="High,Low,Close",
                        help="columns containing high, low & close prices")
    (options, args) = parser.parse_known_args()

    outcol = options.outcol
    datecol = options.date
    length = options.days
    insep = options.insep
    outsep = options.outsep
    cols = options.columns.split(",")
    assert len(cols) == 3

    date = None
    atrs = [None] * length
    high = low = close = None
    tr = None
    with openpair(options, args) as (inf, outf):
        rdr = csv.DictReader(inf, delimiter=insep)
        fnames = rdr.fieldnames[:]
        fnames.append(outcol)
        wtr = csv.DictWriter(outf, delimiter=outsep, fieldnames=fnames)
        if not options.append:
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
            if None not in atrs:
                if tr is None:
                    tr = sum(atrs) / len(atrs)
                else:
                    tr = (tr * (len(atrs) - 1) + tr_today) / len(atrs)
                row[outcol] = tr
            wtr.writerow(row)
    return 0

if __name__ == "__main__":
    try:
        result = main()
    except BrokenPipeError:
        result = 0
    sys.exit(result)
