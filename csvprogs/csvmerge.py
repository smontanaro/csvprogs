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
-d fields    normalize fields as date
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

# TODO: should format date/time objects on output so variable input date/time
# formats work.

from contextlib import suppress
import datetime
import sys
import csv
import os

import dateutil.parser
# Create a trivial guess_... function in common?
from pandas.tseries.api import guess_datetime_format

from csvprogs.common import CSVArgParser, usage


PROG = os.path.split(sys.argv[0])[1]

# Given the recent craziness in the US gov't, maybe EPOCH should be 1875-05-20, e.g.,
#   https://www.dailykos.com/stories/2025/2/14/2303889/-Nope-There-are-no-150-year-olds-on-Social-Security-It-s-COBOL
EPOCH = datetime.datetime.fromtimestamp(0)


def main():
    parser = CSVArgParser()
    parser.add_argument("-k", "--keys", dest="keys", default="",
                        help="merge fields")
    parser.add_argument("-d", "--date-keys", dest="date_keys",
                        default="", help="normalize fields as dates")
    # maybe into CSVArgParser?
    parser.add_argument("-F", "--date-format", dest="format",
                        default="%Y-%m-%dT%H:%M",
                        help="output datetime format")
    (options, args) = parser.parse_known_args()

    keys = options.keys.split(",")
    readers = []
    if options.date_keys:
        date_keys = set(options.date_keys.split(","))
    else:
        date_keys = set()

    if len(args) < 1:
        print(usage(__doc__, globals(), "At least one input file is required."),
              file=sys.stderr)
        return 1

    all_fields = set()
    for fname in args:
        with open(fname, encoding="utf-8") as fp:
            rdr = csv.DictReader(fp)
            all_fields |= set(rdr.fieldnames)
            readers.append(iter(list(rdr)))

    rest = sorted(all_fields - set(keys))

    out_fields = keys + sorted(rest)

    writer = csv.DictWriter(sys.stdout, fieldnames=out_fields, restval="")
    writer.writeheader()

    return merge(keys, date_keys, readers, writer, options.format)

def merge(keys, date_keys, readers, writer, default_format):
    "merge rows from all readers, sending to writer"

    formats = set()
    if default_format:
        formats.add(default_format)

    def construct_key(row, keys, date_keys):
        "helper"
        key = []
        for k in keys:
            v = row.get(k, "")
            if k in date_keys:
                if v:
                    formats.add(guess_datetime_format(v))
                    v = dateutil.parser.parse(v)
                    row[k] = v
                else:
                    # Comparison will still fail if the key is
                    # missing, so substitute epoch for empty
                    # string.
                    v = EPOCH
            key.append(v)
        return key

    rows = {}
    # Populate dict of readers with the first row from each.
    for rdr in readers:
        try:
            row = next(rdr)
        except StopIteration:
            pass
        else:
            key = construct_key(row, keys, date_keys)
            rows[rdr] = (key, sorted(row.items()), rdr)

    format = formats.pop()
    while True:
        if not rows:
            return 0

        _, row, rdr = min(rows.values(), key=lambda x: x[0])
        # Back to dict form for writing...
        row = dict(row)
        for k in date_keys:
            row[k] = row[k].strftime(format)
        writer.writerow(row)

        # Fill in the now stale slot with the next row.
        try:
            row = next(rdr)
        except StopIteration:
            del rows[rdr]
        else:
            key = construct_key(row, keys, date_keys)
            rows[rdr] = (key, sorted(row.items()), rdr)
    return 0

if __name__ == "__main__":
    with suppress((KeyboardInterrupt, BrokenPipeError)):
        sys.exit(main())
