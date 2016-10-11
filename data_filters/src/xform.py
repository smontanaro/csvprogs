#!/usr/bin/env python

"""
======================
%(PROG)s
======================

---------------------------------------------------------
Transform input values based upon user-defined function
---------------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-12-12
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

 %(PROG)s [ -v ] [ -f func | F mod.func ] [ -s sep ] [ -k name ] \\
          [ -H [ -c names ] ]

OPTIONS
=======

-s sep        use sep as the field separator (default is comma)

-f stmts      Python function which transforms the input row (split into
              fields). Incompatible with -F. If the statements define
              more than a single object, you must define a symbol
              named "__xform__" which holds the name of the function
              to execute.  See also "-c".

-F mod.func   Use function func from module mod instead. Incompatible
              with -f. Packages are currently not supported.  See also
              "-c".

-H            Treat the first line as a header

-c names      If -H is given, the comma-separated list of names is
              guaranteed to be included in the output headers, even if
              some are missing from the first output row.  If not
              given, only those keys present in the first non-empty
              row are guaranteed to be included in the header line.

              The list of output columns can also be extended by
              defining a symbol, "__xform_names__" (a list of strings)
              within the module (-F) or list of statements (-f). Any
              extra column names defined by the combination of -c or
              definition of __xform_names__ appear in sorted order in
              the output.

-p key=value,...  Define one or more global variables for the filters
              to reference. Separate each key/value pair by a
              comma. Each value will be interpreted as an int or
              float, if possible. Values can't currently be anything
              other than ints, floats or strings.

-v            Be more chatty.

DESCRIPTION
===========

Data are read from stdin.  Each row is passed to the user-provided
function.  The (possibly modified) row is written to stdout if it is
non-empty.  Fields which look like numbers will be converted
automatically.  Timestamps are kept as strings.

In the normal case, the transformation function won't return a
value. It is allowed to return a two-element tuple, however. If
returned, the elements of that tuple each specify a list of
dictionaries to write to the output before or after the
transformed row.

The input row will not be written to the output if it is empty (empty
list or dict). If you want to write out a blank row, just modify it so
it is a list with a single empty string (e.g., [""]) or a dict with at
least one valid output key whose value is the empty string (e.g.,
{'x': ''}).

If you want to add more keys to a dict row, use the -c names command
line argument. Simply adding keys to the dict will not work.

EXAMPLE
=========

This transform function demonstrates how you can inject new rows into
the output before or after the input row.

    def xform(row):
        pre = [{"x": row["x"] - 0.1, "y": row["y"]}]
        post = [{"x": row["x"] + 0.1, "y": row["y"]}]
        # leave row unchanged...
        return (pre, post)

If example.csv contains these rows and the -H flag was given on the
command line::

    time,GBM,ZF
    11/22/2013 14:00,125.680811,120.80775
    11/22/2013 15:00,125.677778,120.812342
    11/22/2013 16:00,125.655,120.841542
    11/22/2013 17:00,125.655,120.835938

the first row will be treated as a header and the first logical row
passed to the user's function will appear to be a dictionary which
looks like this::

    {
        "time": "11/22/2013 14:00",
        "GBM": 125.680811,
        "ZF": 120.80775,
        0: "11/22/2013 14:00",
        1: 125.680811,
        2: 120.80775,
    }

Code in the function can thus access elements using list or dictionary
notation.  (Note that negative offsets such as x[-1] won't work,
however.) Within the function, the fields can be added, modified, or
removed altogether.

If this function is applied to the above file::

    def func(row):
        row["GBM.ZF"] = row["GBM"] - row["ZF"]

on output, the file would have a new column::

    time,GBM,ZF,GBM.ZF
    11/22/2013 14:00,125.680811,120.80775,4.873061
    11/22/2013 15:00,125.677778,120.812342,4.865436
    11/22/2013 16:00,125.655,120.841542,4.813458
    11/22/2013 17:00,125.655,120.835938,4.819062

Integer key/value pairs are not considered before deciding whether or
not to write the dictionary out.

This tool is obviously going to be slower than grep or sed, but offers
the user a lot more flexibility and if the user has Python experience
is probably easier to use than awk.

SEE ALSO
========

* filter
* mpl
* take
"""

from __future__ import absolute_import
from __future__ import print_function
import sys
import getopt
import os
import csv
import UserDict
import inspect
from six.moves import range
from six.moves import zip

PROG = os.path.basename(sys.argv[0])

def main(args):
    options = process_args(args)

    if options.xform is None:
        usage("-f or -F are required.")
        return 1

    if options.has_header:
        rdr = csv.DictReader(sys.stdin, delimiter=options.sep)
        # Treat first row as a header.
        out_fields = rdr.fieldnames[:]
        for name in options.extra_names:
            if name not in rdr.fieldnames:
                out_fields.append(name)
        indexes = enumerate(rdr.fieldnames)
        wtr = csv.DictWriter(sys.stdout, fieldnames=out_fields)
    else:
        indexes = None
        rdr = csv.reader(sys.stdin, delimiter=options.sep)
        wtr = csv.writer(sys.stdout, delimiter=options.sep)

    inject_globals(options.xform, options.vars)

    xform(rdr, wtr, options.xform, indexes)
    return 0

def xform(rdr, wtr, func, indexes):
    do_header = write_header = isinstance(wtr, csv.DictWriter)
    for row in rdr:
        type_convert(row)
        if indexes is not None:
            row = ListyDict(row, indexes)
        try:
            result = func(row)
        except Exception as e:
            print("Error processing:", row, file=sys.stderr)
            raise
        if do_header:
            pre, post = result if result is not None else [{}, {}]
        else:
            pre, post = result if result is not None else [[], []]
        # Defer writing header as long as possible.
        if write_header:
            fieldnames = set(wtr.fieldnames) | set(pre) | set(post) | set(row)
            wtr.fieldnames = sorted(fieldnames)
            wtr.writeheader()
            write_header = False
        for rows in (pre, [row] if row else [], post):
            if rows:
                wtr.writerows(rows)

def inject_globals(func, vrbls):
    # Inject user-defined variables into the function's globals.  We
    # can have callables which aren't methods or functions, such as
    # class instances, so allow to loop twice. On the first pass we
    # discover that we don't have a normal callable and set func to
    # the __call__ attribute of that object. On the second pass, it
    # better be one of the other things we know how to handle
    # directly.
    #
    # I suppose you could have something like this:
    #
    # class C(object):
    #    def __call__(self):
    #        print "called"
    #
    # class Other(object):
    #    c = C()
    #    __call__ = c
    #
    # o = Other()
    #
    # (or something like that). In this case, if o was the callable,
    # you'd discover that o has a __call__ method, then need to go
    # through the entire exercise again, because c.__call__ is itself
    # not a normal function-like beast.
    for _i in (0, 1):
        if inspect.ismethod(func):
            func_globals = func.__func__.__globals__
        elif inspect.isfunction(func):
            func_globals = func.__globals__
        elif inspect.isbuiltin(func):
            func_globals = sys.modules[func.__module__].__dict__
        elif inspect.ismethoddescriptor(func):
            raise TypeError("Can't get globals of a method descriptor")
        elif hasattr(func, "__call__"):
            func = func.__call__
            # Try again...
            continue
        else:
            raise TypeError("Don't know how to find globals from %s objects" %
                            type(func))
        break
    else:
        raise TypeError("Don't know how to find globals from %s objects" %
                        type(func))
    func_globals.update(vrbls)

def process_args(args):
    opts, args = getopt.getopt(args, "f:F:s:hHc:p:v")

    options = Options()
    for opt, arg in opts:
        if opt == "-s":
            options.sep = arg
        elif opt == "-f":
            d = {}
            exec(arg, {}, d)
            if "__xform__" in d:
                options.xform = d[d["__xform__"]]
            else:
                # Better only define a single object!
                options.xform = d[list(d.keys())[0]]
            if "__xform_names__" in d:
                options.extra_names.extend(d["__xform_names__"])
        elif opt == "-F":
            modname, funcname = arg.split(".")
            mod = __import__(modname)
            options.xform = getattr(mod, funcname)
            if hasattr(mod, "__xform_names__"):
                options.extra_names.extend(getattr(mod, "__xform_names__"))
        elif opt == "-H":
            options.has_header = True
        elif opt == "-v":
            options.verbose = True
        elif opt == "-c":
            options.extra_names.extend(arg.split(","))
        elif opt == "-p":
            keys = [x.split("=")[0].strip() for x in arg.split(",")]
            vals = [x.split("=")[1].strip() for x in arg.split(",")]
            type_convert(vals)
            options.vars = dict(list(zip(keys, vals)))
        elif opt == "-h":
            usage()
            raise SystemExit

    options.extra_names = sorted(set(options.extra_names))
    return options

class Options(object):
    def __init__(self):
        self.xform = lambda _: None
        self.sep = ","
        self.has_header = False
        self.extra_names = []
        self.vars = {}
        self.verbose = False

class ListyDict(UserDict.DictMixin):
    """Dictish objects which also support some list-style numeric indexing."""
    def __init__(self, d, indexes):
        self.data = d
        self.indexes = dict(indexes)

    def keys(self):
        return list(self.data.keys())

    def __contains__(self, k):
        return k in self.data

    def __iter__(self):
        return iter(self.data)
    iterkeys = __iter__

    def __getitem__(self, k):
        k = self.indexes.get(k, k)
        return self.data[k]

    def __delitem__(self, k):
        k = self.indexes.get(k, k)
        del self.data[k]

    def __setitem__(self, k, v):
        k = self.indexes.get(k, k)
        self.data[k] = v

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, self.data)

    def __getattr__(self, k):
        return getattr(self.data, k)

def add_numeric_keys(row, indexes):
    # Add numeric keys to dicts so functions can index using ints.
    for index, key in indexes:
        row[index] = row[key]

def del_numeric_keys(row, indexes):
    # Undo work of add_numeric_keys
    for index, _key in indexes:
        if index in row:
            del row[index]

def type_convert(row):
    if isinstance(row, dict):
        for k in row:
            row[k] = make_number(row[k])
    else:
        for i in range(len(row)):
            row[i] = make_number(row[i])

def make_number(val):
    try:
        val = int(val)
    except ValueError:
        try:
            val = float(val)
        except ValueError:
            pass
    return val

def usage(msg=""):
    if msg:
        print(msg, file=sys.stderr)
    print(__doc__ % globals(), file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
