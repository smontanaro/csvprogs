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

import dateutil.parser

from csvprogs.common import CSVArgParser, openio, usage


PROG = os.path.basename(sys.argv[0])

def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("-x", help="x axis", required=True)
    parser.add_argument("-y", help="y axis", required=True)
    parser.add_argument("-m", "--minval", help="lower threshold",
                        default=-1e308, type=float)
    parser.add_argument("-M", "--maxval", help="upper threshold",
                        default=1e308, type=float)
    options, args = parser.parse_known_args()

    times = {}

    mode = "a" if options.append else "w"
    with openio(args[0] if len(args) >= 1 else sys.stdin, "r",
                args[1] if len(args) == 2 else sys.stdout, mode,
                encoding=options.encoding) as (inf, outf):
        reader = csv.DictReader(inf, delimiter=options.insep)
        writer = csv.DictWriter(outf, delimiter=options.outsep,
            fieldnames=["time", "mean", "sum", "n"])
        if not options.append:
            writer.writeheader()
        for row in reader:
            val = float(row[options.y])
            if val < options.minval or val > options.maxval:
                continue
            now = dateutil.parser.parse(row[options.x]).time()
            total, n = times.get(now, (0.0, 0))
            total += val
            n += 1
            times[now] = (total, n)
        for t in sorted(times):
            total, n = times[t]
            writer.writerow(
                {
                 "time": t,
                 "mean": total/n,
                 "sum": total,
                 "n": n,
                })


if __name__ == "__main__":
    sys.exit(main())
