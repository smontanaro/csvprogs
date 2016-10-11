#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
Propagate known values down columns.
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2015-04-30
:Copyright: TradeLink LLC 2015
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

 %(PROG)s -k f1,f2,f3,... [ options ] [ infile ]

OPTIONS
=======

-k fields   columns whose values should be filled.

EXAMPLE
=======

When merging columns from two CSV files, you will often generate rows
with missing values. For example, if first.csv is::

    time,close
    2015-04-15T15:00,26.98
    2015-04-16T15:00,27.04
    2015-04-17T15:00,27.77

and second.csv is::

    time,position
    2015-04-15T12:00,1
    2015-04-15T12:30,-1
    2015-04-15T12:45,1
    2015-04-15T14:45,-1
    2015-04-16T09:30,1

after merging them on the time field we have::

    time,close,position
    2015-04-15T12:00,,1
    2015-04-15T12:30,,-1
    2015-04-15T12:45,,1
    2015-04-15T14:45,,-1
    2015-04-15T15:00,26.98,
    2015-04-16T09:30,,1
    2015-04-16T15:00,27.04,
    2015-04-17T15:00,27.77,

%(PROG)s fills in missing values on the named columns.  For example,
executing::

    csvmerge -k time first.csv second.csv | %(PROG)s -k position

the output is::

    time,close,position
    2015-04-15T12:00,,1
    2015-04-15T12:30,,-1
    2015-04-15T12:45,,1
    2015-04-15T14:45,,-1
    2015-04-15T15:00,26.98,-1
    2015-04-16T09:30,,1
    2015-04-16T15:00,27.04,1
    2015-04-17T15:00,27.77,1

SEE ALSO
========

* csv2csv
* csvmerge
"""

import sys
import csv
import getopt
import os

PROG = os.path.splitext(os.path.split(sys.argv[0])[1])[0]

def usage(msg=None):
    if msg is not None:
        print >> sys.stderr, msg
        print >> sys.stderr
    print >> sys.stderr, (__doc__.strip() % globals())

def main(args):
    keys = []

    try:
        opts, args = getopt.getopt(args, "k:h")
    except getopt.GetoptError, msg:
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
    rdr = csv.DictReader(f)
    fields = rdr.fieldnames
    wtr = csv.DictWriter(sys.stdout, fieldnames=fields, restval="")
    wtr.writerow(dict(zip(fields, fields)))

    last = {}
    for row in rdr:
        for k in keys:
            if not row[k]:
                row[k] = last.get(k, "")
        wtr.writerow(row)
        last = row
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
