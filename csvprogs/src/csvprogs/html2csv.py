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

 %(PROG)s [ -s n ]

OPTIONS
=======

-s n    read and convert table n (default first table encountered - table 1)

DESCRIPTION
===========

SEE ALSO
========

* csv2csv
* xls2csv

"""

import argparse
import csv
import datetime
from html.parser import HTMLParser
import os
import sys

PROG = os.path.splitext(os.path.basename(sys.argv[0]))[0]
EPOCH = datetime.datetime.fromtimestamp(0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--table", dest="table", default=1,
                        type=int)
    parser.add_argument("-v", "--verbose", dest="verbose", default=False,
                        action="store_true")
    (options, args) = parser.parse_known_args()

    with (open(args[0], "r", encoding="utf-8") if len(args) >= 1 else sys.stdin as inf,
          open(args[1], "w", encoding="utf-8") if len(args) == 2 else sys.stdout as outf):
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
            }
        self.processing_table = False
        super().__init__()

    def handle_starttag(self, tag, attrs):
        handler = self.handlers.get(tag)
        if handler is None:
            if self.verbose:
                print("Start", tag)
            return
        handler("start", tag, attrs)

    def handle_endtag(self, tag):
        handler = self.handlers.get(tag)
        if handler is None:
            if self.verbose:
                print("End", tag)
            return
        handler("end", tag, [])

    def handle_data(self, data):
        if self.processing_table:
            if self.verbose:
                print("Found some data:", repr(data))
            if data not in ("\r\n", "\n", "\r"):
                self.rows[-1].append(data)

    def handle_table(self, what, _tag, _attrs):
        if what == "start":
            self.table_num -= 1
            if not self.table_num:
                self.processing_table = True
            return
        if not self.table_num:
            self.processing_table = False

    def handle_tr(self, what, _tag, _attrs):
        if self.processing_table:
            if what == "start":
                self.rows.append([])

    def error(self, message):
        print(message, file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
