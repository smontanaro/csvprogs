#!/usr/bin/env python

"""Interpolate missing values, preserving some amount of variance.

Usage: {PROG} -f field -x field [ input ]

-x field - x axis column (required)
-f field - y axis column (field to be interpolated - required)

If given, the input file is used, otherwise sys.stdin. Output is always to
sys.stdout.

Currently, all this does is linear interpolation. Variance-preserving
interpolation is TBD.

"""

import getopt
import os
import sys

import numpy as np
import pandas as pd

PROG = os.path.split(sys.argv[0])[1]

def usage(msg=None):
    "help user"
    if msg is not None:
        printe(msg)
        printe()
    printe(__doc__.strip().format(**globals()))

def main():
    "see __doc__"
    opts, args = getopt.getopt(sys.argv[1:], "hf:x:",
                               ["help", "field=", "xaxis=",])
    x_axis = None
    field = None
    for opt, arg in opts:
        if opt in ("--help", "-h"):
            usage()
            return 0
        if opt in ("-f", "--field"):
            field = arg
        elif opt in ("-x", "--xaxis"):
            x_axis = arg
    if field is None or x_axis is None:
        usage("-x and -f are both required.")
        return 1

    infile = open(args[0]) if args else sys.stdin
    header = next(infile).strip().split(",")
    dtype = {
        field: float,
    }
    for col in header:
        if col not in (x_axis, field):
            dtype[col] = str
    frame = pd.read_csv(infile, dtype=dtype, names=header,
                        parse_dates=[x_axis])
    frame.index = frame[x_axis]
    field_data = frame[[field]]
    field_data = field_data.resample("D").mean().interpolate()
    del frame[field]
    frame = field_data.join(frame, how="outer")
    del frame[x_axis]
    frame = frame.reset_index()
    frame = frame.replace(np.nan, "")
    frame.to_csv(sys.stdout, index=False)
    return 0

def printe(*args, file=sys.stderr, **kwds):
    "print, defaultint to stderr for output"
    return print(*args, file=file, **kwds)

if __name__ == "__main__":
    sys.exit(main())
