#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
compute moving averages
----------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Copyright: Skip Montanaro 2016-2021
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -f x ] [ -n val ] [ -s sep ] [ -o name ]

OPTIONS
=======

-n val   number of elements in the moving average (default 5)
-f x     average the values in column x (name, no default)
-o name  name of output column (default "mean" unless -w is given,
         in which case the default is "wma")
-s sep   use sep as the field separator (default is comma)
-w       weight the values, providing more weight to more recent values

DESCRIPTION
===========

Data are read from stdin, the moving average is computed and appended
to the end of the values, then printed to stdout.

The weighted moving average formula used is from:

  https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/wma

SEE ALSO
========

* pt
* bars
* ptwin
* take
* mpl
"""

import sys
import getopt
import os
import csv

PROG = os.path.basename(sys.argv[0])

def main():
    opts, args = getopt.getopt(sys.argv[1:], "n:f:s:o:hw")

    outcol = ""
    weighted = False
    length = 5
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
        elif opt == "-w":
            weighted = True
        elif opt == "-h":
            usage()
            return 0

    if field is None:
        usage("field name is required.")
        return 1

    nan = float('nan')
    outcol = outcol if outcol else ("wma" if weighted else "mean")
    elts = [None] * length
    rdr = csv.DictReader(sys.stdin, delimiter=sep)
    fnames = rdr.fieldnames[:]
    fnames.append(outcol)
    wtr = csv.DictWriter(sys.stdout, delimiter=sep, fieldnames=fnames)
    wtr.writeheader()
    coeffs = [1] * length if not weighted else list(range(length, 0, -1))
    for row in rdr:
        if row[field]:
            elts.append(float(row[field]))
            del elts[0]
        else:
            # restart mv avg calc
            elts = [None] * length
        if None not in elts:
            val = avg(elts, coeffs)
        else:
            val = nan
        row[outcol] = val
        wtr.writerow(row)
    return 0

def avg(elts, coeffs):
    num = sum([c * e for (c, e) in zip(coeffs, elts)])
    den = sum(coeffs[:len(elts)])
    return num / den

def usage(msg=None):
    if msg:
        print(msg, file=sys.stderr)
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main())
