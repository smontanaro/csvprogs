#!/usr/bin/env python

"""
===========
{PROG}
===========

----------------------------------------------------
Compute exponentially weighted moving average
----------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  {PROG} [ -o name ] [ -f x ] [ -a val ] [ -s sep ] [ -m N ]

OPTIONS
=======

-a val   alpha of the ewma (default 0.1)
-f x     average the values in column x (no default)
-s sep   use sep as the field separator (default is comma)
-o name  define output column name (default: "ewma")
-m N     reset moving average after N missing values

DESCRIPTION
===========

Data are read from stdin, the ewma is computed, appended to the end of
the values, then printed to stdout.

SEE ALSO
========

* bars
* take
* mpl
* mvavg
"""


__all__ = ["ewma"]

import csv
import math
import os
import sys

from csvprogs.common import CSVArgParser, usage


PROG = os.path.basename(sys.argv[0])

def ewma(rdr, field, outcol, alpha, gap):
    "core moving average calculation: outcol = ewma(field)"
    nan = float('nan')
    val = nan
    missing = 0
    result = []

    # Trim trailing rows with empty string values for the field of
    # interest. This should keep us from spuriously continuing to produce
    # values after the useful end of the input.
    rows = list(rdr)
    extras = []
    while rows and rows[-1][field] == rdr.restval:
        # save these rows for later restoration
        extras.insert(0, rows[-1])
        del rows[-1]

    for row in rows:
        if not row[field] or math.isnan(float(row[field])):
            missing += 1
            if missing >= gap:
                val = nan
        else:
            missing = 0
            if math.isnan(val):
                val = float(row[field])
            else:
                val = alpha * float(row[field]) + (1-alpha) * val
        row[outcol] = val
        result.append(row)

    # Restore the rows we removed for the ewma calculation, for use
    # by downstream programs.
    result.extend(extras)

    return result

def main():
    parser = CSVArgParser()
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument("--outcol", default="ewma")
    parser.add_argument("-f", "--field", required=True)
    parser.add_argument("-m", "--gap", "--missing", dest="gap", default=5,
                        type=int)
    options, _args = parser.parse_known_args()

    if options.gap <= 0:
        print(usage(__doc__, globals(), "gap must be greater than zero"),
              file=sys.stderr)
        return 1

    rdr = csv.DictReader(sys.stdin, delimiter=options.insep, restval="")
    fnames = rdr.fieldnames[:]
    fnames.append(options.outcol)
    wtr = csv.DictWriter(sys.stdout, delimiter=options.outsep,
        fieldnames=fnames)
    wtr.writeheader()

    result = ewma(rdr, options.field, options.outcol, options.alpha,
        options.gap)
    wtr.writerows(result)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, KeyboardInterrupt):
        sys.exit(0)
