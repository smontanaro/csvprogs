#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
Compute exponentially weighted moving average
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -f x ] [ -a val ] [ -s sep ]

OPTIONS
=======

-a val   alpha of the ewma (default 0.1)
-f x     average the values in column x (zero-based offset - default 1)
-s sep   use sep as the field separator (default is comma)

DESCRIPTION
===========

Data are read from stdin, the ewma is computed, appended to the end of
the values, then printed to stdout.

SEE ALSO
========

* pt
* bars
* ptwin
* take
* mpl
* avg
"""

from __future__ import absolute_import
from __future__ import print_function
import sys
import getopt
import os

PROG = os.path.basename(sys.argv[0])

def main(args):
    opts, args = getopt.getopt(args, "a:f:s:h")

    alpha = 0.1
    field = 1
    sep = ","
    for opt, arg in opts:
        if opt == "-a":
            alpha = float(arg)
        elif opt == "-f":
            field = int(arg)
        elif opt == "-s":
            sep = arg
        elif opt == "-h":
            usage()
            raise SystemExit

    val = None
    for line in sys.stdin:
        fields = line.strip().split(sep)
        if fields[field]:
            if val is None:
                val = float(fields[field])
            else:
                val = alpha * float(fields[field]) + (1-alpha) * val
        fields.append(str(val))
        print(sep.join(fields))
    return 0

def usage():
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
