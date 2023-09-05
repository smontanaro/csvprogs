#!/usr/bin/env python

"""
===========
{PROG}
===========

----------------------------------------------------
Compute exponentially weighted moving average
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  {PROG} [ -o name ] [ -f x ] [ -a val ] [ -s sep ]

OPTIONS
=======

-a val   alpha of the ewma (default 0.1)
-f x     average the values in column x (zero-based offset or name - default 1)
-s sep   use sep as the field separator (default is comma)
-o name  define output column name (default: "ewma")

DESCRIPTION
===========

Data are read from stdin, the ewma is computed, appended to the end of
the values, then printed to stdout.

SEE ALSO
========

* pt
* bars
* ptwin
* take
* mpl
* avg
"""

import csv
import getopt
import os
import sys

PROG = os.path.basename(sys.argv[0])

def main():
    opts, args = getopt.getopt(sys.argv[1:], "a:f:s:o:h")

    alpha = 0.1
    field = 1
    sep = ","
    outcol = "ewma"
    for opt, arg in opts:
        if opt == "-a":
            alpha = float(arg)
        elif opt == "-o":
            outcol = arg
        elif opt == "-f":
            try:
                field = int(arg)
                reader = csv.reader
                writer = csv.writer
            except ValueError:
                # Dict key
                field = arg
                reader = csv.DictReader
                writer = csv.DictWriter
        elif opt == "-s":
            sep = arg
        elif opt == "-h":
            usage()
            raise SystemExit

    val = None
    rdr = reader(sys.stdin, delimiter=sep)
    if isinstance(field, str):
        fnames = rdr.fieldnames[:]
        fnames.append(outcol)
        wtr = writer(sys.stdout, delimiter=sep, fieldnames=fnames)
        wtr.writeheader()
    else:
        wtr = writer(sys.stdout, delimiter=sep)
    for row in rdr:
        if row[field]:
            if val is None:
                val = float(row[field])
            else:
                val = alpha * float(row[field]) + (1-alpha) * val
            if isinstance(field, str):
                row[outcol] = val
            else:
                row.append(val)
        wtr.writerow(row)
    return 0

def usage():
    print(__doc__.format(**globals()).strip(), file=sys.stderr)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, KeyboardInterrupt):
        sys.exit(0)
