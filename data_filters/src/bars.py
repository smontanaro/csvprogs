#!/usr/bin/env python

"""
===========
%(PROG)s
===========

------------------------------
compute bars from input ticks
------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -s sep ] [ -f fld ] [ -t fld ] [ -b barlen ]

OPTIONS
=======

-s sep   set the input and output field separator to sep (default comma)
-f fld   set the input data field (default 1)
-t fld   set the input time field (default 0)
-b len   set the bar length in seconds (default 60)

DESCRIPTION
===========

Bars are generated on stdout from user-specified time and price
columns on stdin.  By default, one-minute bars are created from column
1, using the timestamps in column 0.

SEE ALSO
========
* pt
* ptwin
* avg
* take
* mpl
"""

import sys
import getopt
import datetime
import os

import dateutil.parser

PROG = os.path.basename(sys.argv[0])

def main(args):
    opts, args = getopt.getopt(args, "hb:s:f:t:")

    barlen = 60                         # seconds
    field = 1
    time_field = 0
    sep = ","
    for opt, arg in opts:
        if opt == "-b":
            barlen = int(arg)
        elif opt == "-f":
            field = int(arg)
        elif opt == "-s":
            sep = arg
        elif opt == "-t":
            time_field = int(arg)
        elif opt == "-h":
            usage()
            raise SystemExit
    interval = datetime.timedelta(seconds=barlen)

    barstart = None
    prev_last = last = None
    close = ""
    for line in sys.stdin:
        fields = line.strip().split(sep)
        dt = dateutil.parser.parse(fields[time_field])
        prev_last = last
        last = float(fields[field])
        if barstart is None:
            offset = (dt.hour * 60 * 60) + dt.minute * 60 + dt.second
            barstart = offset // barlen * barlen
            hour = barstart // 3600
            minute = barstart % 3600 // 60
            second = barstart % 3600 % 60
            barstart = dt.replace(hour=hour, minute=minute, second=second,
                                  microsecond=0)
        if dt - barstart >= interval:
            close = prev_last
            barstart += interval
        fields.append(str(close))
        print sep.join(fields)
    return 0

def usage():
    print >> sys.stderr, __doc__ % globals()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
