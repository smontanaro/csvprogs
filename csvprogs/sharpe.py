#!/usr/bin/env python3

"""
Take in output of mean(1) on stdin and optional intervals per year
(on command line, default: 253), produce Sharpe Ratio on stdout.

===========
sharpe
===========

----------------------------------------------------
compute sharpe ratio from output of mean(1)
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2016-08-16
:Copyright: TradeLink LLC 2016
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  sharpe [ -h ] [ -s char ] [ N ]

OPTIONS
=======

-h       print this and exit
-s char  use char as the input separator

DESCRIPTION
===========

Data are read from stdin. An optional number of measurements per year
(default: 253) are read from the command line. The Sharpe Ratio is printed
on stdout.

SEE ALSO
========

* mean
"""

import csv
import math
import os
import sys

from csvprogs.common import CSVArgParser, openpair, usage


PROG = os.path.basename(sys.argv[0])

def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("-d", "--days", default=253, type=int,
                        help="measurements per year")
    options, args = parser.parse_known_args()

    with openpair(options, args) as (inf, outf):
        fields = next(csv.reader(inf, delimiter=options.insep))

        _n = int(fields[0])
        mean = float(fields[1])
        _median = float(fields[2])
        std = float(fields[3])

        print(mean / std * math.sqrt(options.days), file=outf)


if __name__ == "__main__":
    sys.exit(main())
