#!/usr/bin/env python

"""=========== %(PROG)s===========

------------------------------------------------
compute correlation of two user-specified fields
------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2026-07-03
:Copyright: Skip Montanaro 2026
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -f x,y ] [ -s sep ]

OPTIONS
=======

-f x,y        use columns x and y as inputs to correlation.

DESCRIPTION
===========

Data are read from stdin, the correlation is computed, then written
to stdout.

SEE ALSO
========

* regress
* mpl
* avg
* sigavg
"""

from contextlib import suppress
import csv
import os
import statistics
import sys

from csvprogs.common import CSVArgParser, usage, openin, parse_x

PROG = os.path.basename(sys.argv[0])

def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("-f", "--fields", required=True,
                        help="numeric fields input to correlation")
    options, args = parser.parse_known_args()

    with openin(options, args) as inf:
        reader = csv.DictReader(inf, delimiter=options.insep)

        x = []
        y = []

        field1, field2 = options.fields.split(",")
        rows = list(reader)
        for row in rows:
            if row[field1] and row[field2]:
                row[field1] = parse_x(row[field1])
                row[field2] = parse_x(row[field2])
                x.append(row[field1])
                y.append(row[field2])

        r = statistics.correlation(x, y)

        if options.verbose:
            print("corr coeff:", r, file=sys.stderr)

        print(r)

    return 0


if __name__ == "__main__":
    with suppress((BrokenPipeError, KeyboardInterrupt)):
        sys.exit(main())
