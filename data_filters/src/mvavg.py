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
-o name  name of output column (default "mean")
-s sep   use sep as the field separator (default is comma)

DESCRIPTION
===========

Data are read from stdin, the moving average is computed and appended
to the end of the values, then printed to stdout.

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

def main(args):
    opts, args = getopt.getopt(args, "n:f:s:o:h")

    outcol = "mean"
    length = 5
    field = None
    sep = ","
    reader = csv.DictReader
    writer = csv.DictWriter
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

    elts = [None] * length
    rdr = reader(sys.stdin, delimiter=sep)
    if isinstance(field, str):
        fnames = rdr.fieldnames[:]
        fnames.append(outcol)
        wtr = writer(sys.stdout, delimiter=sep, fieldnames=fnames)
        wtr.writerow(dict(list(zip(fnames, fnames))))
    else:
        wtr = writer(sys.stdout, delimiter=sep)
    for row in rdr:
        if row[field]:
            elts.append(float(row[field]))
            del elts[0]
        if None not in elts:
            val = sum(elts)/len(elts)
        else:
            val = ""
        if reader == csv.reader:
            row.append(val)
        else:
            row[outcol] = val
        wtr.writerow(row)
    return 0

def usage(msg=None):
    if msg:
        print(msg, file=sys.stderr)
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
