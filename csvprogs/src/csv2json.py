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
-i sep     alternate input field separator (default is a comma)
-t types   comma-separated list of types for the input data - valid
           values are 'int', 'float', 'date', 'time', 'datetime', 'str'.
           If given, length of this list must match the length of the
           names list given by -f (or implicit in the file itself).
-a         emit rows as arrays, not dicts - array elements will be ordered
           by order of field names on input.
-H         emit header if -a was given.

If -f isn't given, all fields in the CSV file will be dumped.

if given, infile specifies the input CSV file (default: stdin)
if given, outfile specifies the output CSV file (default: stdout)

DESCRIPTION
===========

Read a CSV file and write it in JSON form.

EXAMPLE
=======

Extract just the time and price fields from a CSV file.

  csv2json -f time,price -t datetime,int < somefile.csv > somefile.json

Generate a Python list of lists from the input CSV file.

  csv2json -a -H < somefile.csv

(This might be handy for generating unit test data from CSV
files. Just sayin'...)

SEE ALSO
========

* csv2csv
"""

import argparse
import csv
import json
import os
import sys

import dateutil.parser

PROG = os.path.split(sys.argv[0])[1]

def usage(msg=None):
    if msg is not None:
        print(msg, file=sys.stderr)
        print(file=sys.stderr)
    print((__doc__.strip() % globals()), file=sys.stderr)

def datetime(s):
    dt = dateutil.parser.parse(s)
    return "new Date(%d, %d, %d, %d, %d, %d, %d)" % (
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second,
        int(round(dt.microsecond / 1000)))
date = time = datetime

TYPES = {
    'int': int,
    'float': float,
    'date': date,
    'time': time,
    'datetime': datetime,
    'str': str,
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fields", dest="inputfields", default=None,
                        help="fields to emit (default all fields)")
    parser.add_argument("-t", "--types", dest="typenames", default=None,
                        help="type converters for emitted fields")
    parser.add_argument("-i", "--insep", dest="insep", default=",",
                        help="input field separator (default ',')")
    parser.add_argument("-a", "--array", dest="emit_arrays", default=False,
                        action="store_true",
                        help="emit arrays instead of objects")
    parser.add_argument("-H", "--header", dest="array_header", default=False,
                        action="store_true",
                        help="when emitting arrays, also emit a header array")

    (options, args) = parser.parse_known_args()
    options.inputfields = (options.inputfields.split(",")
                               if options.inputfields
                               else [])
    options.typenames = (options.typenames.split(",")
                               if options.typenames
                               else [])

    if len(args) > 2:
        usage(sys.argv[0])
        return 1

    if len(args) >= 1:
        inf = open(args[0], "r")
    else:
        inf = sys.stdin
    if len(args) == 2:
        outf = open(args[1], "w")
    else:
        outf = sys.stdout

    reader = csv.DictReader(inf, delimiter=options.insep)
    if not options.inputfields:
        options.inputfields = reader.fieldnames

    if options.typenames:
        if len(options.typenames) != len(options.inputfields):
            usage("Length of type names (-t) and field names (-f) must match.")
            return 1
        options.typenames = {
            i: TYPES[t]
                for (i, t) in zip(options.inputfields, options.typenames)
        }
    return translate(reader, options, outf)

def translate(reader, options, outf):
    "Convert reader input to JSON output."

    try:
        outf.write("[\n")
        if options.emit_arrays and options.array_header:
            outf.write(" " * 4)
            json.dump(options.inputfields, outf)
            outf.write(",\n")
        for row in reader:
            if options.typenames:
                for k in options.inputfields:
                    row[k] = options.typenames[k](row[k])
            outrow = dict((k, v)
                              for (k, v) in row.items()
                                  if k in options.inputfields)
            if options.emit_arrays:
                outrow = [outrow[k] for k in options.inputfields]
            outf.write(" " * 4)
            json.dump(outrow, outf)
            outf.write(",\n")
        outf.write("]\n")
    except IOError:
        pass
    return 0

if __name__ == "__main__":
    sys.exit(main())
