#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
Extract fields from a CSV file, generate another
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-07-19
:Copyright: TradeLink LLC 2013
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

from __future__ import absolute_import
from __future__ import print_function
import csv
import sys
import getopt
import os
from six.moves import zip

PROG = os.path.split(sys.argv[0])[1]

def usage(msg=None):
    if msg is not None:
        print(msg, file=sys.stderr)
        print(file=sys.stderr)
    print((__doc__.strip() % globals()), file=sys.stderr)

def main(args):
    quote_style = csv.QUOTE_ALL
    escape_char = '\\'
    insep = outsep = ','
    inputfields = []
    outputfields = []
    terminator = "\r\n"
    emitheader = True
    headers = []

    try:
        opts, args = getopt.getopt(args, "o:i:f:F:DHnh")
    except getopt.GetoptError as msg:
        usage(msg)
        return 1

    for opt, arg in opts:
        if opt == "-f":
            inputfields = arg.split(",")
            outputfields.extend(inputfields)
        elif opt == "-F":
            headers.extend(arg.split(","))
        elif opt == "-o":
            outsep = arg
        elif opt == "-i":
            insep = arg
        elif opt == "-H":
            emitheader = False
        elif opt == "-n":
            quote_style = csv.QUOTE_NONE
        elif opt == "-D":
            terminator = "\n"
        elif opt == "-h":
            usage()
            return 0

    if len(args) > 2:
        usage(sys.argv[0])

    if len(args) >= 1:
        inf = open(args[0], "rb")
    else:
        inf = sys.stdin
    if len(args) == 2:
        outf = open(args[1], "wb")
    else:
        outf = sys.stdout

    class outdialect(csv.excel):
        delimiter = outsep
        quoting = quote_style
        escapechar = escape_char
        lineterminator = terminator

    # cheap trick to get the title row for the dict reader...
    reader = csv.reader(inf, delimiter=insep)
    if headers:
        fields = headers
    else:
        fields = next(reader)
    if not inputfields:
        inputfields = outputfields = fields
    reader = csv.DictReader(inf, fields, delimiter=insep)
    writer = csv.DictWriter(outf, outputfields, dialect=outdialect,
                            extrasaction='ignore')
    if emitheader:
        writer.writerow(dict(list(zip(outputfields, outputfields))))

    try:
        for inrow in reader:
            if fields != inputfields:
                outrow = {}
                for field in inputfields:
                    outrow[field] = inrow.get(field, "")
            else:
                outrow = inrow
            writer.writerow(outrow)
    except IOError:
        pass

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
