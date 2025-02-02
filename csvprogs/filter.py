#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
Filter input values based upon user-defined function
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

 %(PROG)s -f lambda [ -k name ] [ infile [ outfile ] ]

OPTIONS
=======

-f lambda   Python lambda expression which takes the row (split into
            fields) to use as the filter - returns True to print the row,
            False to discard it.
-k name     If given, the return value of the lambda function will be
            associated with this key in the output (if input has a
            header). If given but the input has no header, the return
            value will simply be appended to the output.

DESCRIPTION
===========

Data are read from the given input file or stdin.  Each row is passed to the
user-provided lambda expression.  If it returns True, the row is printed to the
output file (or stdout).  If it returns False, the row is discarded.  Fields
which look like numbers will be converted automatically.

Example:

If example.csv contains these rows::

    20120620T14:37:30.25882,$LIQF2,5.51495000,TRD,0,b=0
    20120620T14:37:31.25848,$LIQF2,4.23667000,TRD,0,b=1
    20120620T19:52:24.40244,$LIQF2,3.90499000,TRD,0,b=0
    20120620T19:52:25.40252,$LIQF2,3.89785000,TRD,0,b=1
    20120626T08:55:52.75992,$LIQF2,69.29036000,TRD,0,b=1
    20120626T08:55:53.76004,$LIQF2,65.65485000,TRD,0,b=0
    20120626T08:55:54.75964,$LIQF2,61.83906000,TRD,0,b=1
    20120626T08:55:55.75970,$LIQF2,59.46307000,TRD,0,b=0

this command::

    filter -f 'lambda row: row[-1] != "b=1"' < example.csv

will emit only the rows where the batch flag is zero.

If example.csv contains these rows and the -H flag was given on the
command line::

    time,symbol,price,type,age,batch
    20120620T14:37:30.25882,$LIQF2,5.51495000,TRD,0,b=0
    20120620T14:37:31.25848,$LIQF2,4.23667000,TRD,0,b=1
    20120620T19:52:24.40244,$LIQF2,3.90499000,TRD,0,b=0
    20120620T19:52:25.40252,$LIQF2,3.89785000,TRD,0,b=1
    20120626T08:55:52.75992,$LIQF2,69.29036000,TRD,0,b=1
    20120626T08:55:53.76004,$LIQF2,65.65485000,TRD,0,b=0
    20120626T08:55:54.75964,$LIQF2,61.83906000,TRD,0,b=1
    20120626T08:55:55.75970,$LIQF2,59.46307000,TRD,0,b=0

the first row will be treated as a header and the first logical row
passed to the user's lambda function will be a dictionary that looks
like this::

    {
     "time": "20120620T14:37:30.25882",
     "symbol": "$LIQF2",
     "price": 5.51495000,
     "type": "TRD",
     "age": 0,
     "batch": "b=0",
     0: "20120620T14:37:30.25882",
     1: "$LIQF2",
     2: 5.51495000,
     3: "TRD",
     4: 0,
     5: "b=0",
    }

Code in the lambda expression can thus access elements using list or
dictionary notation.  (Note that negative offsets such as x[-1] won't
work, however.)

This tool is obviously going to be slower than grep or sed, but offers
the user a lot more flexibility and if the user has Python experience
is probably easier to use than awk.

SEE ALSO
========

* nt
* pt
* bars
* take
* mpl
* avg
* sigavg
* mean
"""

import csv
import os
import sys

from csvprogs.common import type_convert, CSVArgParser, usage, openio


PROG = os.path.basename(sys.argv[0])


def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("-f", "--function", required=True,
                        help="Python lambda expression to use as row filter")
    parser.add_argument("-k", "--lambda-key", default="",
                        help="Result of lambda expression evaluation, if given")
    options, args = parser.parse_known_args()

    # pylint: disable=W0123
    func = eval(options.function)

    mode = "a" if options.append else "w"
    with openio(args[0] if len(args) >= 1 else sys.stdin, "r",
                args[1] if len(args) == 2 else sys.stdout, mode,
                encoding=options.encoding) as (inf, outf):
        reader = csv.DictReader(inf, delimiter=options.insep)
        fieldnames = reader.fieldnames[:]
        if options.lambda_key:
            if options.lambda_key in fieldnames:
                raise ValueError(f"{options.lambda_key} is already in {fieldnames}")
            fieldnames.append(options.lambda_key)
        writer = csv.DictWriter(outf, fieldnames=fieldnames, delimiter=options.outsep)
        if not options.append:
            writer.writeheader()

        for row in reader:
            type_convert_row(row)

            eff_row = row.copy()
            val = func(eff_row)
            if options.lambda_key:
                row[options.lambda_key] = val
            if val:
                writer.writerow(row)

    return 0


def type_convert_row(row):
    for k in row:
        row[k] = type_convert(row[k])


if __name__ == "__main__":
    sys.exit(main())
