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

PROG = os.path.splitext(os.path.basename(sys.argv[0]))[0]
EPOCH = datetime.datetime.fromtimestamp(0)

def main(args):
    sheet = 0
    try:
        opts, args = getopt.getopt(args, "hs:")
    except getopt.GetoptError:
        usage()
        return 1

    for opt, arg in opts:
        if opt == "-h":
            usage()
            return 0
        if opt == "-s":
            sheet = int(arg)

    if args:
        usage()
        return 1

    wrtr = csv.writer(sys.stdout)
    tmpf = tempfile.mktemp()
    f = open(tmpf, "wb")
    f.write(sys.stdin.read())
    f.close()

    try:
        book = xlrd.open_workbook(tmpf)
        worksheet = book.sheet_by_index(sheet)

        for i in range(worksheet.nrows):
            wrtr.writerow([cell_value(x, book.datemode)
                               for x in worksheet.row(i)])
    finally:
        os.unlink(tmpf)

    return 0

def usage(msg=""):
    if msg:
        print >> sys.stderr, msg.rstrip()
    print >> sys.stderr, __doc__ % globals()

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
    sys.exit(main(sys.argv[1:]))
