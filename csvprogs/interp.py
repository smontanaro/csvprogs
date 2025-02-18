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

import os
import sys

import numpy as np
import pandas as pd

from csvprogs.common import CSVArgParser, openpair, usage


PROG = os.path.split(sys.argv[0])[1]

def main():
    "see __doc__"

    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("-f", "--field", required=True,
                        help="column to interpolate")
    parser.add_argument("-x", "--xaxis", required=True,
                        help="date/time column")
    options, args = parser.parse_known_args()

    with openpair(options, args) as (inf, outf):
        header = next(inf).strip().split(options.insep)
        dtype = {
            options.field: float,
        }
        for col in header:
            if col not in (options.xaxis, options.field):
                dtype[col] = str
        frame = pd.read_csv(inf, dtype=dtype, names=header,
                            parse_dates=[options.xaxis])
        frame.index = frame[options.xaxis]
        field_data = frame[[options.field]]
        field_data = field_data.resample("D").mean().interpolate()
        del frame[options.field]
        frame = field_data.join(frame, how="outer")
        del frame[options.xaxis]
        frame = frame.reset_index()
        frame = frame.replace(np.nan, "")
        frame.to_csv(outf, index=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
