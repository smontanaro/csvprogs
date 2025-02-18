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
import math
import os
import sys

from csvprogs.common import CSVArgParser, openpair, usage


PROG = os.path.basename(sys.argv[0])

def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("--ewma", default="ewma",
                        help="column containing ewma values")
    parser.add_argument("--atr", default="atr",
                        help="column containing atr values")
    parser.add_argument("-p", "--prefix", default="kc-",
                        help="prefix for keltner output values")
    options, args = parser.parse_known_args()

    with openpair(options, args) as (inf, outf):
        reader = csv.DictReader(inf, delimiter=options.insep)

        upper = options.prefix + "upper"
        lower = options.prefix + "lower"
        fnames = reader.fieldnames + [upper, lower]
        writer = csv.DictWriter(outf, delimiter=options.outsep, fieldnames=fnames)
        if not options.append:
            writer.writeheader()
        for row in reader:
            atr = float(row.get(options.atr, "") or 'nan')
            ewma = float(row.get(options.ewma, "") or 'nan')
            if math.isnan(atr) or math.isnan(ewma):
                writer.writerow(row)
                continue
            row[upper] = ewma + 2 * atr
            row[lower] = ewma - 2 * atr
            writer.writerow(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
