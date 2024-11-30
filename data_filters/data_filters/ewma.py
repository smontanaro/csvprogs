#!/usr/bin/env python

"""
===========
{PROG}
===========

----------------------------------------------------
Compute exponentially weighted moving average
----------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  {PROG} [ -o name ] [ -f x ] [ -a val ] [ -s sep ] [ -m N ]

OPTIONS
=======

-a val   alpha of the ewma (default 0.1)
-f x     average the values in column x (no default)
-s sep   use sep as the field separator (default is comma)
-o name  define output column name (default: "ewma")
-m N     reset moving average after N missing values

DESCRIPTION
===========

Data are read from stdin, the ewma is computed, appended to the end of
the values, then printed to stdout.

SEE ALSO
========

* bars
* take
* mpl
* mvavg
"""


__all__ = ["ewma"]

import csv
import getopt
import math
import os
import sys

PROG = os.path.basename(sys.argv[0])

def ewma(rdr, field, outcol, alpha, gap):
    "core moving average calculation: outcol = ewma(field)"
    nan = float('nan')
    val = nan
    missing = 0
    result = []
    for row in rdr:
        if not row[field] or math.isnan(float(row[field])):
            missing += 1
            if missing >= gap:
                val = nan
        else:
            missing = 0
            if math.isnan(val):
                val = float(row[field])
            else:
                val = alpha * float(row[field]) + (1-alpha) * val
        if isinstance(field, str):
            row[outcol] = val
        else:
            row.append(val)
        result.append(row)
    return result

def main():
    opts, _args = getopt.getopt(sys.argv[1:], "a:f:s:o:m:h")

    alpha = 0.1
    field = None
    reader = csv.reader
    writer = csv.writer
    sep = ","
    outcol = "ewma"
    gap = 5
    for opt, arg in opts:
        if opt == "-a":
            alpha = float(arg)
        elif opt == "-o":
            outcol = arg
        elif opt == "-f":
            field = arg
        elif opt == "-s":
            sep = arg
        elif opt == "-m":
            gap = int(arg)
            assert gap > 0
        elif opt == "-h":
            usage()
            raise SystemExit

    if field is None:
        usage()
        return 1

    rdr = csv.DictReader(sys.stdin, delimiter=sep)
    fnames = rdr.fieldnames[:]
    fnames.append(outcol)
    wtr = csv.DictWriter(sys.stdout, delimiter=sep, fieldnames=fnames)
    wtr.writeheader()

    result = ewma(rdr, field, outcol, alpha, gap)
    wtr.writerows(result)
    return 0

def usage():
    print(__doc__.format(**globals()).strip(), file=sys.stderr)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, KeyboardInterrupt):
        sys.exit(0)
