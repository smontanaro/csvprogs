#!/usr/bin/env python3

"""
DESCRIPTION
===========

Data are read from the input files, sorted on the key field (with duplicates
removed), then written to stdout. All input files must have the same column
names. If the non-key data in two rows which have the same key field value are
encountered, which one is written to stdout is undefined.

Suppose you want to download ten years of daily historical market data for a
stock from a website, but the site only allows you to download daily data for
no more than a five year range. You can download smaller (possibly overlapping)
chunks of data, then feed them into csvcat to generate a single file without
duplicate records.

EXAMPLE
=======

To concatenate and sort three files on their Date field:

csvcat -l Date A.csv B.csv C.csv

SEE ALSO
========

* csvmerge

"""

from contextlib import suppress
import csv
import sys

from csvprogs.common import CSVArgParser, usage


def cat(files, key):
    rows = []
    keys = set()
    for fn in files:
        with open(fn, encoding="utf-8") as inp:
            rdr = csv.DictReader(inp)
            fieldnames = rdr.fieldnames
            for row in rdr:
                if row[key] in keys:
                    continue
                keys.add(row[key])
                rows.append(row)
    rows.sort(key=lambda row: row[key])
    wtr = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    wtr.writeheader()
    wtr.writerows(rows)

def main():
    "see __doc__"
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("--key", "-k", required=True,
                        help="key field for the merge operation")
    parser.add_argument("files", nargs="+", help="list of input files")
    options = parser.parse_args()

    cat(options.files, options.key)

    return 0

if __name__ == "__main__":
    with suppress((BrokenPipeError, KeyboardInterrupt)):
        sys.exit(main())
