#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------------
Convert an Excel spreadsheet (stdin) to CSV form (stdout).
----------------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

 %(PROG)s [ -s n ]

OPTIONS
=======

-s n    read and convert sheet n (default 0)

DESCRIPTION
===========

SEE ALSO
========

* csv2csv
"""

import sys
import tempfile
import getopt
import csv
import os
import datetime

import xlrd

from csvprogs.common import usage


PROG = os.path.splitext(os.path.basename(sys.argv[0]))[0]
EPOCH = datetime.datetime.fromtimestamp(0)


def main():
    sheet = 0
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:")
    except getopt.GetoptError as err:
        print(usage(__doc__, globals()), err, file=sys.stderr)
        return 1

    for opt, arg in opts:
        if opt == "-h":
            print(usage(__doc__, globals()), file=sys.stderr)
            return 0
        if opt == "-s":
            sheet = int(arg)

    if args:
        print(usage(__doc__, globals()), f"unexpected cmdline arg: {sys.argv[1:]}",
              file=sys.stderr)
        return 2

    wrtr = csv.writer(sys.stdout)

    try:
        (fd, xlsf) = tempfile.mkstemp()
        with (open(xlsf, "wb") as xls,
              os.fdopen(sys.stdin.fileno(), "rb") as xlsin):
            os.close(fd)
            xls.write(xlsin.read())

        rows = xls2csv(xlsf, sheet)
        wrtr.writerows(rows)
    finally:
        os.unlink(xlsf)

    return 0


def xls2csv(xlsf, sheet):
    book = xlrd.open_workbook(xlsf)
    worksheet = book.sheet_by_index(sheet)

    rows = []
    for i in range(worksheet.nrows):
        rows.append([cell_value(x, book.datemode)
                     for x in worksheet.row(i)])
    return rows


def cell_value(cell, datemode):
    if cell.ctype == xlrd.XL_CELL_DATE:
        if cell.value != 0.0:
            t = xlrd.xldate_as_tuple(cell.value, datemode)
            if t[0] > 0:
                val = datetime.datetime(*t)
            else:
                val = datetime.time(*t[3:])
        else:
            val = EPOCH
    else:
        val = cell.value
        if isinstance(val, str):
            if "," in val:
                # we got ourselves a list
                val = val.split(",")
        elif isinstance(val, float):
            if int(val) == val:
                # int masquerading as a float?
                val = int(val)
    return val

if __name__ == "__main__":
    sys.exit(main())
