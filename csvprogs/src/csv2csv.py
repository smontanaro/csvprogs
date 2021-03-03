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
-F names   comma-separated list of field names to use for files without a header line
-o sep     alternate output field separator (default is a comma)
-i sep     alternate input field separator (default is a comma)
-n         don't quote fields
-D         don't use DOS/Windows line endings
-H         do not emit the header line

if given, infile specifies the input CSV file (default: stdin)
if given, outfile specifies the output CSV file (default: stdout)

DESCRIPTION
===========

Transform a CSV file into another form, adjusting the fields
displayed, field quoting, field separators, etc.

EXAMPLE
=======

Extract just the time and price fields from a larger input file,
stripping the header, using Unix line endings, and leaving fields
unquoted::

  csv2csv -n -H -D -f time,price < somefile.csv > anotherfile.csv

If a field name is present in the argument to -f or -F, but not
present in the infile, it will still be emitted to the output, but all
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
        }

    def __init__(self, option_strings, dest, nargs='?', **kwargs):
        if nargs != '?':
            raise ValueError("nargs must be '?'")
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        val = self.quotes[value] if value else csv.QUOTE_NONE
        setattr(namespace, self.dest, val)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fields", dest="fields", default=None)
    parser.add_argument("-F", "--headers", dest="headers", default=None)
    parser.add_argument("-i", "--insep", dest="insep", default=",")
    parser.add_argument("-o", "--outsep", dest="outsep", default=",")
    parser.add_argument("-H", "--noheader", dest="emitheader",
                        action="store_false", default=True)
    parser.add_argument("-n", "--quote", dest="quote_style", nargs='?',
                        action=QuoteAction, default=csv.QUOTE_ALL)
    parser.add_argument("-D", "--newline", dest="terminator", default="\r\n",
                        action="store_const", const="\n")
    parser.add_argument("-e", "--encoding", dest="encoding", default="utf-8")
    (options, args) = parser.parse_known_args()
    options.fields = options.fields.split(",") if options.fields else []
    options.headers = options.headers.split(",") if options.headers else []

    if len(args) > 2:
        usage(args[0])

    if len(args) >= 1:
        inf = open(args[0], "r", encoding=options.encoding)
    else:
        inf = sys.stdin
    if len(args) == 2:
        outf = open(args[1], "w")
    else:
        outf = sys.stdout

    # pylint: disable=too-few-public-methods
    class outdialect(csv.excel):
        "user-defined values for several output csv params"
        delimiter = options.outsep
        quoting = options.quote_style
        escapechar = '\\'
        lineterminator = options.terminator

    reader = csv.DictReader(inf, delimiter=options.insep)
    if not options.fields:
        # All by default
        options.fields = reader.fieldnames
    writer = csv.DictWriter(outf, options.fields, dialect=outdialect,
                            extrasaction='ignore')
    if options.emitheader:
        writer.writeheader()

    try:
        for inrow in reader:
            if options.fields != reader.fieldnames:
                outrow = {}
                for field in options.fields:
                    outrow[field] = inrow.get(field, "")
            else:
                outrow = inrow
            writer.writerow(outrow)
    except IOError:
        pass

    return 0

if __name__ == "__main__":
    sys.exit(main())
