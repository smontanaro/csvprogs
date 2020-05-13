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

import csv
import datetime
import getopt
from html.parser import HTMLParser
import os
import sys

PROG = os.path.splitext(os.path.basename(sys.argv[0]))[0]
EPOCH = datetime.datetime.fromtimestamp(0)

def main(args):
    table = 1
    verbose = False
    try:
        opts, args = getopt.getopt(args, "ht:v")
    except getopt.GetoptError:
        usage()
        return 1

    for opt, arg in opts:
        if opt == "-h":
            usage()
            return 0
        if opt == "-t":
            table = int(arg)
        elif opt == "-v":
            verbose = True

    if args:
        usage()
        return 1

    parser = TableParser(table, verbose)
    for line in sys.stdin:
        parser.feed(line)
    wrtr = csv.writer(sys.stdout)
    wrtr.writerows(parser.rows)
    return 0

class TableParser(HTMLParser):
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

    def handle_table(self, what, tag, attrs):
        if what == "start":
            self.table_num -= 1
            if not self.table_num:
                self.processing_table = True
            return
        if not self.table_num:
            self.processing_table = False

    def handle_tr(self, what, tag, attrs):
        if self.processing_table:
            if what == "start":
                self.rows.append([])

    def error(self, message):
        print(message, file=sys.stderr)

def usage(msg=""):
    if msg:
        print(msg.rstrip(), file=sys.stderr)
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
