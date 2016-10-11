#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
Sort a CSV file by user-defined keys.
----------------------------------------------------

SYNOPSIS
========

%(PROG)s -k f1,f2,f3,... [ options ] [ infile ]

OPTIONS
=======

-k fields   list merge fields (quote if names contain spaces)

An optional input file can be given on the command line.  If not
given, input is read from stdin.  Output is to stdout.  Column order
remains unchanged on output.

EXAMPLE
=======

To sort stdin by date and time::

    %(PROG)s -k 'Date Stamp,Time Stamp'
"""

# source: URL: http://svnhost:3690/svn/people/skipm/trunk/scripts/csvmerge.py

from __future__ import absolute_import
from __future__ import print_function
import sys
import csv
import getopt
import os
from six.moves import zip

PROG = os.path.splitext(os.path.split(sys.argv[0])[1])[0]

def usage(msg=None):
    if msg is not None:
        print(msg, file=sys.stderr)
        print(file=sys.stderr)
    print((__doc__.strip() % globals()), file=sys.stderr)

def main(args):
    keys = []

    try:
        opts, args = getopt.getopt(args, "k:h")
    except getopt.GetoptError as msg:
        usage(msg)
        return 1

    for opt, arg in opts:
        if opt == "-k":
            keys = arg.split(",")
        elif opt == "-h":
            usage()
            return 0

    if len(args) > 1:
        usage("Too many input files")
        return 1

    if args:
        fname = args[0]
    else:
        fname = "/dev/stdin"
    f = open(fname)
    r = csv.reader(f)
    fields = next(r)
    rest = sorted(set(fields) - set(keys))
    rdr = csv.DictReader(f, fieldnames=fields)

    writer = csv.DictWriter(sys.stdout, fieldnames=fields, restval="")
    writer.writerow(dict(list(zip(fields, fields))))

    rows = sorted(rdr, cmp=lambda x, y: cmp([x[k] for k in keys],
                                            [y[k] for k in keys]))
    for row in rows:
        writer.writerow(row)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
