#!/usr/bin/env python

"""
============
 %(PROG)s
============

---------------------------------
Shuffle lines from standard input
---------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  $(PROG)s [input [output]]

DESCRIPTION
===========

Write input (default stdin) to output (default stdout), shuffling the lines.
Note: The entire contents of the input must be read first, so it is not a good
idea to use this filter with very large files.
"""

import os
import random
import sys

from csvprogs.common import CSVArgParser, openio, usage, swallow_exceptions

PROG = os.path.basename(sys.argv[0])

def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    options, args = parser.parse_known_args()

    if len(args) > 2:
        print(usage(__doc__, globals(), msg="spurious command line arguments"),
              file=sys.stderr)
        return 1

    with openio(args[0] if len(args) >= 1 else sys.stdin, "r",
                args[1] if len(args) == 2 else sys.stdout, "w",
                encoding=options.encoding) as (inf, outf):
        lines = list(inf)
        random.shuffle(lines)
        outf.writelines(lines)
    return 0


if __name__ == "__main__":
    with swallow_exceptions((BrokenPipeError, KeyboardInterrupt)):
        sys.exit(main())
