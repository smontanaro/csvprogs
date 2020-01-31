#!/usr/bin/env python

"""Interpolate missing values, preserving some amount of variance.

Usage: {PROG} -f field [ -n N ] [ -x field,value ] [ input ]

-f field - field to be interpolated
-x field,value - field with value to be ignored (if missing, see below)
-n N - number of previous samples to use when calculating variance.

If given, the input file is used, otherwise sys.stdin. Output is always to
sys.stdout.

Consider this simple CSV file:

date,weight,note
2019-08-03,187
2019-08-04,186.8
2019-08-05,187.4
2019-08-06,187
2019-08-07,187.8
2019-08-08,185.8
2019-08-09,186.6,after b'fast
2019-08-10,185.2
2019-08-11,186
2019-08-17,187.4
2019-08-18,185.2

We want to interpolate values for 2019-08-12 through 2019-08-16. With -n 0,
a simple mean (variance 0) between the preceding and following values with
be used:

date,weight,note
...
2019-08-10,185.2
2019-08-11,186
2019-08-12,186.23333333333335
2019-08-13,186.46666666666667
2019-08-14,186.7
2019-08-15,186.93333333333334
2019-08-16,187.16666666666669
2019-08-17,187.4
2019-08-18,185.2

The -x flag serves two purposes. First, if the given field has the stated
value, it will be skipped. Second, when writing out interpolated values,
that field will be populated with the given value. Thus, adding

    -x note,interpolated

to the previous example, we'd see:

date,weight,note
...
2019-08-10,185.2
2019-08-11,186
2019-08-12,186.23333333333335,interpolated
2019-08-13,186.46666666666667,interpolated
2019-08-14,186.7,interpolated
2019-08-15,186.93333333333334,interpolated
2019-08-16,187.16666666666669,interpolated
2019-08-17,187.4
2019-08-18,185.2

insuring that further runs would avoid using those interpolated values as
inputs when computing recent variance.

Consider the original CSV file, but with a value of 5 given as the argument
to -n. When interpolating values, a normal distribution with mean 0 and
standard deviation of the previous N values will be sampled. The simple
interpolated value as above will be augmented with the corresponding
sample. While the result will be different for different runs, here is an
example with -n 5:

date,weight,note
...
2019-08-10,185.2
2019-08-11,186
2019-08-12,186.65488823164566,interpolated
2019-08-13,186.4387491966378,interpolated
2019-08-14,186.32154210926754,interpolated
2019-08-15,185.75948522232295,interpolated
2019-08-16,186.29836923023845,interpolated
2019-08-17,187.4
2019-08-18,185.2

"""

import csv
import getopt
import os
import random
import statistics
import sys

PROG = os.path.split(sys.argv[0])[1]

def usage(msg=None):
    "help user"
    if msg is not None:
        printe(msg)
        printe()
    printe(__doc__.strip().format(**globals()))

def main():
    "see __doc__"
    opts, args = getopt.getopt(sys.argv[1:], "hf:n:x:",
                               ["help", "field=", "samples=", "extra="])
    field = None
    nsamples = 5
    extra = {}
    for opt, arg in opts:
        if opt in ("--help", "-h"):
            usage()
            return 0
        if opt in ("-f", "--field"):
            field = arg
        elif opt in ("-n", "--samples"):
            nsamples = int(arg)
        elif opt in ("-x", "--extra"):
            exname, exval = arg.split(",", 1)
            extra = {"field": exname, "value": exval}
    if field is None:
        usage("-f is required.")
        return 1

    printe("field:", field)
    printe("nsamples:", nsamples)
    printe("extra:", extra)

    infile = open(args[0]) if args else sys.stdin

    rdr = csv.DictReader(infile)
    rows = list(rdr)
    # Try to first convert field to date, default to float.
    for row in rows:
        try:
            row[field] = datetime.datetime.strptime(row[field], "%Y-%m-%d")
        except ValueError:
            row[field] = float(row[field])

    printe(f"{len(rows)} rows read")
    if extra:
        exrows = [row for row in rows
                    if row[extra["field"]] == extra["value"]]
        printe(f"{len(exrows)} rows will not be used")

    rows = interpolate(rows, field, nsamples, extra)
    wtr = csv.DictWriter(sys.stdout, fieldnames=rdr.fieldnames)
    wtr.writeheader()
    wtr.writerows(rows)
    return 0

class MaxList:
    "like a list, but limited in length"
    def __init__(self, maxlen):
        assert maxlen >= 0
        self.maxlen = maxlen
        self._values = []

    def append(self, val):
        "tack on a value, possibly trimming at front."
        self._values.append(val)
        while len(self._values) > maxlen:
            del self._values[0]

    def values(self):
        return self._values[:]

def interpolate(rows, field, nsamples, extra):
    "do the hard work"
    values = MaxList(nsamples)
    # Need at least two non-interpolated values at the start to determine
    # interval. We also assume the rows are monotonically increasing by the
    # field.
    interval = rows[1][field] - rows[0][field]
    for (i, row) in enumerate(rows):
        if extra and row[extra["field"]] == extra["value"]:
            # This is a value to interpolate.

    return rows

def printe(*args, file=sys.stderr, **kwds):
    "print, defaultint to stderr for output"
    return print(*args, file=file, **kwds)

if __name__ == "__main__":
    sys.exit(main())
