#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
compute hull moving averages
----------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2021-04-19
:Copyright: TradeLink LLC 2013
:Copyright: Skip Montanaro 2021
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -f x ] [ -n val ] [ -s sep ] [ -o name ]

OPTIONS
=======

-n val   number of elements in the moving average (default 30)
-f x     average the values in column x (name, no default)
-o name  name of output column (default "hull")
-s sep   use sep as the field separator (default is comma)

DESCRIPTION
===========

Data are read from stdin, the hull moving average is computed and
appended to the end of the values, then printed to stdout.

The formula used is from:

  https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/hull-moving-average

The above page doesn't describe whether to truncate or round sqrt(n),
so I've chosen to round.  For n == 10, we choose 3, for n == 15, we
choose 4.


SEE ALSO
========

* mvavg

"""

from contextlib import suppress
import csv
import getopt
import math
import os
import sys


PROG = os.path.basename(sys.argv[0])

def main():
    opts, args = getopt.getopt(sys.argv[1:], "n:f:s:o:h")

    outcol = "hull"
    length = 30
    field = None
    sep = ","
    for opt, arg in opts:
        if opt == "-n":
            length = int(arg)
        elif opt == "-f":
            field = arg
        elif opt == "-s":
            sep = arg
        elif opt == "-o":
            outcol = arg
        elif opt == "-h":
            usage()
            return 0

    if field is None:
        usage("field name is required.")
        return 1

    rdr = csv.DictReader(sys.stdin, delimiter=sep)
    fnames = rdr.fieldnames[:]
    fnames.append(outcol)
    wtr = csv.DictWriter(sys.stdout, delimiter=sep, fieldnames=fnames)
    wtr.writeheader()
    coeffs = list(range(length, 0, -1))
    half = length // 2
    sqrt_len = int(round(math.sqrt(length)))
    # values correspond to raw data, wma(n), wma(n/2), hull(n).
    # Values for wma(n), wma(n/2) and hull(n) are only computed when
    # the raw data fills up enough to eliminate the None values in the
    # raw data.
    values = [
        [None] * length,        # raw inputs, appended to end
        [None] * length,        # wma(n)
        [None] * length,        # wma(n/2)
        [None] * length,        # 2 * wma(n/2) - wma(n)
    ]
    for row in rdr:
        val = ""
        if row[field]:
            values[0].append(float(row[field]))
            del values[0][0]
            if None not in values[0]:
                # wma(n)
                values[1].append(wma(values[0], coeffs))
                del values[1][0]
                # wma(n/2)
                values[2].append(wma(values[0][-half:], coeffs[-half:]))
                del values[2][0]
                # 2 * wma(n/2) - wma(n)
                values[3].append(2 * values[2][-1] - values[1][-1])
                del values[3][0]
                vals = values[3][-sqrt_len:]
                if None not in vals:
                    val = wma(vals, coeffs[-sqrt_len:])
        row[outcol] = val
        wtr.writerow(row)
    return 0

def wma(elts, coeffs):
    num = sum(c * e for (c, e) in zip(coeffs, elts))
    den = sum(coeffs[:len(elts)])
    return num / den

def usage(msg=None):
    if msg:
        print(msg, file=sys.stderr)
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    with suppress((BrokenPipeError,)):
        sys.exit(main())
