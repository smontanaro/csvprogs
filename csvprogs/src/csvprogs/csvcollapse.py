#!/usr/bin/env python

"""
===============
%(PROG)s
===============

-------------------------------------------------------------
Collapse multiple rows having the same key into a single row
-------------------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2016-08-26
:Copyright: TradeLink LLC 2016
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

 %(PROG)s -k f1,f2,f3,...

OPTIONS
=======

-k names   comma-separated list of field names

DESCRIPTION
===========

For each row in stdin which has identical values for the given key(s),
collapse them into one row. Values in later rows overwrite values in
earlier rows. Output is to stdout. To be collapsed, rows with
identical key(s) must be adjacent to one another.

EXAMPLE
=======

Given this CSV file:

time,pos1,pos2,pos3
11:00,,-1,3
12:00,1,,1
12:00,,1,2

running csvcollapse -k time will emit this CSV file to stdout:

time,pos1,pos2,pos3
11:00,,-1,3
12:00,1,1,2

This program is often used to collapse rows with common keys in the
output of csvmerge.

SEE ALSO
========

* csvmerge
* csv2csv
"""

from __future__ import absolute_import
from __future__ import print_function
import csv
import sys
import getopt
import os

PROG = os.path.split(sys.argv[0])[1]

def usage(msg=None):
    if msg is not None:
        print(msg, file=sys.stderr)
        print(file=sys.stderr)
    print((__doc__.strip() % globals()), file=sys.stderr)

def main():
    keys = ()

    opts, _args = getopt.getopt(sys.argv[1:], "k:h")
    for opt, arg in opts:
        if opt == "-k":
            keys = tuple(arg.split(","))
        elif opt == "-h":
            usage()
            return 0

    last = ()
    result = {}
    reader = csv.DictReader(sys.stdin)
    writer = csv.DictWriter(sys.stdout, fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        row_key = []
        for k in keys:
            row_key.append(row.get(k))
        row_key = tuple(row_key)
        if row_key != last:
            last = row_key
            if result:
                writer.writerow(result)
                result.clear()
        for key in row:
            if row[key]:
                result[key] = row[key]

    if result:
        writer.writerow(result)
    return 0

if __name__ == "__main__":
    sys.exit(main())
