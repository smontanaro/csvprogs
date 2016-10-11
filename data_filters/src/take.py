#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
Pass every nth line to stdout
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

 %(PROG)s [ -n n ]

OPTIONS
=======

-n n   copy every n'th line to stdout (default 10)

SEE ALSO
========

* pt
* bars
* avg
* ptwin
* mpl
"""

from __future__ import absolute_import
from __future__ import print_function
import sys
import getopt
import os

PROG = os.path.basename(sys.argv[0])

def main(args):
    opts, args = getopt.getopt(args, "n:h")

    n = 10
    for opt, arg in opts:
        if opt == "-n":
            n = int(arg)
        elif opt == "-h":
            usage()
            raise SystemExit

    i = 0
    for line in sys.stdin:
        if not i % n:
            print(line.strip())
        i += 1
    return 0

def usage():
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
