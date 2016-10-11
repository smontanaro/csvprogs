#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
compute mean, median, stddev of a series of values
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -H ] -f x ] [ -s sep ] [ -m val ] [ -M val ] [ file ]

OPTIONS
=======

-H       input has a CSV header
-f x     average the values in column x (zero-based offset, default 1)
-s sep   use sep as the field separator (default is comma)
-m val   discard values below this value (no default)
-M val   discard values above this value (no default)

DESCRIPTION
===========

Data are read from the file given on the command line, or stdin. The
mean, median, and standard deviation are computed.  Output is: number
of records, mean, median, and standard deviation.

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

from __future__ import absolute_import
from __future__ import print_function
import sys
import getopt
import os
import numpy
import csv

PROG = os.path.basename(sys.argv[0])

def main(args):
    try:
        opts, args = getopt.getopt(args, "f:s:hm:M:H")
    except getopt.GetoptError:
        usage()
        return 1

    field = 1
    sep = ","
    maxval = 1e308
    minval = -1e308
    header = False
    for opt, arg in opts:
        if opt == "-f":
            field = arg
        elif opt in ("-m", "--minval"):
            minval = float(arg)
        elif opt in ("-M", "--maxval"):
            maxval = float(arg)
        elif opt == "-s":
            sep = arg
        elif opt == "-H":
            header = True
        elif opt == "-h":
            usage()
            return 0

    if len(args) > 1:
        usage()
        return 1
    if len(args) == 1:
        inf = open(args[0], "rb")
    else:
        inf = sys.stdin
    values = []
    if header:
        rdr = csv.DictReader(inf)
    else:
        rdr = csv.reader(inf)
        field = int(field)
    for row in rdr:
        if row[field]:
            val = float(row[field])
            if val < minval or val > maxval:
                continue
            values.append(val)
    median = sorted(values)[len(values)//2]
    values = numpy.array(values, dtype=float)
    mean = numpy.mean(values)
    std = numpy.std(values)
    print("%d%s%f%s%f%s%f" % (len(values), sep, mean, sep, median, sep, std))
    return 0

def usage():
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
