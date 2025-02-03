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

import sys
import os

from csvprogs.common import CSVArgParser

PROG = os.path.basename(sys.argv[0])

def main():
    parser = CSVArgParser()
    parser.add_argument("-n", type=int, default=10,
                        help="print every n'th line from the input")
    options = parser.parse_args()

    i = 0
    for line in sys.stdin:
        if not i % options.n:
            print(line.strip())
        i += 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
