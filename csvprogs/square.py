#!/usr/bin/env python

"""
===========
%(PROG)s
===========

-----------------------------------------------------
Convert data from point-to-point to square movements
-----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

 %(PROG)s [ -k n ] [ -s sep ] [ -h ] [ -b ] [ -H ]

OPTIONS
=======

-k n use field n as a key field (default: 1) - may be given
multiple times to build compound key.  Last value of n is used as
the 'squared' value.  The first field is assumed to be the datetime
(x axis). The key may be a column name as well.

-s sep Use sep as the field separator (default is comma).

-b   Instead of removing entire rows, just blank duplicate fields.

-H   Skip header at start of input - ignored if any element of the key is
     non-numeric.

DESCRIPTION
===========

When thinking about market prices, it's useful to think of a given
price holding until there is a change.  If all you do is plot the
changes, you wind up with diagonal lines between two quote prices.
It's more correct to think of the earlier price holding until just
before the new price is received.

Consider a simple CSV file:

2012-10-25T09:18:15.593480,F:C6Z12,10057
2012-10-25T09:18:38.796756,F:C6Z12,10058
2012-10-25T09:18:38.796769,F:C6Z12,10058
2012-10-25T09:18:38.796912,F:C6Z12,10058
2012-10-25T09:18:38.796924,F:C6Z12,10058
2012-10-25T09:18:38.796930,F:C6Z12,10059

The lines connecting the first two points and the last two points will
be plotted diagonally.  That's probably not really the way these data
should be viewed.  Once a price is seen, it should remain in effect
until the next price is seen.  Also, the repetitive points with a y
value of 10058 cause useless work for downstream filters.

Given the above input, this filter emits the following:

2012-10-25T09:18:15.593480,F:C6Z12,10057
2012-10-25T09:18:38.796755,F:C6Z12,10057
2012-10-25T09:18:38.796756,F:C6Z12,10058
2012-10-25T09:18:38.796929,F:C6Z12,10058
2012-10-25T09:18:38.796930,F:C6Z12,10059

That is, it elides all duplicate y values and inserts a single
duplicate just before each price change to 'square up' the plot.

The net effect is that plots look square and are generally rendered
much faster because they contain many fewer points.

SEE ALSO
========

* nt
* pt
* mpl
"""

import sys
import csv
import getopt
import os
import copy

PROG = os.path.basename(sys.argv[0])

def main():
    opts, _args = getopt.getopt(sys.argv[1:], "hk:s:b")

    keys = []
    sep = ','
    blank = False
    for opt, arg in opts:
        if opt == "-h":
            usage()
            return 0
        if opt == "-s":
            sep = arg
        elif opt == "-k":
            keys.append(arg)
        elif opt == "-b":
            blank = True
    if not keys:
        usage("At least one key field is required.")
        return 1

    rdr = csv.DictReader(sys.stdin, delimiter=sep)
    wtr = csv.DictWriter(sys.stdout, fieldnames=rdr.fieldnames,
        delimiter=sep)
    wtr.writeheader()
    for row in square(remove_dups(rdr, keys, blank), keys):
        wtr.writerow(row)

    return 0

def remove_dups(iterator, keys, blank):
    last = []
    row = None
    for row in iterator:
        value = [row[k] for k in keys]
        if value != last:
            yield row
        elif blank:
            for k in keys:
                row[k] = ""
            yield row
        last = value
    if row is not None:
        yield row

def square(rows, keys):
    try:
        r1 = next(rows)
    except StopIteration:
        return
    yield r1
    for r2 in rows:
        row = copy.copy(r2)
        for k in keys:
            row[k] = r1[k]
        yield row
        yield r2
        r1 = r2

def usage(msg=""):
    if msg:
        print(msg, file=sys.stderr)
        print(file=sys.stderr)
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main())
