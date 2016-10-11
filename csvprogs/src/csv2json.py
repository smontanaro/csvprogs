#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
Extract fields from a CSV file, output JSON
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
-i sep     alternate input field separator (default is a comma)
-t types   comma-separated list of types for the input data - valid
           values are 'int', 'float', 'date', 'time', 'datetime', 'str'.
           If given, length of this list must match the length of the
           names list (-f or -F).
-a         emit rows as arrays, not dicts - array elements will be ordered
           by order of field names on input.

One of -f or -F must be given.
if given, infile specifies the input CSV file (default: stdin)
if given, outfile specifies the output CSV file (default: stdout)

DESCRIPTION
===========

Read a CSV file and write it in JSON form.

EXAMPLE
=======

Extract just the time and price fields from a CSV file.

  csv2json -f time,price -t datetime,int < somefile.csv > somefile.json

SEE ALSO
========

* csv2csv
"""

from __future__ import division

import csv
import sys
import getopt
import os
import json

import dateutil.parser

PROG = os.path.split(sys.argv[0])[1]

def usage(msg=None):
    if msg is not None:
        print >> sys.stderr, msg
        print >> sys.stderr
    print >> sys.stderr, (__doc__.strip() % globals())

def main(args):
    insep = ','
    inputfields = []
    outputfields = []
    headers = []
    typenames = []
    emit_arrays = False

    try:
        opts, args = getopt.getopt(args, "i:f:F:t:ha")
    except getopt.GetoptError, msg:
        usage(msg)
        return 1

    for opt, arg in opts:
        if opt == "-f":
            inputfields = arg.split(",")
            outputfields.extend(inputfields)
        elif opt == "-t":
            typenames = arg.split(",")
        elif opt == "-F":
            headers.extend(arg.split(","))
        elif opt == "-i":
            insep = arg
        elif opt == "-h":
            usage()
            return 0
        elif opt == "-a":
            emit_arrays = True

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

    # cheap trick to get the title row for the dict reader...
    reader = csv.reader(inf, delimiter=insep)
    if headers:
        fields = headers
    else:
        fields = reader.next()

    if not inputfields:
        inputfields = outputfields = fields

    if typenames:
        if len(typenames) != len(inputfields):
            usage("Length of type names (-t) and field names (-f) must match.")
            return 1
        typenames = {i: eval(t) for (i, t) in zip(inputfields, typenames)}

    reader = csv.DictReader(inf, fields, delimiter=insep)

    try:
        rows = list(reader)
        if typenames:
            for row in rows:
                for k in row:
                    row[k] = typenames[k](row[k])
        if emit_arrays:
            for i in range(len(rows)):
                rows[i] = [rows[i][k] for k in fields]
        outf.write("[\n")
        for row in rows:
            json.dump(row, outf)
            outf.write(",\n")
        outf.write("]\n")
    except IOError:
        pass

    return 0

def datetime(s):
    dt = dateutil.parser.parse(s)
    return "new Date(%d, %d, %d, %d, %d, %d, %d)" % (
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second,
        int(round(dt.microsecond / 1000)))
date = time = datetime

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
