#!/usr/bin/env python

"""===========
%(PROG)s
===========

-------------------------------------------------------
compute linear regression of two user-specified fields
-------------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2014-01-13
:Copyright: TradeLink LLC 2014
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -c ] [ -f x,y ] [ -s sep ] [ -o col ]

OPTIONS
=======

-f x,y   use columns x and y as inputs to regression.
-s sep   use sep as the field separator (default is comma)
-o col   write to column col - if not given, just append to output
-c       only print correlation coefficient to stdout, no regression data

DESCRIPTION
===========

Data are read from stdin, the regression is computed, the the input is
written to stdout with the new field.  Details about the regression
results are written to stderr (unless -c is given).

SEE ALSO
========

* take
* mpl
* avg
* sigavg
"""

from __future__ import absolute_import
from __future__ import print_function
import sys
import getopt
import os
import csv

import scipy.stats
from six.moves import zip

PROG = os.path.basename(sys.argv[0])

def main(args):
    try:
        opts, args = getopt.getopt(args, "f:s:ho:c")
    except getopt.GetoptError:
        usage()
        return 1

    corr = False
    sep = ","
    field1 = 0
    field2 = 1
    field3 = 2
    for opt, arg in opts:
        if opt == "-f":
            try:
                field1, field2 = [int(x) for x in arg.split(",")]
            except ValueError:
                # Must have given names
                field1, field2 = arg.split(",")
        elif opt == "-o":
            try:
                field3 = int(arg)
            except ValueError:
                # Must have given names
                field3 = arg
        elif opt == "-c":
            corr = True
        elif opt == "-s":
            sep = arg
        elif opt == "-h":
            usage()
            return 0

    writer_type = type(csv.writer(sys.stdout))
    if isinstance(field1, int):
        reader = csv.reader(sys.stdin, delimiter=sep)
        writer = csv.writer(sys.stdout, delimiter=sep)
    else:
        reader = csv.DictReader(sys.stdin, delimiter=sep)
        names = reader.fieldnames[:]
        names.append(str(field3))
        writer = csv.DictWriter(sys.stdout, fieldnames=names, delimiter=sep)

    x = []
    y = []

    rows = list(reader)
    for row in rows:
        if row[field1] and row[field2]:
            row[field1] = float(row[field1])
            row[field2] = float(row[field2])
            x.append(row[field1])
            y.append(row[field2])

    (slope, intercept, r, p, stderr) = scipy.stats.linregress(x, y)

    if corr:
        print(r)
        return 0

    print("slope:", slope, "intercept:", intercept, file=sys.stderr)
    print("corr coeff:", r, "p:", p, "err:", stderr, file=sys.stderr)

    writer.writeheader()
    for row in rows:
        if row[field1]:
            val = slope * float(row[field1]) + intercept
            if isinstance(writer, writer_type):
                row.append(val)
            else:
                row[field3] = val
        writer.writerow(row)
    return 0

def usage():
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
