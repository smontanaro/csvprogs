#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
Signal average inputs based on time.
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -f x,y ] [ -s sep ] [ -m val ] [ -M val ]

OPTIONS
=======

-f x,y   average field y over time x (zero-based offsets, default 0,2)
-s sep   use sep as the field separator (default is comma)
-m val   discard values below this value (no default)
-M val   discard values above this value (no default)

DESCRIPTION
===========

TBD.

SEE ALSO
========

* pt
* bars
* avg
* take
* ptwin
* mpl
"""

import sys
import os
import csv
import getopt

PROG = os.path.basename(sys.argv[0])

def main(args):
    opts, args = getopt.getopt(args, "f:s:m:M:hH",
                               ["fields=", "separator=", "minval=",
                                "maxval=", "help", "skip-header"])
    x, y = [0, 2]
    sep = ","
    maxval = 1e308
    minval = -1e308
    skip_header = False
    for opt, arg in opts:
        if opt in ("-f", "--fields"):
            x, y = [int(val.strip()) for val in arg.split(",")]
        elif opt in ("-s", "--separator"):
            sep = arg
        elif opt in ("-m", "--minval"):
            minval = float(arg)
        elif opt in ("-M", "--maxval"):
            maxval = float(arg)
        elif opt in ("-h", "--help"):
            usage()
            raise SystemExit
        elif opt == "-H":
            skip_header = True

    times = {}
    rdr = csv.reader(sys.stdin, delimiter=sep)
    wtr = csv.writer(sys.stdout, delimiter=sep)
    if skip_header:
        row = rdr.next()
        row.extend(["mean", "sum", "n"])
        wtr.writerow(row)
    for row in rdr:
        try:
            val = float(row[y])
            if val < minval or val > maxval:
                continue
            now = row[x].split("T")[-1].split(".")[0]
            total, n = times.get(now, (0.0, 0))
            total += val
        except IndexError:
            print >> sys.stderr, "failed to process row:", row
        else:
            n += 1
            times[now] = (total, n)
    for t in sorted(times):
        total, n = times[t]
        wtr.writerow((t, total/n, total, n))

def usage():
    print >> sys.stderr, __doc__ % globals()

if __name__ == "__main__":
    main(sys.argv[1:])
