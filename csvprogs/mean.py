#!/usr/bin/env python

"""
===========
{PROG}
===========

----------------------------------------------------
compute mean, median, stddev of a series of values
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  {PROG} -f x ] [ -s sep ] [ -m val ] [ -M val ] [ file ]

OPTIONS
=======

-f x     average the values in column x (zero-based offset, default 1)
-s sep   use sep as the field separator (default is comma)
-m val   discard values below this value (no default)
-M val   discard values above this value (no default)

DESCRIPTION
===========

Data are read from the file given on the command line, or stdin. The
mean, median, and standard deviation are computed.  Output is: number
of records, mean, median, and standard deviation.

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
import statistics
import sys


from csvprogs.common import CSVArgParser, openio, usage


PROG = os.path.basename(sys.argv[0])


def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("-f", "--field", required=True,
                        help="field on which to compute rudimentary statistics")
    parser.add_argument("-m", "--minval", default=-1e308, type=float,
                        help="toss values below the minval")
    parser.add_argument("-M", "--maxval", default=1e308, type=float,
                        help="toss values above the maxval")
    options, args = parser.parse_known_args()

    mode = "a" if options.append else "w"
    with openio(args[0] if len(args) >= 1 else sys.stdin, "r",
                args[1] if len(args) == 2 else sys.stdout, mode,
                encoding=options.encoding) as (inf, outf):
        reader = csv.DictReader(inf, delimiter=options.insep)
        values = []
        for row in reader:
            if row[options.field]:
                val = float(row[options.field])
                if val < options.minval or val > options.maxval:
                    continue
                values.append(val)
        median = statistics.median(values)
        mean = statistics.mean(values)
        pstd = statistics.pstdev(values, mu=mean)
        writer = csv.writer(outf, delimiter=options.outsep)
        writer.writerow([len(values), mean, median, pstd])
    return 0


if __name__ == "__main__":
    sys.exit(main())
