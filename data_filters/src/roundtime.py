#!/usr/bin/env python

"""
===============
%(PROG)s
===============

---------------------------------------
Round timestamps to specified precision
---------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-08-13
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -s sep ] [ -f fld ] [ -t fld ] [ -b barlen ]

OPTIONS
=======

-s sep      set the input and output field separator to sep (default comma)
-t fld      set the input time field (default 0)
-d digits   set the number of digits of precision (default 0)

DESCRIPTION
===========

The time field is rounded to the nearest 10 ** -digits seconds, where
digits is given by the -d option.

EXAMPLE
=======

Round the timestamps in the fourth column (offset three from the
leftmost column) to the nearest hundredth of a second:

  %(PROG)s -t 3 -d 2

SEE ALSO
========
* csv2csv
* csvmerge
"""

from __future__ import absolute_import
from __future__ import print_function
import sys
import getopt
import datetime
import os
import csv
import time

import dateutil.parser
from six.moves import zip

PROG = os.path.basename(sys.argv[0])

def main(args):
    opts, args = getopt.getopt(args, "hs:t:d:")

    digits = 0
    time_field = 0
    sep = ","
    for opt, arg in opts:
        if opt == "-s":
            sep = arg
        elif opt == "-d":
            digits = int(arg)
        elif opt == "-t":
            try:
                time_field = int(arg)
                reader = csv.reader
                writer = csv.writer
            except ValueError:
                time_field = arg
                reader = csv.DictReader
                writer = csv.DictWriter
        elif opt == "-h":
            usage()
            return 0

    rdr = reader(sys.stdin)
    if writer == csv.DictWriter:
        wtr = writer(sys.stdout, fieldnames=rdr.fieldnames)
        wtr.writerow(dict(list(zip(rdr.fieldnames, rdr.fieldnames))))
    else:
        wtr = writer(sys.stdout)
    power = 10 ** digits
    for row in rdr:
        dt = dateutil.parser.parse(row[time_field])
        epoch_t = to_timestamp(dt)
        t = round(epoch_t * power) / power
        row[time_field] = datetime.datetime.fromtimestamp(t)
        wtr.writerow(row)
    return 0

def to_timestamp(dt):
    """Convert a datetime object into seconds since the Unix epoch."""
    return time.mktime(dt.timetuple()) + dt.microsecond/1e6

def usage():
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
