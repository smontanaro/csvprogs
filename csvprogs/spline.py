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

Compute a smoothed spline of the Close values in somefile.csv with time as the
independent variable.

  %(PROG)s -x time -f Close -c spline --smooth=1 somefile.csv

DESCRIPTION
===========

Data are read from stdin or file, spline values are added to the end as a new
column.

Note that by default $(PROG)s uses dateutil.parser.parse to parse
timestamps. This is robust, but quite slow for large datasets.


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

import csv
import os
import sys
import time

import numpy
from scipy import interpolate
import dateutil.parser

from csvprogs.common import CSVArgParser, usage, openpair

PROG = os.path.basename(sys.argv[0])

def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("-f", "--field", required=True,
                        help="field/column used as input to spline function")
    parser.add_argument("-c", "--column", default="spline",
                        help="column used as output of the spline function")
    parser.add_argument("-s", "--smooth", default=0, type=float,
                        help="smoothing parameter")
    parser.add_argument("-x", default="time",
                        help="default column for independent data")
    parser.add_argument("--x-not-time", dest='istime', default=True,
                        action='store_false',
                        help="indicate independent variable is not time-based")
    (options, args) = parser.parse_known_args()

    with openpair(options, args) as (inf, outf):
        rdr = csv.DictReader(inf, delimiter=options.insep)
        wtr = csv.DictWriter(outf, fieldnames=rdr.fieldnames+[options.column],
            delimiter=options.outsep)
        if not options.append:
            wtr.writeheader()

        rows = list(rdr)
        x = []
        y = []
        for row in rows:
            x1 = row[options.x]
            y1 = row[options.field]
            if not x1 or not y1:
                continue
            if options.istime:
                x.append(to_timestamp(dateutil.parser.parse(x1)))
            else:
                x.append(float(x1))
            y.append(float(y1))
        # xx = numpy.linspace(min(x), max(x), len(x))
        x = numpy.array(x, dtype=float)
        y = numpy.array(y, dtype=float)
        tck, u = interpolate.splprep([x, y], s=options.smooth)
        ynew = interpolate.splev(u, tck)
        for (y, row) in zip(ynew[1], rows):
            row[options.column] = y
        # maybe someday? but not yet (too much difference in outpus)
        # bspline = interpolate.make_splrep(x, y, s=options.smooth)
        # ynew = bspline(xx)
        # for (y, row) in zip(ynew, rows):
        #     row[options.column] = y
        wtr.writerows(rows)

    return 0

def to_timestamp(dt):
    """Convert a datetime object into seconds since the Unix epoch."""
    return time.mktime(dt.timetuple()) + dt.microsecond/1e6


if __name__ == "__main__":
    sys.exit(main())
