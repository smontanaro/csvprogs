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

 %(PROG)s [ -n ] [ -k n ] [ -s sep ] [ -h ] [ -b ] [ -H ]

OPTIONS
=======

-k n use field n as a key field (default: 1) - may be given
multiple times to build compound key.  Last value of n is used as
the 'squared' value.  The first field is assumed to be the datetime
(x axis). The key may be a column name as well.

-n   X axis is numeric, not time.

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
import datetime
import copy

import dateutil.parser

PROG = os.path.basename(sys.argv[0])

def main(args):
    opts, args = getopt.getopt(args, "hk:s:nbH")

    keys = []
    numeric = False
    sep = ','
    blank = False
    skip_header = False
    for opt, arg in opts:
        if opt == "-h":
            usage()
            raise SystemExit
        elif opt == "-s":
            sep = arg
        elif opt == "-n":
            numeric = True
        elif opt == "-k":
            try:
                keys.append(int(arg))
            except ValueError:
                # Non-int implies use of dictionaries later
                keys.append(arg)
        elif opt == "-b":
            blank = True
        elif opt == "-H":
            skip_header = True
    if not keys:
        keys.append(1)

    if str in set(type(k) for k in keys):
        # At least one key is a string - use DictReader/DictWriter
        rdr = csv.DictReader(sys.stdin, delimiter=sep)
        wtr = csv.DictWriter(sys.stdout, fieldnames=rdr.fieldnames,
                             delimiter=sep)
        wtr.writerow(dict(zip(wtr.fieldnames, wtr.fieldnames)))
    else:
        rdr = csv.reader(sys.stdin, delimiter=sep)
        wtr = csv.writer(sys.stdout, delimiter=sep)
        if skip_header:
            wtr.writerow(rdr.next())
    for row in square(remove_dups(rdr, keys, blank), 0, keys[-1], numeric):
        wtr.writerow(row)

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

def square(iterator, t, y, numeric):
    r1 = iterator.next()
    yield r1
    for r2 in iterator:
        row = copy.copy(r2)
        row[y] = r1[y]
        yield row
        yield r2
        r1 = r2

def usage():
    print >> sys.stderr, __doc__ % globals()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
