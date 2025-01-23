#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
Propagate known values down columns.
----------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2015-04-30
:Copyright: Skip Montanaro 2015-2021
:Copyright: TradeLink LLC 2015
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

%(PROG)s -k f1,f2,f3,... [ infile [ outfile ] ]

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

import argparse
import csv
import os
import sys

from csvprogs.common import usage

PROG = os.path.splitext(os.path.split(sys.argv[0])[1])[0]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--keys", dest="keys", required=True)
    (options, args) = parser.parse_known_args()
    if options.keys:
        options.keys = options.keys.split(",")

    if len(args) > 2:
        print(usage(__doc__, globals(), msg="Too many input files"),
              file=sys.stderr)
        return 1

    inf = open((args[0] if args else "/dev/stdin"), "r")
    outf = open((args[1] if len(args) > 1 else "/dev/stdout"), "w")
    rdr = csv.DictReader(inf)
    wtr = csv.DictWriter(outf, fieldnames=rdr.fieldnames, restval="")
    wtr.writeheader()

    last = {}
    for row in rdr:
        for k in options.keys:
            if not row[k]:
                row[k] = last.get(k, "")
        wtr.writerow(row)
        last = row
    return 0

if __name__ == "__main__":
    sys.exit(main())
