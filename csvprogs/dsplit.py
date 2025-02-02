#!/usr/bin/env python3

"""
===========
%(PROG)s
===========

------------------------------------------------------------
split CSV on dates, generating new CSV with multiple columns
------------------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2024-11-28
:Copyright: Skip Montanaro 2024
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

  %(PROG)s [ -f field ] [ -o field ] [ -p pattern ] [ -S pattern ]

OPTIONS
=======

-f field          split this field (not present in the output)
--output field    new output field name
-p pattern        split pattern on the input field (using strptime(3) format
                  specifiers, default: %Y-%m-%d)
-S pattern        output pattern (default: |%Y|%m-%d - see details below)
-t field          scatter this field over the new output columns (no default)

DESCRIPTION
===========

Data are read from stdin, the relevant field is parsed, the split into
two parts. The input pattern is used to construct datetime objects
using date.strptime() format codes. The output pattern is similar, but
uses date.strftime() format codes and has an introductory character
which is used to define the two parts of the date split.

To construct the output the entire input must be held in memory. Keep
that in mind if processing large CSV files.

OUTPUT FORMAT
=============

On output, the parsed datetime object is used to generate two values,
the value for the output field and the values for output columns. The
first character indicates how the two-part pattern is to be split. For
instance, a pattern of "|%Y|%m-%d" would split the datetime object
into a year (column header) and day (row). Using that pattern and an
output field name of "day", this CSV file:

date,weight
2020-01-03,183.4
2020-01-04,183.0
2020-01-05,182.0
2020-01-06,181.0
2021-01-03,181.4
2021-01-04,179.0
2021-01-05,180.0
2021-01-06,181.0
2022-01-03,185.4
2022-01-04,184.4
2022-01-05,187.4
2022-01-06,182.6
2023-01-03,191.6
2023-01-04,191.0
2023-01-05,191.2
2023-01-06,190.6
2024-01-03,190.4
2024-01-04,187.6
2024-01-05,187.8
2024-01-06,189.8

would be converted to this CSV file:

day,2020,2021,2022,2023,2024
01-03,183.4,181.4,185.4,191.6,190.4
01-04,183.0,179.0,184.4,191.0,187.6
01-05,182.0,180.0,187.4,191.2,187.8
01-06,181.0,181.0,182.6,190.6,189.8
"""

import csv
import datetime
import os
import sys

from csvprogs.common import CSVArgParser, usage, openio
PROG = os.path.basename(sys.argv[0])

def main():
    # haven't figured out what isn't fine with stuff like %%Y...
    parser = CSVArgParser()#usage=usage(__doc__, globals()))
    parser.add_argument("--field", "-f", default="date",
                        help="date field to split")
    parser.add_argument("--output", default="day",
                        help="output key name")
    parser.add_argument("--column", "-c", required=True,
                        help="column value to copy to the output")
    parser.add_argument("--pattern", "-p", default="%Y-%m-%d",
                        help="date pattern")
    parser.add_argument("--split", "-S", default="|%Y|%m-%d",
                        help="how to split date arg into column and row names")
    options, args = parser.parse_known_args()

    mode = "a" if options.append else "w"
    with openio(args[0] if len(args) >= 1 else sys.stdin, "r",
                args[1] if len(args) == 2 else sys.stdout, mode,
                encoding=options.encoding) as (inf, outf):
        reader = csv.DictReader(inf, delimiter=options.insep)
        rows = list(reader)

        major = {}
        columns = set()

        first, second = options.split[1:].split(options.split[0])
        for row in rows:
            dt = datetime.datetime.strptime(row[options.field], options.pattern)
            colname = str(dt.strftime(first))
            rowname = str(dt.strftime(second))
            columns.add(colname)
            if rowname not in major:
                major[rowname] = {
                    options.output: rowname,
                }
            major[rowname][colname] = row[options.column]
        fieldnames = [options.output]
        fieldnames.extend(sorted(columns))
        wtr = csv.DictWriter(outf, fieldnames=fieldnames,
            delimiter=options.outsep)
        wtr.writeheader()
        for row in sorted(major):
            wtr.writerow(major[row])

if __name__ == "__main__":
    sys.exit(main())
