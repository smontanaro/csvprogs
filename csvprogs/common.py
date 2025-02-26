#!/usr/bin/env python3

"""
Common arg processing for this group of CSV programs
"""

import argparse
from contextlib import contextmanager
from functools import partial
import io
from locale import getlocale, atoi, atof
import os
import sys

import dateutil.parser
from public import public

LOCALE = ".".join(getlocale())

SECONDS_PER_DAY = 60 * 60 * 24


@public
class CSVArgParser(argparse.ArgumentParser):
    "ArgumentParser with some behavior common to all CSV progs/data filters"

    def __init__(self, *args, **kwargs):
        argparse.ArgumentParser.__init__(self, *args, **kwargs)
        self.add_common_args()

    def add_common_args(self):
        "Add arguments to the parser which are common to all tools"
        self.add_argument("-l", "--locale", dest="locale", default=LOCALE,
                          help="input field delimiter")
        self.add_argument("-i", "--insep", dest="insep", default=",",
                          help="input field delimiter")
        self.add_argument("-o", "--outsep", dest="outsep", default=",",
                          help="output field delimiter")
        self.add_argument("-v", "--verbose", dest="verbose", default=False,
                          action="store_true", help="be more chatty")
        self.add_argument("-e", "--encoding", dest="encoding", default="utf-8",
                          help="encoding of both input and output files")
        self.add_argument("-a", "--append", default=False, action='store_true',
                          help="append rows to output (no header is written)")

@public
@contextmanager
def openi(infile, imode, encoding="utf-8"):
    "open infile, guaranteeing automatic closure."
    if hasattr(infile, "fileno"):
        # need to reopen this file object
        iopen = partial(os.fdopen, infile.fileno(), imode, encoding=encoding)
    else:
        iopen = partial(open, infile, imode, encoding=encoding)
    with iopen() as inf:
        yield inf

@public
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

@public
@contextmanager
def openpair(options, args):
    mode = "a" if options.append else "w"
    with openio(args[0] if len(args) >= 1 else sys.stdin, "r",
                args[1] if len(args) == 2 else sys.stdout, mode,
                encoding=options.encoding) as (inf, outf):
        yield (inf, outf)

@public
def usage(docstring, global_dict, msg=None):
    "common extraction of __doc__"
    output = io.StringIO()
    if msg:
        print(msg, file=output)

    # see csvplot.py:main where I thwart this step

    if global_dict:
        print(docstring % global_dict, file=output)
    else:
        print(docstring, file=output)

    # eventually this instead? argparse.ArgumentParser uses % string
    # formatting, which makes it difficult to double up. Using {}-style
    # formatting here might work better, but all callers to this function have
    # to be modified.

    # print(docstring.format(**global_dict), file=output)

    return output.getvalue()

@public
def type_convert(string, keep_tz=True):
    """Try to coerce a string value into various Python types.

    The order of attack is: int, float, datetime. If all attempts
    to convert the cell value fail, it is returned unchanged.

    If keep_tz is True and the result is a datetime object, the tzinfo
    field will be cleared.
    """

    for cvt in (atoi, atof, dateutil.parser.parse):
        try:
            result = cvt(string)
        except ValueError:
            pass
        else:
            if hasattr(result, "tzinfo") and not keep_tz:
                result = result.replace(tzinfo=None)
            return result
    # nothing matched, punt...
    return string

@public
def as_days(delta):
    "timedelta as float # of days"
    return (delta.days +
            delta.seconds / SECONDS_PER_DAY +
            delta.microseconds / (1e6 * SECONDS_PER_DAY))

@public
def weighted_ma(elts, coeffs):
    "moving average of elts, weighted by coeffs"
    num = sum(c * e for (c, e) in zip(coeffs, elts))
    den = sum(coeffs[:len(elts)])
    return num / den

@public
class ListyDict:
    """Dictish objects which also support some list-style numeric indexing."""
    def __init__(self, d, indexes):
        self.data = d
        self.indexes = dict(indexes)

    def keys(self):
        "delegate to self.data"
        return list(self.data.keys())

    def __contains__(self, k):
        "delegate to self.data"
        return k in self.data

    def __iter__(self):
        "delegate to self.data"
        return iter(self.data)

    def __getitem__(self, k):
        "k can be list index or dict key"
        k = self.indexes.get(k, k)
        return self.data[k]

    def __delitem__(self, k):
        "k can be list index or dict key"
        k = self.indexes.get(k, k)
        del self.data[k]

    def __setitem__(self, k, v):
        "k can be list index or dict key"
        k = self.indexes.get(k, k)
        self.data[k] = v

    def __len__(self):
        "delegate to self.data"
        return len(self.data)

    def __str__(self):
        return f"<{self.__class__.__name__} {self.data}>"

    def __getattr__(self, k):
        "delegate to self.data"
        return getattr(self.data, k)
