#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
compute keltner channel
----------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2023-09-09
:Copyright: Skip Montanaro 2023
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -f x ] [ -n val ] [ -s sep ] [ -o name ]

OPTIONS
=======

-a x     get the atr from input column x (default "atr")
-e y     get the ewma from input column y (default "ewma")
-o name  prefix for output column (default "kc-")
-s sep   use sep as the field separator (default is comma)

DESCRIPTION
===========

Data are read from stdin, the indicator is computed and appended to the end of
the values, then printed to stdout.

The Keltner channel is defined here:

  https://www.investopedia.com/terms/k/keltnerchannel.asp

SEE ALSO
========

* mvavg
* ewma
* atr

"""

import csv
import getopt
import math
import os
import sys

PROG = os.path.basename(sys.argv[0])

def main():
    opts, _args = getopt.getopt(sys.argv[1:], "a:e:s:o:h")

    outpfx = "kc-"
    atrcol = "atr"
    emacol = "ewma"

    sep = ","
    for opt, arg in opts:
        if opt == "-e":
            emacol = arg
        elif opt == "-a":
            atrcol = arg
        elif opt == "-o":
            outpfx = arg
        elif opt == "-s":
            sep = arg
        elif opt == "-h":
            usage()
            return 0

    upper = outpfx + "upper"
    lower = outpfx + "lower"
    rdr = csv.DictReader(sys.stdin, delimiter=sep)
    fnames = rdr.fieldnames[:]
    fnames.append(upper)
    fnames.append(lower)
    wtr = csv.DictWriter(sys.stdout, delimiter=sep, fieldnames=fnames)
    wtr.writeheader()
    for row in rdr:
        atr = float(row.get(atrcol, "") or 'nan')
        ewma = float(row.get(emacol, "") or 'nan')
        if math.isnan(atr) or math.isnan(ewma):
            wtr.writerow(row)
            continue
        row[upper] = ewma + 2 * atr
        row[lower] = ewma - 2 * atr
        wtr.writerow(row)
    return 0

def usage(msg=None):
    if msg:
        print(msg, file=sys.stderr)
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main())
