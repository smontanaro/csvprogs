#!/usr/bin/env python3

"""
Common arg processing for this group of CSV programs
"""

__all__ = ["CSVArgParser",]

import argparse
from contextlib import contextmanager
from functools import partial
import os

class CSVArgParser(argparse.ArgumentParser):
    "ArgumentParser with some behavior common to all CSV progs/data filters"

    def __init__(self, *args, **kwargs):
        argparse.ArgumentParser.__init__(self, *args, **kwargs)
        self.add_common_args()

    def add_common_args(self):
        "Add arguments to the parser which are common to all tools"
        self.add_argument("-i", "--insep", dest="insep", default=",",
                          help="input field delimiter")
        self.add_argument("-o", "--outsep", dest="outsep", default=",",
                          help="output field delimiter")
        self.add_argument("-f", "--fields", dest="fields", default=None,
                          help="fields to copy from input to output")
        self.add_argument("-v", "--verbose", dest="verbose", default=False,
                          action="store_true", help="be more chatty")
        self.add_argument("-e", "--encoding", dest="encoding", default="utf-8",
                          help="encoding of both input and output files")

@contextmanager
def openio(infile, imode, outfile, omode, encoding="utf-8"):
    "open infile and outfile, guaranteeing automatic closure."
    if hasattr(infile, "fileno"):
        # need to reopen this file object
        iopen = partial(os.fdopen, infile.fileno(), imode, encoding=encoding)
    else:
        iopen = partial(open, infile, imode, encoding=encoding)
    if hasattr(outfile, "fileno"):
        # need to reopen this file object
        oopen = partial(os.fdopen, outfile.fileno(), omode, encoding=encoding)
    else:
        oopen = partial(open, outfile, omode, encoding=encoding)
    with (iopen() as inf, oopen() as outf):
        yield (inf, outf)
