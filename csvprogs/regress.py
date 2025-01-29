#!/usr/bin/env python

"""===========
%(PROG)s
===========

-------------------------------------------------------
compute linear regression of two user-specified fields
-------------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2014-01-13
:Copyright: TradeLink LLC 2014
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -c ] [ -f x,y ] [ -s sep ] [ -o col ]

OPTIONS
=======

-f x,y   use columns x and y as inputs to regression.
-s sep   use sep as the field separator (default is comma)
-o col   write to column col - if not given, just append to output
-c       only print correlation coefficient to stdout, no regression data

DESCRIPTION
===========

Data are read from stdin, the regression is computed, the the input is
written to stdout with the new field.  Details about the regression
results are written to stderr (unless -c is given).

SEE ALSO
========

* take
* mpl
* avg
* sigavg
"""

import sys
import os
import csv

import scipy.stats

from csvprogs.common import CSVArgParser, usage, openio

PROG = os.path.basename(sys.argv[0])

def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("-c", "--corr", default=False, action="store_true",
                        help="only print correlation coefficient to stdout")
    parser.add_argument("--column", default="reg",
                        help="output column name for regression")
    parser.add_argument("-f", "--fields", required=True,
                        help="fields input to regression")
    options, args = parser.parse_known_args()

    mode = "a" if options.append else "w"
    with openio(args[0] if len(args) >= 1 else sys.stdin, "r",
                args[1] if len(args) == 2 else sys.stdout, mode,
                encoding=options.encoding) as (inf, outf):
        reader = csv.DictReader(inf, delimiter=options.insep)
        writer = csv.DictWriter(outf, delimiter=options.outsep,
            fieldnames=reader.fieldnames+[options.column])

        x = []
        y = []

        field1, field2 = options.fields.split(",")
        rows = list(reader)
        for row in rows:
            if row[field1] and row[field2]:
                row[field1] = float(row[field1])
                row[field2] = float(row[field2])
                x.append(row[field1])
                y.append(row[field2])

        (slope, intercept, r, p, stderr) = scipy.stats.linregress(x, y)

        if options.corr:
            print(r)
            return 0

        if options.verbose:
            print("slope:", slope, "intercept:", intercept, file=sys.stderr)
            print("corr coeff:", r, "p:", p, "err:", stderr, file=sys.stderr)

        if not options.append:
            writer.writeheader()
        for row in rows:
            if row[field1]:
                val = slope * float(row[field1]) + intercept
                row[options.column] = val
            writer.writerow(row)

    return 0


if __name__ == "__main__":
    sys.exit(main())
