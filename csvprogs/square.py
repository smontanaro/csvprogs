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

 %(PROG)s -x name -f name[,name...]

OPTIONS
=======

-x name          - use name as the X axis value.
-f name,name,... - use these names as the Y values.

DESCRIPTION
===========

When thinking about market prices, it's useful to think of a given
price holding until there is a change.  If all you do is plot the
changes, you wind up with diagonal lines between two quote prices.
It's more correct to think of the earlier price holding until just
before the new price is received.

Consider a simple CSV file:

time,symbol,price
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

time,symbol,price
2012-10-25T09:18:15.593480,F:C6Z12,10057
2012-10-25T09:18:38.796756,F:C6Z12,10057
2012-10-25T09:18:38.796756,F:C6Z12,10058
2012-10-25T09:18:38.796930,F:C6Z12,10058
2012-10-25T09:18:38.796930,F:C6Z12,10059

That is, it elides all duplicate y values and inserts a single
row just before each price change to 'square up' the plot.

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
import os
import copy

from csvprogs.common import CSVArgParser, openio

PROG = os.path.basename(sys.argv[0])

def main():
    parser = CSVArgParser()
    parser.add_argument("-x", default="time",
                        help="column to use as the X value")
    options, args = parser.parse_known_args()

    with openio(args[0] if len(args) >= 1 else sys.stdin, "r",
                args[1] if len(args) == 2 else sys.stdout, "w",
                encoding=options.encoding) as (inf, outf):
        rdr = csv.DictReader(inf, delimiter=options.insep)
        wtr = csv.DictWriter(outf, fieldnames=rdr.fieldnames,
            delimiter=options.outsep)
        wtr.writeheader()
        yvals = rdr.fieldnames[:]
        yvals.remove(options.x)
        for row in square(remove_dups(rdr, options.x, yvals), options.x, yvals):
            wtr.writerow(row)

    return 0

def remove_dups(iterator, x, yvals):
    assert x not in yvals
    last = []
    row = None
    for row in iterator:
        value = [row[y] for y in yvals]
        if value != last:
            # some y value changed - not a duplicate
            yield row
            row = None
            # remember...
            last = value
    if row is not None:
        # keep the last row, even if it was a duplicate, so we preserve the
        # last x value.
        yield row

def square(rows, x, yvals):
    assert x not in yvals
    try:
        r1 = next(rows)
    except StopIteration:
        return
    yield r1

    for r2 in rows:
        row = copy.copy(r2)
        for y in yvals:
            row[y] = r1[y]
        # retain the previous y values, but don't mess with x
        yield row
        # now the new values at the same x value
        yield r2
        r1 = r2

def usage(msg=""):
    if msg:
        print(msg, file=sys.stderr)
        print(file=sys.stderr)
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main())
