#!/usr/bin/env python

"""
%(PROG)s - Merge multiple CSV files.


===========
%(PROG)s
===========

----------------------------------------------------
Merge multiple CSV files
----------------------------------------------------

SYNOPSIS
========

 %(PROG)s -k f1,f2,f3,... [ options ] infile ...

OPTIONS
=======

-k fields    merge fields (quote if names contain spaces)

if given, infile specifies the input CSV file (default: stdin)

DESCRIPTION
===========

Data are read from the input files.  Each row is written to the
output, merging the inputs together. Files must be sorted by the key
field(s).  The output will have the union of all columns.

Multiple input files are given on the command line.  Output is to
stdout.  On output the key fields are listed first (in the order
given).  The remaining fields are simply sorted.

EXAMPLE
=======

To merge two csv files, A.csv and B.csv, by both the date and time fields:
2011-05-09 by date and time::

    %(PROG)s -k 'date,time' A.csv B.csv

SEE ALSO
========

* csv2csv
* csvsort
* data_misc package

:Author: skipm@trdlnk.com
:Date: 2013-07-19
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters
"""

from __future__ import absolute_import
from __future__ import print_function
import sys
import csv
import getopt
import os
from six.moves import zip

PROG = os.path.split(sys.argv[0])[1]

def usage(msg=None):
    if msg is not None:
        print(msg, file=sys.stderr)
        print(file=sys.stderr)
    print((__doc__.strip() % globals()), file=sys.stderr)

def main(args):
    keys = []
    readers = []

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

    if len(args) < 1:
        usage("At least one input file is required.")
        return 1

    all_fields = set()
    for fname in args:
        f = open(fname, "r")
        rdr = csv.DictReader(f)
        all_fields |= set(rdr.fieldnames)
        readers.append(rdr)

    rest = sorted(all_fields - set(keys))

    out_fields = keys + sorted(rest)

    writer = csv.DictWriter(sys.stdout, fieldnames=out_fields, restval="")
    writer.writerow(dict(list(zip(out_fields, out_fields))))

    rows = {}
    # Populate dict of readers with the first row from each.
    for rdr in readers:
        try:
            row = next(rdr)
        except StopIteration:
            pass
        else:
            rows[rdr] = ([row.get(k, "") for k in keys], row, rdr)

    while True:
        if not rows:
            return 0

        _, row, rdr = min(rows.values())
        writer.writerow(row)

        # Fill in the now stale slot with the next row.
        try:
            row = next(rdr)
        except StopIteration:
            del rows[rdr]
        else:
            rows[rdr] = ([row.get(k, "") for k in keys], row, rdr)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
