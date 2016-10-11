#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
compute parametric spline of a series of values
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -f x ] [ -s sep ] [ -m val ] [ -M val ]

OPTIONS
=======

-f x     compute spline of the values in column x (zero-based offset, default 1)
-s sep   use sep as the field separator (default is comma)
-m val   discard values below this value (no default)
-M val   discard values above this value (no default)
-F fmt   use this format to parse timestamps (default is to use dateutil.parser)

DESCRIPTION
===========

Data are read from stdin, spline values are added to the end as a new
column.

Note that by default $(PROG)s uses dateutil.parser.parse to parse
timestamps. This is robust, but quite slow for large datasets. If your
timestamps are all (or mostly) in a single format it's better to use
the -F fmt command line option. Even if your data are not all in the
same format this can help. If parsing using the given format fails,
the code falls back to dateutil.parser.parse anyway.

SEE ALSO
========

* pt
* bars
* ptwin
* take
* mpl
* avg
* sigavg
"""

import sys
import getopt
import os
import csv
import time
import datetime

import numpy
from scipy import interpolate
import dateutil.parser

PROG = os.path.basename(sys.argv[0])

def main(args):
    opts, args = getopt.getopt(args, "f:s:hm:M:TtS:F:")

    field = 1
    sep = ","
    maxval = 1e308
    minval = -1e308
    xtime = True
    smooth = 0
    xfmt = ""
    for opt, arg in opts:
        if opt == "-f":
            field = int(arg)
        elif opt == "-T":
            xtime = False
        elif opt == "-t":
            xtime = True
        elif opt in ("-m", "--minval"):
            minval = float(arg)
        elif opt in ("-M", "--maxval"):
            maxval = float(arg)
        elif opt == "-s":
            sep = arg
        elif opt == "-S":
            smooth = int(arg)
        elif opt == "-F":
            xfmt = arg
        elif opt == "-h":
            usage()
            raise SystemExit

    rows = list(csv.reader(sys.stdin, delimiter=sep))
    if xtime:
        x = [to_timestamp(parse_timestamp(row[0], xfmt)) for row in rows]
    else:
        x = [float(row[0]) for row in rows]
    x = numpy.array(x, dtype=float)
    y = numpy.array([float(row[field]) for row in rows], dtype=float)
    tck, u = interpolate.splprep([x, y], s=smooth)
    ynew = interpolate.splev(u, tck)
    for (y, row) in zip(ynew[1], rows):
        row.append(y)
    csv.writer(sys.stdout, delimiter=sep).writerows(rows)
    return 0

def parse_timestamp(stamp, xfmt=""):
    if xfmt:
        try:
            return datetime.datetime.strptime(stamp, xfmt)
        except ValueError:
            pass

    # Fall back to the more general dateutil parser if no format was
    # given or we failed to successfully parse with the given format.
    return dateutil.parser.parse(stamp)

def to_timestamp(dt):
    """Convert a datetime object into seconds since the Unix epoch."""
    return time.mktime(dt.timetuple()) + dt.microsecond/1e6

def usage():
    print >> sys.stderr, __doc__ % globals()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
