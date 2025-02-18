#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
compute hull moving averages
----------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2021-04-19
:Copyright: TradeLink LLC 2013
:Copyright: Skip Montanaro 2021
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -f x ] [ -n val ] [ -s sep ] [ -o name ]

OPTIONS
=======

-n val   number of elements in the moving average (default 30)
-f x     average the values in column x (name, no default)
-o name  name of output column (default "hull")
-s sep   use sep as the field separator (default is comma)

DESCRIPTION
===========

Data are read from stdin, the hull moving average is computed and
appended to the end of the values, then printed to stdout.

The formula used is from:

  https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/hull-moving-average

The above page doesn't describe whether to truncate or round sqrt(n),
so I've chosen to round.  For n == 10, we choose 3, for n == 15, we
choose 4.


SEE ALSO
========

* mvavg

"""

from contextlib import suppress
import csv
import math
import os
import sys

from csvprogs.common import CSVArgParser, openpair, usage, weighted_ma


PROG = os.path.basename(sys.argv[0])

def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("-n", "--length", default=30, type=int,
                        help="moving average length")
    parser.add_argument("-f", "--field", required=True,
                        help="column on which to compute hull")
    parser.add_argument("-c", "--column", default="hull",
                        help="output column")
    (options, args) = parser.parse_known_args()

    with openpair(options, args) as (inf, outf):
        reader = csv.DictReader(inf, delimiter=options.insep)
        fnames = reader.fieldnames + [options.column]
        wtr = csv.DictWriter(outf, delimiter=options.outsep, fieldnames=fnames)
        if not options.append:
            wtr.writeheader()
        coeffs = list(range(options.length, 0, -1))
        half = options.length // 2
        sqrt_len = int(round(math.sqrt(options.length)))
        # values correspond to raw data, wma(n), wma(n/2), hull(n).
        # Values for wma(n), wma(n/2) and hull(n) are only computed when
        # the raw data fills up enough to eliminate the None values in the
        # raw data.
        values = [
            [None] * options.length,        # raw inputs, appended to end
            [None] * options.length,        # wma(n)
            [None] * options.length,        # wma(n/2)
            [None] * options.length,        # 2 * wma(n/2) - wma(n)
        ]
        for row in reader:
            val = ""
            if row[options.field]:
                values[0].append(float(row[options.field]))
                del values[0][0]
                if None not in values[0]:
                    # wma(n)
                    values[1].append(weighted_ma(values[0], coeffs))
                    del values[1][0]
                    # wma(n/2)
                    values[2].append(weighted_ma(values[0][-half:], coeffs[-half:]))
                    del values[2][0]
                    # 2 * wma(n/2) - wma(n)
                    values[3].append(2 * values[2][-1] - values[1][-1])
                    del values[3][0]
                    vals = values[3][-sqrt_len:]
                    if None not in vals:
                        val = weighted_ma(vals, coeffs[-sqrt_len:])
            row[options.column] = val
            wtr.writerow(row)
    return 0


if __name__ == "__main__":
    with suppress((BrokenPipeError,)):
        sys.exit(main())
