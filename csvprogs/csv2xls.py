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

import csv
from locale import setlocale, LC_ALL, atof, atoi
import os
import sys

import dateutil.parser
import openpyxl

from csvprogs.common import CSVArgParser, usage
PROG = os.path.splitext(os.path.basename(sys.argv[0]))[0]

def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    options, csvfiles = parser.parse_known_args()

    if not csvfiles:
        print(usage(__doc__, globals(), msg="At least one CSV file is required."),
              file=sys.stderr)
        return 1

    setlocale(LC_ALL, options.locale)

    book = openpyxl.Workbook()
    # creating a workbook creates an empty initial worksheet named "Sheet". Get rid of it.
    del book["Sheet"]
    for csvf in csvfiles:
        append_sheet_from_csv(book, csvf, options.encoding)
    book.save("/dev/stdout")

    return 0

def append_sheet_from_csv(book, csvf, encoding):
    sheet = book.create_sheet(title=os.path.basename(csvf).replace("/", "_"))
    populate_sheet_from_csv(sheet, csvf, encoding)

def populate_sheet_from_csv(sheet, csvf, encoding):
    with open(csvf, "r", encoding=encoding) as inf:
        rdr = csv.reader(inf)
        for row in rdr:
            sheet_row = []
            for cell in row:
                sheet_row.append(type_convert(cell))
            sheet.append(sheet_row)

def type_convert(cell):
    """Try to coerce a cell's value into various Python types.

    The order of attack is: int, float, datetime. If all attempts
    to convert the cell value fail, it is returned unchanged.
    """

    for cvt in (atoi, atof, dateutil.parser.parse):
        try:
            result = cvt(cell)
        except ValueError:
            pass
        else:
            if hasattr(result, "tzinfo"):
                result = result.replace(tzinfo=None)
            return result
    # nothing matched, punt...
    return cell


if __name__ == "__main__":
    sys.exit(main())
