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

import csv
import sys
import os

from csvprogs.common import CSVArgParser, openio, usage

PROG = os.path.split(sys.argv[0])[1]

def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("-k", "--keys", required=True,
                        help="column(s) to use as keys for the merge/collapse")
    options, args = parser.parse_known_args()

    keys = tuple(options.keys.split(","))

    last = ()
    result = {}

    mode = "a" if options.append else "w"
    with openio(args[0] if len(args) >= 1 else sys.stdin, "r",
                args[1] if len(args) == 2 else sys.stdout, mode,
                encoding=options.encoding) as (inf, outf):
        reader = csv.DictReader(inf, delimiter=options.insep)
        writer = csv.DictWriter(outf, fieldnames=reader.fieldnames,
            delimiter=options.outsep)
        if not options.append:
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
