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
import getopt
import os
import sys

PROG = os.path.split(sys.argv[0])[1]

def usage(msg=None):
    if msg is not None:
        print(msg, file=sys.stderr)
        print(file=sys.stderr)
    print((__doc__.strip() % globals()), file=sys.stderr)

def main(args):
    opts, args = getopt.getopt(args, "hv")
    verbose = False
    for opt, _arg in opts:
        if opt == "-h":
            usage()
            return 0
        if opt == "-v":
            verbose = True


    # Build a comparison function from the remaining cmdline args
    func = ["def compare_func(row):\n",
            "    import re\n",
            "    return ( "]

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
            func.append(f"(re.match({args[2]!r}, row[{args[0]!r}], re.I) is not None)")
            if verbose:
                eprint(repr(func[-1]))
            del args[0:3]
            continue

        # Now we know we must find a constraint.  It must consume the
        # next three tokens.
        func.append(f"(row[{args[0]!r}] {args[1]} {args[2]!r})")
        if verbose:
            eprint(repr(func[-1]))
        del args[0:3]

    func.append(" )\n")
    func = "".join(func)
    # We've now built a function.  Compile the code and proceed.

    glbls = {}
    # pylint: disable=exec-used
    exec(func, glbls)
    func = glbls["compare_func"]

    rdr = csv.DictReader(sys.stdin)
    wtr = csv.DictWriter(sys.stdout, fieldnames=rdr.fieldnames)
    wtr.writeheader()
    for row in rdr:
        if verbose:
            eprint(row, func(row))
        if func(row):
            wtr.writerow(row)

    return 0

def eprint(*args, file=sys.stderr, **kwds):
    print(*args, file=file, **kwds)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
