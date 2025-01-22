#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
Extract fields from a CSV file, generate another
----------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2013-07-19
:Copyright: TradeLink LLC 2013
:Copyright: Skip Montanaro, 2013-2021
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

 %(PROG)s -f f1,f2,f3,... [ options ] [ infile [ outfile ] ]

OPTIONS
=======

-f names   comma-separated list of field names to dump
-n [style] with no argument, don't quote fields, otherwise use the specified
           value
-D         don't use DOS/Windows line endings
-a         append rows to output file (no header is written)

if given, infile specifies the input CSV file (default: stdin)
if given, outfile specifies the output CSV file (default: stdout)

DESCRIPTION
===========

Transform a CSV file into another form, adjusting the fields
displayed, field quoting, field separators, etc.

EXAMPLE
=======

Extract just the time and price fields from a larger input file,
using Unix line endings, and leaving fields unquoted::

  csv2csv -n -D -f time,price < somefile.csv > anotherfile.csv

If a field name is present in the argument to -f, but not present
in the infile, it will still be emitted to the output, but all
values will be blank.

SEE ALSO
========

* csvmerge
* csvsort
* xls2csv
* data_misc package
"""

import argparse
import csv
import os
import sys

from csvprogs.common import CSVArgParser, openio

PROG = os.path.split(sys.argv[0])[1]

def usage(msg=None):
    if msg is not None:
        print(msg, file=sys.stderr)
        print(file=sys.stderr)
    print((__doc__.strip() % globals()), file=sys.stderr)

# pylint: disable=too-few-public-methods
class QuoteAction(argparse.Action):
    "Custom action for quote style"
    # Keys are possible values used on cmdline.
    quotes = {
        'QUOTE_ALL': csv.QUOTE_ALL,
        'QUOTE_MINIMAL': csv.QUOTE_MINIMAL,
        'QUOTE_NONE': csv.QUOTE_NONE,
        'QUOTE_NONNUMERIC': csv.QUOTE_NONNUMERIC,
        'ALL': csv.QUOTE_ALL,
        'MINIMAL': csv.QUOTE_MINIMAL,
        'NONE': csv.QUOTE_NONE,
        'NONNUMERIC': csv.QUOTE_NONNUMERIC,
        str(csv.QUOTE_ALL): csv.QUOTE_ALL,
        str(csv.QUOTE_MINIMAL): csv.QUOTE_MINIMAL,
        str(csv.QUOTE_NONE): csv.QUOTE_NONE,
        str(csv.QUOTE_NONNUMERIC): csv.QUOTE_NONNUMERIC,
        int(csv.QUOTE_ALL): csv.QUOTE_ALL,
        int(csv.QUOTE_MINIMAL): csv.QUOTE_MINIMAL,
        int(csv.QUOTE_NONE): csv.QUOTE_NONE,
        int(csv.QUOTE_NONNUMERIC): csv.QUOTE_NONNUMERIC,
        }

    def __call__(self, parser, namespace, value, option_string=None):
        val = self.quotes[value] if value else csv.QUOTE_NONE
        setattr(namespace, self.dest, val)

def csv2csv(reader, writer, fields):
    "copy the named fields from the CSV reader to the CSV writer"
    try:
        for inrow in reader:
            outrow = {}
            for field in fields:
                outrow[field] = inrow.get(field, "")
            writer.writerow(outrow)
    except IOError:
        pass


def main():
    parser = CSVArgParser()
    parser.add_argument("-f", "--fields", dest="fields", default=None,
                        help="fields to copy from input to output")
    parser.add_argument("-n", "--quote", dest="quote_style", nargs='?',
                        action=QuoteAction, default=csv.QUOTE_ALL,
                        const=csv.QUOTE_NONE,
                        help="quoting style used when writing output")
    parser.add_argument("-D", "--newline", dest="terminator", default="\r\n",
                        action="store_const", const="\n",
                        help="use Unix line endings instead of Windows")
    (options, args) = parser.parse_known_args()
    options.fields = options.fields.split(",") if options.fields else []

    if len(args) > 2:
        usage(args[0])

    # pylint: disable=too-few-public-methods
    class outdialect(csv.excel):
        "user-defined values for several output csv params"
        delimiter = options.outsep
        quoting = options.quote_style
        escapechar = '\\'
        lineterminator = options.terminator

    mode = "a" if options.append else "w"
    with openio(args[0] if len(args) >= 1 else sys.stdin, "r",
                args[1] if len(args) == 2 else sys.stdout, mode,
                encoding=options.encoding) as (inf, outf):
        reader = csv.DictReader(inf, delimiter=options.insep)
        if not options.fields:
            # All by default
            options.fields = reader.fieldnames
        writer = csv.DictWriter(outf, options.fields, dialect=outdialect,
            extrasaction='ignore')
        if not options.append:
            writer.writeheader()
        csv2csv(reader, writer, options.fields)

    return 0

if __name__ == "__main__":
    try:
        result = main()
    except BrokenPipeError:
        result = 0
    sys.exit(result)
