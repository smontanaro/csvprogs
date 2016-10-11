#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------------
Assemble one or more CSV files into an Excel spreadsheet
----------------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2015-09-14
:Copyright: TradeLink LLC 2015
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

 %(PROG)s file ...

At least one CSV file must be named.

DESCRIPTION
===========

As each CSV file is encountered on the command line, it is appended to
a workbook as a separate sheet.  After all CSV files have been
processed, the generated Excel workbook is written to stdout.

An attempt is made to coerce each cell encountered to one of the
following types, in order: int, float, datetime. If all coercion
attempts fail, the cell is saved as a string.

SEE ALSO
========

* xls2csv
* csv2csv
"""

from __future__ import absolute_import
from __future__ import print_function
import csv
import getopt
import os
import sys

import dateutil.parser
import xlwt

PROG = os.path.splitext(os.path.basename(sys.argv[0]))[0]

def main(args):
    opts, args = getopt.getopt(args, "h")
    for opt, _arg in opts:
        if opt == "-h":
            usage()
            return 0

    csvfiles = args
    if not csvfiles:
        usage("At least one CSV file is required.")
        return 1

    book = xlwt.Workbook(encoding="utf-8")
    for csvf in csvfiles:
        append_sheet_from_csv(book, csvf)
    book.save(sys.stdout)

    return 0

def append_sheet_from_csv(book, csvf):
    sheet = book.add_sheet(csvf.replace("/", "_"))
    populate_sheet_from_csv(sheet, csvf)

def populate_sheet_from_csv(sheet, csvf):
    rdr = csv.reader(open(csvf, "rb"))
    r = 0
    for row in rdr:
        c = 0
        for cell in row:
            sheet.write(r, c, label=type_convert(cell))
            c += 1
        r += 1

def type_convert(cell):
    """Try to coerce a cell's value into various Python types.

    The order of attack is: int, float, datetime. If all attempts
    to convert the cell value fail, it is returned unchanged.
    """

    for cvt in (int, float, dateutil.parser.parse):
        try:
            return cvt(cell)
        except ValueError:
            pass
    return cell

def usage(msg=""):
    if msg:
        print(msg.rstrip(), file=sys.stderr)
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
