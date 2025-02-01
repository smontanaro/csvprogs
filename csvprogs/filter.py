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

 %(PROG)s -f lambda [ -s sep ] [ -k name ] [ -H ]

OPTIONS
=======

-s sep      use sep as the field separator (default is comma)
-f lambda   Python lambda expression which takes the row (split into
            fields) to use as the filter - returns True to print the row,
            False to discard it.
-H          Treat the first line as a header
-k name     If given, the return value of the lambda function will be
            associated with this key in the output (if input has a
            header). If given but the input has no header, the return
            value will simply be appended to the output.

DESCRIPTION
===========

Data are read from stdin.  Each row is passed to the user-provided
lambda expression.  If it returns True, the row is printed to stdout.
If it returns False, the row is discarded.  Fields which look like
numbers will be converted automatically.  Timestamps are kept as
strings.

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

import sys
import getopt
import os
import csv

PROG = os.path.basename(sys.argv[0])

def main():
    opts, args = getopt.getopt(sys.argv[1:], "f:s:hk:H")

    func = None
    sep = ","
    lambda_key = ""
    has_header = False
    for opt, arg in opts:
        if opt == "-s":
            sep = arg
        elif opt == "-f":
            func = eval(arg)
        elif opt == "-k":
            lambda_key = arg
        elif opt == "-H":
            has_header = True
        elif opt == "-h":
            usage()
            raise SystemExit

    if func is None:
        usage("lambda expression is required!")
        return 1

    rdr = csv.reader(sys.stdin)
    wtr = csv.writer(sys.stdout)
    first = next(rdr)
    indexes = None
    if has_header:
        # Treat first row as a header.
        if lambda_key:
            if lambda_key in first:
                raise ValueError("%r is already in %s" % (lambda_key, first))
            first.append(lambda_key)
        rdr = csv.DictReader(sys.stdin, fieldnames=first, restval="")
        wtr = csv.DictWriter(sys.stdout, fieldnames=first)
        wtr.writerow(dict(list(zip(first, first))))
        indexes = enumerate(first)

    for row in rdr:
        type_convert(row)

        if has_header:
            eff_row = row.copy()
            for index, key in indexes:
                eff_row[index] = eff_row[key]
            val = func(eff_row)
            if lambda_key:
                row[lambda_key] = val
                wtr.writerow(row)
            elif val:
                wtr.writerow(row)
        else:
            val = func(row)
            if lambda_key:
                row.append(val)
                wtr.writerow(row)
            elif val:
                wtr.writerow(row)

    return 0

def no_floats(row):
    for elt in row:
        try:
            float(elt)
        except ValueError:
            pass
        else:
            return False
    return True

def type_convert(row):
    if isinstance(row, dict):
        for k in row:
            row[k] = floatify(row[k])
    else:
        for i in range(len(row)):
            row[i] = floatify(row[i])

def floatify(val):
    try:
        val = int(val)
    except ValueError:
        try:
            val = float(val)
        except ValueError:
            pass
    return val

def usage(msg=""):
    if msg:
        print(msg, file=sys.stderr)
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main())
