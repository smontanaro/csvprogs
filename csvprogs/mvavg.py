#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
compute moving averages
----------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Copyright: Skip Montanaro 2016-2021
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -f x ] [ -n val ] [ -s sep ] [ -o name ]

OPTIONS
=======

-n val   number of elements in the moving average (default 5)
-f x     average the values in column x (name, no default)
-o name  name of output column (default "mean" unless -w is given,
         in which case the default is "wma")
-s sep   use sep as the field separator (default is comma)
-w       weight the values, providing more weight to more recent values

DESCRIPTION
===========

Data are read from stdin, the moving average is computed and appended
to the end of the values, then printed to stdout.

The weighted moving average formula used is from:

  https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/wma

SEE ALSO
========

* pt
* bars
* ptwin
* take
* mpl
"""

import csv
import os
import sys

from csvprogs.common import CSVArgParser, openpair, usage, weighted_ma


PROG = os.path.basename(sys.argv[0])

def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("-c", "--column", "--outcol", default="mean",
                        help="output column name")
    parser.add_argument("-f", "--field", help="input column name",
                        required=True)
    parser.add_argument("-w", "--weighted", default=False, action="store_true",
                        help="weight more recent values")
    parser.add_argument("-n", "--length", default=5, type=int,
                        help="length of moving average window")
    options, args = parser.parse_known_args()


    nan = float('nan')
    elts = [None] * options.length

    with openpair(options, args) as (inf, outf):
        rdr = csv.DictReader(inf, delimiter=options.insep)
        wtr = csv.DictWriter(outf, delimiter=options.outsep,
            fieldnames=rdr.fieldnames+[options.column])
        if not options.append:
            wtr.writeheader()
        coeffs = ([1] * options.length
            if not options.weighted
            else list(range(options.length, 0, -1)))
        for row in rdr:
            if row[options.field]:
                elts.append(float(row[options.field]))
                del elts[0]
            else:
                # restart mv avg calc
                elts = [None] * options.length
            if None not in elts:
                val = weighted_ma(elts, coeffs)
            else:
                val = nan
            row[options.column] = val
            wtr.writerow(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
