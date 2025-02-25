#!/usr/bin/env python

"""======================
%(PROG)s
======================

---------------------------------------------------------
Transform input values based upon user-defined function
---------------------------------------------------------

:Author: skip.montanaro@gmail.com
:Date: 2013-12-12
:Copyright: TradeLink LLC 2013
:Copyright: Skip Montanaro 2016-2021
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

 %(PROG)s [ -v ] [ -f func | F mod.func ] [ -s sep ] [ -k name ] \\
          [ -c names ]

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

-c names      If given, the comma-separated list of names is guaranteed
              to be included in the output headers, even if some are
              missing from the first output row.  If not given, only
              those keys present in the first non-empty row are
              guaranteed to be included in the header line.

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

If example.csv contains these rows::

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

import csv
import inspect
import os
import sys

from csvprogs.common import CSVArgParser, usage, ListyDict

PROG = os.path.basename(sys.argv[0])

def main():
    "see __doc__"
    options = process_args()
    if options is None:
        return 1

    rdr = csv.DictReader(sys.stdin, delimiter=options.insep)
    out_fields = rdr.fieldnames[:]
    for name in options.extra_names:
        if name not in rdr.fieldnames:
            out_fields.append(name)
    indexes = enumerate(rdr.fieldnames)
    wtr = csv.DictWriter(sys.stdout, fieldnames=out_fields,
        delimiter=options.outsep)
    if not options.append:
        wtr.writeheader()

    inject_globals(options.xform, options.vars)

    xform(rdr, wtr, options.xform, indexes)
    return 0

def xform(rdr, wtr, func, indexes):
    "see __doc__"
    for row in rdr:
        type_convert(row)
        row = ListyDict(row, indexes)
        result = func(row)
        pre, post = result if result is not None else [{}, {}]
        wtr.writerows(pre)
        wtr.writerow(row.data)
        wtr.writerows(post)

def inject_globals(func, vrbls):
    "Inject user-defined variables into the function's globals."

    # We can have callables which aren't methods or functions, such as
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
    #        print("called")
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
        elif hasattr(func, "__class__"):
            func_globals = sys.modules[func.__class__.__module__].__dict__
        elif hasattr(func, "__call__"):
            func = func.__call__
            # Try again...
            continue
        else:
            raise TypeError("Don't know how to find globals "
                            f"from {type(func)} objects")
        break
    else:
        raise TypeError("Don't know how to find globals "
                        f"from {type(func)} objects")
    func_globals.update(vrbls)

def process_args():
    parser = CSVArgParser()
    parser.add_argument("-f", "--function", dest="function", default="",
                        help="user-defined function to execute")
    parser.add_argument("-F", "--external-function", dest="ext_func", default="",
                        help="user-defined external function to execute")
    parser.add_argument("-c", "--extra-args", dest="extra_names", default="",
                        help="arguments guaranteed to be in the output")
    parser.add_argument("-p", "--variable-pair", dest="vars", default="",
                        help="global variable name/value pairs")
    (options, _args) = parser.parse_known_args()
    if options.function and options.ext_func:
        print(usage(__doc__, globals(), "only one of -f or -F may be given"))
        return None

    options.extra_names = options.extra_names.split(",")

    if options.function:
        d = {}
        # pylint: disable=W0122
        exec(options.function, {}, d)
        if "__xform__" in d:
            options.xform = d[d["__xform__"]]
        else:
            # Better only define a single object!
            options.xform = d[list(d.keys())[0]]
        if "__xform_names__" in d:
            options.extra_names.extend(d["__xform_names__"])
    elif options.ext_func:
        modname, funcname = options.ext_func.split(".")
        mod = __import__(modname)
        options.xform = getattr(mod, funcname)
        if hasattr(mod, "__xform_names__"):
            options.extra_names.extend(getattr(mod, "__xform_names__"))
    else:
        print(usage(__doc__, globals(), "no transform function given"))
        return None

    if options.vars:
        keys = [x.split("=")[0].strip() for x in options.vars.split(",")]
        vals = [x.split("=")[1].strip() for x in options.vars.split(",")]
        type_convert(vals)
        options.vars = dict(list(zip(keys, vals)))

    options.extra_names = sorted(set(options.extra_names))
    return options


def type_convert(row):
    "guess data types (can you say Perl???)"
    if isinstance(row, dict):
        for k in row:
            row[k] = make_number(row[k])
    else:
        for (i, val) in enumerate(row):
            row[i] = make_number(val)

def make_number(val):
    "Convert val to the most specific kind of number we can."
    try:
        val = int(val)
    except ValueError:
        try:
            val = float(val)
        except ValueError:
            pass
    return val


if __name__ == "__main__":
    sys.exit(main())
