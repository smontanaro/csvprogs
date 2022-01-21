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

  $(PROG)s

DESCRIPTION
===========

Write stdin to stdout, shuffling the lines.  Note: The entire contents
of stdin must be read first, so it is not a good idea to use this
filter with very large files.
"""

import contextlib
import getopt
import os
import random
import sys

PROG = os.path.basename(sys.argv[0])

@contextlib.contextmanager
def swallow(exceptions):
    "catch and swallow the named exceptions"
    try:
        yield None
    except exceptions:
        pass
    finally:
        pass

def main():
    opts, args = getopt.getopt(sys.argv[1:], "h")
    for opt, _arg in opts:
        if opt == "-h":
            usage()
            return 0

    if args:
        usage("spurious command line arguments")
        return 1

    with swallow((BrokenPipeError, KeyboardInterrupt)):
        lines = list(sys.stdin)
        random.shuffle(lines)
        sys.stdout.writelines(lines)
    return 0

def usage(msg=""):
    if msg:
        print(msg, file=sys.stderr)
        print(file=sys.stderr)
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main())
