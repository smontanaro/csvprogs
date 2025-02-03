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
import getopt
import math
import os
import sys

PROG = os.path.basename(sys.argv[0])

def main():
    opts, args = getopt.getopt(sys.argv[1:], "s:h")

    days = 253
    sep = ","
    for opt, arg in opts:
        if opt == "-s":
            sep = arg
        elif opt == "-h":
            usage()
            return 0

    if len(args) > 1:
        usage(f"{PROG} accepts zero or one positional arguments")
        return 1

    if args:
        days = int(args[0])

    fields = next(csv.reader(sys.stdin, delimiter=sep))

    n = int(fields[0])
    mean = float(fields[1])
    median = float(fields[2])
    std = float(fields[3])
    print(mean / std * math.sqrt(days))

def usage(msg=None):
    if msg is not None:
        print(msg, file=sys.stderr)
        print(file=sys.stderr)
    print((__doc__.strip() % globals()), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main())
