#!/usr/bin/env python

"""===============
%(PROG)s
===============

--------------------------------------------------------
Extract rows from CSV files matching stated constraints.
--------------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2022-04-06
:Copyright: © TradeLink LLC 2013, Skip Montanaro, 2022
:Version: 1.0
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

 %(PROG)s [ options ] expression

OPTIONS
=======

::

    -v - make output more verbose
    -h - display this help and exit

input is read from stdin, output written to stdout.

DESCRIPTION
===========

Filter an input CSV file, emitting rows to the output which match the
expression given on the command line.  Individual terms are specified
as::

  column RELOP expr

where RELOP is one of the usual Python binary operators or 'match'.
Terms can be joined together using "and" or "or".  Parentheses can be
used to direct order of evaluation.

'match' is used to specify a regular expression match. This term::

  column match pattern

is equivalent to::

  re.match(pattern, row[column], re.I)

Note that patterns are matched in a case-insensitive manner.

EXAMPLE
=======

Write rows from the input if the "contract" column equals "F:LGOV13"
and price > 96125 or price < 96000::

  %(PROG)s contract == F:LGOV13 and '(' price '>' 96125 or price '<' 96000 ')'

Write rows from a trading audit archive file corresponding to fills
for the user "zelenskyy"::

  %(PROG)s "User Name" == "zelenskyy" and \\
    'Source or Destination' == "From Exchange" and \\
    Transaction == "EXECUTION"

Note that characters which are special to the shell ("(", ")", "<",
and ">" in this case) must be quoted to protect them.  Values which
contain spaces must also be quoted.

DETAILS
=======

Under the covers, the script builds a Python function which compares
the user's expression against the values of a given row.  The first
example would generate a function like this::

    def compare_func(row):
        return ((row["contract"] == "F:LGOV13") and
                ((row["price"] > "96125" or row["price"] < "96000")))

The second example generates this function::

    def compare_func(row):
        return ((row["User Name"] == "zelenskyy") and
                (row["Source or Destination"] == "From Exchange") and
                (row["Transaction"] == "EXECUTION"))

LIMITATIONS
===========

* Note that comparisons are currently done as strings.  This is
  obviously suboptimal for many uses.
* The interaction of the constraint notation with shell quoting makes
  writing the expressions less intuitive than it should be.
* Should allow the user to specify a function defined in a Python
  file.

SEE ALSO
========

* csvmerge
* csvsort
* csv2csv
* data_misc package

"""

import csv
from locale import setlocale, LC_ALL
import os
import sys

from csvprogs.common import CSVArgParser, usage, type_convert


PROG = os.path.split(sys.argv[0])[1]

def main():
    parser = CSVArgParser(usage=usage("__doc__", globals()))
    options, args = parser.parse_known_args()

    setlocale(LC_ALL, options.locale)

    rdr = csv.DictReader(sys.stdin)
    func = build_compare_func(args, verbose=options.verbose, keys=rdr.fieldnames)
    wtr = csv.DictWriter(sys.stdout, fieldnames=rdr.fieldnames)
    if not options.append:
        wtr.writeheader()
    for row in rdr:
        mods = {}
        for key in row:
            cvt = type_convert(row[key])
            if cvt != row[key]:
                mods[key] = cvt
        row.update(mods)
        if options.verbose:
            eprint(row, func(row))
        if func(row):
            wtr.writerow(row)

    return 0

def build_compare_func(args, verbose=False, keys=()):
    "Build a comparison function from cmdline args"

    keys = set(keys)
    func = ["def compare_func(row):\n",
            "    import re\n",
            "    return ( "]

    for (i, arg) in enumerate(args):
        args[i] = type_convert(arg)

    while args:
        # Expect the start of a constraint, a paren or the words "and"
        # or "or".
        if args[0] in ("(", ")", "and", "or"):
            func.append(f" {args[0]} ")
            if verbose:
                eprint(repr(func[-1]))
            del args[0]
            continue

        if args[1] == "match":
            # args[0] must match args[2], e.g.:
            #    re.match(args[2], row[args[0]], re.I) is not None
            func.append(f"(re.match(str({args[2]!r}), str(row[{args[0]!r}]), re.I) is not None)")
            if verbose:
                eprint(repr(func[-1]))
            del args[0:3]
            continue

        # Now we know we must find a constraint.  It must consume the
        # next three tokens.
        if args[0] in keys:
            args[0] = f"row[{args[0]!r}]"
        if args[2] in keys:
            args[2] = f"row[{args[2]!r}]"

        func.append(f"({args[0]} {args[1]} {args[2]})")
        if verbose:
            eprint(repr(func[-1]))
        del args[0:3]

    func.append(" )\n")
    func = "".join(func)
    if verbose:
        eprint(func)
    # We've now built a function.  Compile the code and proceed.

    glbls = {}
    # pylint: disable=exec-used
    exec(func, glbls)

    return glbls["compare_func"]


def eprint(*args, file=sys.stderr, **kwds):
    print(*args, file=file, **kwds)

if __name__ == "__main__":
    sys.exit(main())
