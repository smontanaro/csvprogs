#!/usr/bin/env python3

"""
Common arg processing for this group of CSV programs
"""

__all__ = ["CSVArgParser",]

import argparse

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
