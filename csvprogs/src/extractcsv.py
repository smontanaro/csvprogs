#!/usr/bin/env python

"""
===============
%(PROG)s
===============

--------------------------------------------------------
Extract rows from CSV files matching stated constraints.
--------------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-07-19
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

 %(PROG)s [ options ] [ infile [ outfile ] ]

OPTIONS
=======

none yet

if given, infile specifies the input CSV file (default: stdin)
if given, outfile specifies the output CSV file (default: stdout)

DESCRIPTION
===========

Filter an input CSV file, emitting rows to the output which match the
constraints given on the command line.  Individual constraints are
specified as

    column RELOP expr

where RELOP is one of the Python relational operators.  Constraints
can be joined together using "and" or "or".  Parentheses can be used
to direct order of evaluation.

EXAMPLE
=======

Write rows from the input if the "contract" column equals "F:LGOV13"
and price > 96125 or price < 96000::

  %(PROG)s contract == F:LGOV13 and '(' price '>' 96125 or price '<' 96000 ')'

Write rows from a trading audit archive file corresponding to fills
for the user "putin"::

  %(PROG)s "User Name" == putin and \\
    'Source or Destination' == "From Exchange" and \\
    Transaction == "EXECUTION"

Note that characters which are special to the shell ("(", ")", "<",
and ">" in this case) must be quoted to protect them.  Values which
contain spaces must also be quoted.

DETAILS
=======

Under the covers, the script builds a Python function which compares
the constraint expression against a given row.  The above example
would generate a function like this::

    def compare_func(row):
        return (row["contract"] == "F:LGOV13" and
                (row["price"] > "96125" or row["price"] < "96000"))

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

from __future__ import absolute_import
from __future__ import print_function
import sys
import csv
import os
import getopt
from six.moves import zip

PROG = os.path.split(sys.argv[0])[1]

def usage(msg=None):
    if msg is not None:
        print(msg, file=sys.stderr)
        print(file=sys.stderr)
    print((__doc__.strip() % globals()), file=sys.stderr)

def main(args):
    opts, args = getopt.getopt(args, "hf:")
    for opt, arg in opts:
        if opt == "-h":
            usage()
            return 0

    # Build a comparison function from the remaining
    func = ["def compare_func(row):\n",
            "    return ( "]

    while args:
        # Expect the start of a constraint, a paren or the words "and"
        # or "or".
        if args[0] in ("(", ")", "and", "or"):
            func.append(" %s " % args[0])
            del args[0]
            continue

        # Now we know we must find a constraint.  It must consume the
        # next three tokens.
        func.append("row[%r] %s %r" % (args[0], args[1], args[2]))
        del args[0:3]

    func.append(" )\n")
    func = "".join(func)
    # We've now built a function.  Compile the code and proceed.

    glbls = {}
    exec(func, glbls)
    func = glbls["compare_func"]

    rdr = csv.DictReader(sys.stdin)
    wtr = csv.DictWriter(sys.stdout, fieldnames=rdr.fieldnames)
    wtr.writerow(dict(list(zip(rdr.fieldnames, rdr.fieldnames))))
    for row in rdr:
        if func(row):
            wtr.writerow(row)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
