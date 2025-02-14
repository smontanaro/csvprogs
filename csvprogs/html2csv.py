#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------------
Convert an HTML table (stdin) to CSV form (stdout).
----------------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2020-05-11
:Copyright:
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

 %(PROG)s [ -s n ] [ infile [ outfile ] ]

OPTIONS
=======

-s n    read and convert table n (default first table encountered - table 1)

DESCRIPTION
===========

Find the n-th table in the input file (or stdin) and write the cell data to
output file (or stdout).

SEE ALSO
========

* csv2csv
* xls2csv

"""

import csv
import datetime
from html.parser import HTMLParser
import os
import sys

from csvprogs.common import CSVArgParser, usage, openio


PROG = os.path.splitext(os.path.basename(sys.argv[0]))[0]
EPOCH = datetime.datetime.fromtimestamp(0)

def main():
    parser = CSVArgParser(usage=usage(__doc__, globals()))
    parser.add_argument("-t", "--table", dest="table", default=1,
                        type=int)
    (options, args) = parser.parse_known_args()

    with openio(args[0] if len(args) >= 1 else sys.stdin, "r",
                args[1] if len(args) == 2 else sys.stdout, "a",
                encoding=options.encoding) as (inf, outf):
        tbl_parser = TableParser(options.table, options.verbose)
        for line in inf:
            tbl_parser.feed(line)
        tbl_parser.close()
        wrtr = csv.writer(outf)
        for row in tbl_parser.rows:
            wrtr.writerow(row)
    return 0

class TableParser(HTMLParser):
    "Extract row/cell info from the given table number."
    def __init__(self, table_num, verbose):
        self.table_num = table_num
        self.verbose = verbose
        self.rows = []
        self.handlers = {
            "table": self.handle_table,
            "tr": self.handle_tr,
            "th": self.handle_cell,
            "td": self.handle_cell,
            }
        self._processing_table = False
        self._processing_cell = False
        self._indent = 0
        super().__init__()

    @property
    def processing_table(self):
        return self._processing_table
    @processing_table.setter
    def processing_table(self, value):
        self._processing_table = value

    @property
    def processing_cell(self):
        return self._processing_cell
    @processing_cell.setter
    def processing_cell(self, value):
        self._processing_cell = value

    def handle_starttag(self, tag, attrs):
        handler = self.handlers.get(tag)
        if handler is None:
            self.error("start", tag, attrs)
            return
        handler("start", tag, attrs)
        self._indent += 2

    def handle_endtag(self, tag):
        handler = self.handlers.get(tag)
        if handler is None:
            self.error("end", tag)
            return
        self._indent -= 2
        handler("end", tag, [])

    def handle_data(self, data):
        if self.processing_table and self.processing_cell:
            if data not in ("\r\n", "\n", "\r"):
                self.rows[-1].append(data)

    def handle_table(self, what, _tag, _attrs):
        if what == "start":
            self.table_num -= 1
            if not self.table_num:
                self.processing_table = True
                self.error("start table")
            return
        if not self.table_num:
            self.processing_table = False

    def handle_tr(self, what, _tag, _attrs):
        if self.processing_table:
            if what == "start":
                self.rows.append([])
        self.error(f"{what} tr")

    def handle_cell(self, what, tag, _attrs):
        if self.processing_table:
            self.processing_cell = what == "start"
            self.error(f"{what} {tag}", end=" " if what == "start" else "\n")

    def error(self, *args, file=sys.stderr, **kwds):
        if self.verbose:
            print(" " * self._indent, *args, file=file, **kwds)


if __name__ == "__main__":
    sys.exit(main())
