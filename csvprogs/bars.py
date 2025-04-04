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

import csv
import sys
import datetime
import os
import re

import dateutil.parser
import unum.units

from csvprogs.common import CSVArgParser, openpair

PROG = os.path.basename(sys.argv[0])

def main():
    parser = CSVArgParser()
    parser.add_argument("-b", "--barlen", dest="barlen", default="60s",
                        help="bar length (seconds)")
    parser.add_argument("-n", "--name", dest="name", default="bar",
                        help="name of bar output column")
    parser.add_argument("-t", "--time", dest="time", default="time",
                        help="name of time column")
    parser.add_argument("-p", "--price", dest="price", default="close",
                        help="column used to construct bars")
    (options, args) = parser.parse_known_args()

    # Use time units to allow smaller magnitudes for longer bars. For example,
    # you can give "1h" instead of "3600s" for one-hour bars.

    with openpair(options, args) as (inf, outf):
        rdr = csv.DictReader(inf, delimiter=options.insep)
        wtr = csv.DictWriter(outf, delimiter=options.outsep,
            fieldnames=rdr.fieldnames + [options.name])
        if not options.append:
            wtr.writeheader()

        mat = re.match(r"([0-9]+)\s*([a-z]*)", options.barlen.strip())
        val = int(mat.group(1))
        units = getattr(unum.units, mat.group(2) or "s")
        barlen = int((val * units).asNumber(unum.units.s))

        generate_bars(rdr, wtr, options.time, options.price, options.name, barlen)

    return 0

def generate_bars(rdr, wtr, time, price, barname, barlen):
    interval = datetime.timedelta(seconds=barlen)

    barstart = ""
    prev_last = last = ""
    close = ""

    for row in rdr:
        dt = dateutil.parser.parse(row[time])
        prev_last = last
        if row[price]:
            last = float(row[price])
        if barstart == "":
            offset = (dt.hour * 60 * 60) + dt.minute * 60 + dt.second
            barstart = offset // barlen * barlen
            hour = barstart // 3600
            minute = barstart % 3600 // 60
            second = barstart % 3600 % 60
            barstart = dt.replace(hour=hour, minute=minute, second=second,
                                  microsecond=0)
            nextbar = barstart + interval
        close = prev_last
        if dt >= nextbar:
            # emit a new row with just the bar
            barstart += interval
            wtr.writerow({
                time: barstart,
                barname: str(close),
            })
            nextbar += interval
        else:
            row[barname] = ""
        wtr.writerow(row)

if __name__ == "__main__":
    sys.exit(main())
