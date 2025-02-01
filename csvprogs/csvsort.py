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

::

-k fields   list merge fields (quote if names contain spaces)
-s          strip fields in the sort key function (data are not changed)

An optional input file can be given on the command line.  If not
given, input is read from stdin.  Output is to stdout.  Column order
remains unchanged on output.

EXAMPLE
=======

To sort stdin by date and time::

    %(PROG)s -k 'Date Stamp,Time Stamp'
"""

from contextlib import suppress
import sys
import csv
import os

from csvprogs.common import CSVArgParser, openio, usage


PROG = os.path.basename(sys.argv[0])


def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("-k", "--keys", required=True,
                        help="sort keys")
    parser.add_argument("-s", "--strip", default=False, action='store_true',
                        help="strip values in key function")
    options, args = parser.parse_known_args()

    options.keys = options.keys.split(",")

    def keyfunc(x):
        return [(x[k].strip() if options.strip else x[k]) for k in options.keys]

    mode = "a" if options.append else "w"
    with openio(args[0] if len(args) >= 1 else sys.stdin, "r",
                args[1] if len(args) == 2 else sys.stdout, mode,
                encoding=options.encoding) as (inf, outf):
        reader = csv.DictReader(inf, delimiter=options.insep)
        writer = csv.DictWriter(outf, fieldnames=reader.fieldnames, delimiter=options.outsep)
        if not options.append:
            writer.writeheader()
        writer.writerows(sorted(reader, key=keyfunc))

    return 0

if __name__ == "__main__":
    with suppress((BrokenPipeError, KeyboardInterrupt)):
        sys.exit(main())
