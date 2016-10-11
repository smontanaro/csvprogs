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

import sys
import random
import getopt
import os

PROG = os.path.basename(sys.argv[0])

def main(args):
    opts, args = getopt.getopt(args, "h")
    for opt, arg in opts:
        if opt == "-h":
            usage()
            return 0

    if args:
        usage("spurious command line arguments")
        return 1

    lines = list(sys.stdin)
    random.shuffle(lines)
    sys.stdout.writelines(lines)
    return 0

def usage(msg=""):
    if msg:
        print >> sys.stderr, msg
        print >> sys.stderr
    print >> sys.stderr, __doc__ % globals()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
