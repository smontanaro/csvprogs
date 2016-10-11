#!/usr/bin/env python

"""
===========
%(PROG)s
===========

----------------------------------------------------
plot csv-ish input from stdin using matplotlib
----------------------------------------------------

:Author: skipm@trdlnk.com
:Date: 2013-03-15
:Copyright: TradeLink LLC 2013
:Version: 0.1
:Manual section: 1
:Manual group: data filters

SYNOPSIS
========

%(PROG)s [ -f x,y[,a[,c[,l[s[,m]]]]]] [ -p file ] [ -F fmt ] [ -s sep ] \\
         [ -T title ] [ -r label ] [ -l label] [ -x label ] \\
         [ -b x,y,val,c ] [ -L ] [ -v ] [ -B bkend ] [ -S ] \\
         [ -X min:max ] [ -Y min:max[,min:max] ] [ --xkcd ]

OPTIONS
=======

* -f x,y[,axis[,color[,legend[,style[,marker]]]]] - plot field x vs.
  field y
* -b x,y,val,c - set background to c where field y value >= val at x
* -p file - if given, will save the plot to the named file and exit.
* -F fmt - plot the X axis using fmt (default varies)
* -s sep - use sep as the field separator (default is comma)
* -d dimension - specify dimensions in (I think) inches, default
  8 wide, 6 high
* -T title - set title of the plot
* -r label - set the label for the right y axis
* -l label - set the label for the left y axis
* -x label - set the label for the x axis
* -L - do not create a legend
* -X min:max - set the min and max values for the X axis
* -Y min:max[,min:max] - set the initial min and max values for the left (and
  optionally, right) Y axis
* -v - be a bit more verbose
* -B bkend - use the named backend
* -S - if a fieldname is not found, also try stripping leading and trailing
  whitespace
* --xkcd - mimic style of the XKCD cartoon.

LONG OPTION NAMES
-----------------

Long option names are supported. Supported long names and their
equivalent short names are:

* backend: B
* format : F
* skip_legend: L
* sloppy_names: S
* title: T
* xkcd: X
* y_range: Y
* background: b
* dimension: d
* field: f
* help: h
* left_label: l
* plot_file: p
* right_label: r
* separator: s
* verbose: v
* x_label: x

DESCRIPTION
===========

The %(PROG)s command takes a CSV-like file as input and generates one
or more plots.  Those plots can be displayed interactively (the
default) or written to an image file (if the -p option is given).

In its simplest form it displays a single plot of the values from a
CSV file in column 1 as a function of time (in column 0).  In this
case, the CSV file is assumed to not have a header.

The specification of the fields to plot and their attributes are given
using the -f option.  At its simplest, a single x,y pair is given,
resulting in a red line plot using the left Y axis.  If the CSV file
has a header, x and y can be column names as well.

The -f option is the most frequently used and most complicated:

* The first two fields (x, y) are always required, and specify the two
  columns to plot.
* The Y axis defaults to "left", but can be given explicitly as 'l'
  or 'r'.
* The color can be anything matplotlib accepts. Typically, a single
  letter suffices ('r' for red, etc), but the color name can also be
  spelled out or given using hex notation.
* A legend label can be specified, and defaults to the y column name.
* Consult the matplotlib documentation for details of acceptable styles
  (default '-') and
* markers (default ''). The one exception to matplotlib convention is
  to use ';' instead of ',' to specify use of the pixel marker.

You can also color the background of the plot based on one or more
values using the -b flag.  For example, if you have a value at offset
2 which toggles between three values, -1, 0, and +1, you could color
the background accordingly::

  -b 0,2,-1,skyblue -b 0,2,0,pink -b 0,2,+1,lightgreen.

If you don't specify a format for the X axis, time is assumed, and a
hopefully reasonable format is chosen based on the current visible X
range:

* X range > 1.5 years ==> "%%Y-%%m-%%d"
* X range > two days ==> "%%m/%%d\\n%%H:%%M"
* X range < ten minutes ==> "%%H:%%M\\n%%S.%%f"
* X range < two hours ==> "%%H:%%M:%%S"
* otherwise ==> "%%H:%%M"

EXAMPLE
=======

Plot one hour of F:NQM12 trades, highlighting all trades of size 10
with a light green background::

  nt -S -s 2012-04-06T07:25 -e 2012-04-06T08:25 F:NQM12 \\
  | mpl -f 0,2,l,r -b 0,3,10,lightgreen

VERSION
=======

@@VERSION@@

SEE ALSO
========

* avg
* bars
* nt
* pt
* square
* take

"""

from __future__ import division

from __future__ import absolute_import
from __future__ import print_function
import sys
import csv
import getopt
import datetime
import os
import re

import numpy
import matplotlib

import dateutil.parser

PROG = os.path.basename(sys.argv[0])

SECONDS_PER_DAY = 60 * 60 * 24
ONE_MINUTE = datetime.timedelta(minutes=10)
ONE_DAY = datetime.timedelta(days=1)
ONE_HOUR = datetime.timedelta(minutes=60)

def main(args):
    fields = []
    xtime = True
    xfmt = None
    sep = ","
    title = ""
    right_label = ""
    left_label = ""
    x_label = ""
    plot_file = ""
    dims = (8, 6)
    bkgds = []
    x_min_max = []
    y_min_max = []
    do_legend = True
    backend = None
    use_xkcd = False
    verbose = False
    sloppy_names = False
    opts, args = getopt.getopt(args, "B:F:LST:X:Y:b:d:f:hl:p:r:s:vx:",
                               ["backend=",
                                "format=",
                                "skip_legend",
                                "sloppy_names"
                                "title=",
                                "xkcd",
                                "x_range=",
                                "y_range=",
                                "background=",
                                "dimension=",
                                "field=",
                                "help",
                                "left_label=",
                                "plot_file=",
                                "right_label=",
                                "separator=",
                                "verbose=",
                                "x_label",
                                ])
    for opt, arg in opts:
        if opt in ("-B", "--backend"):
            backend = arg
        elif opt in ("-f", "--field"):
            arg = arg.split(",")
            if len(arg) == 2:
                # plot using left y axis by default
                arg.append("l")
            if len(arg) == 3:
                # plot using blue by default
                arg.append("b")
            if len(arg) == 4:
                # use the Y column name as the default legend name.
                arg.append(arg[1])
            if len(arg) == 5:
                # plot with '-' line style by default
                arg.append("-")
            if len(arg) == 6:
                # no marker by default
                arg.append("")
            try:
                fields.append([int(x.strip()) for x in arg[0:2]]+
                              [arg[2][0].lower()]+
                              [arg[3].lower()]+
                              arg[4:])
                reader = csv.reader
            except ValueError:
                # Assume first two fields name column headers.
                fields.append(arg[0:2]+
                              [arg[2][0].lower()]+
                              [arg[3].lower()]+
                              arg[4:])
                reader = csv.DictReader

        elif opt in ("-b", "--background"):
            vals = arg.split(",")
            try:
                x = int(vals[0])
                y = int(vals[1])
                reader = csv.reader
            except ValueError:
                x = vals[0].strip()
                y = vals[1].strip()
                reader = csv.DictReader
            if ":" in vals[2]:
                low, hi = [float(x) for x in vals[2].split(":")]
            else:
                low = hi = float(vals[2])
            c = vals[3]
            bkgds.append((x, y, low, hi, c))
        elif opt in ("-S", "--sloppy_names"):
            sloppy_names = True
        elif opt in ("-F", "--format"):
            xtime = "%H" in arg or "%M" in arg or "%m" in arg or "%d" in arg
            xfmt = arg
        elif opt in ("-d", "--dimension"):
            dims = tuple([float(v.strip()) for v in re.split("[x,]", arg)])
        elif opt in ("-L", "--skip_legend"):
            do_legend = False
        elif opt in ("-p", "--plot_file"):
            plot_file = arg
        elif opt in ("-l", "--left_label"):
            left_label = arg
        elif opt in ("-r", "--right_label"):
            right_label = arg
        elif opt in ("-x", "--x_label"):
            x_label = arg
        elif opt == "--xkcd":
            use_xkcd = True
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-Y", "--y_range"):
            if "," in arg:
                left, right = arg.split(",")
                y_min_max = [[float(x) for x in left.split(":")],
                             [float(x) for x in right.split(":")]]
            else:
                y_min_max = [[float(x) for x in arg.split(":")]]
        elif opt in ("-X", "--x_range"):
            x_min_max = [[float(x) for x in arg.split(":")]]
        elif opt in ("-s", "--separator"):
            sep = arg
        elif opt in ("-T", "--title"):
            title = arg
        elif opt in ("-h", "--help"):
            usage()
            raise SystemExit

    if backend is None:
        if not os.environ.get("DISPLAY"):
            # Allow non-interactive use (e.g. running with -p from cron)
            matplotlib.use("Agg")
    else:
        matplotlib.use(backend)

    if verbose:
        print("Using", matplotlib.get_backend(), file=sys.stderr)

    from matplotlib import ticker, dates

    import pylab

    if use_xkcd:
        from matplotlib import pyplot
        try:
            pyplot.xkcd()
        except AttributeError:
            print("XKCD style not available.", file=sys.stderr)
        else:
            if verbose:
                print("Using XKCD style.", file=sys.stderr)

    if not fields:
        # normal output from pt, nt, etc
        fields = [(0, 2, "l", "b", "2", "-", "")]
        reader = csv.reader

    min_y = 1e99
    max_y = -1e99
    if xtime:
        min_x = datetime.datetime(9999, 12, 31, 23, 59, 59)
        max_x = datetime.datetime(1970, 1, 1, 0, 0, 0)
        def parse_x(x):
            try:
                return dateutil.parser.parse(x)
            except ValueError:
                print("Can't parse", repr(x), "as a timestamp.", file=sys.stderr)
                raise
        def fmt_date(f, _=None, xfmt=xfmt):
            dt = dates.num2date(f)
            if xfmt is None:
                # Calculate X format dynamically based on the visible
                # range.
                left, right = [dates.num2date(x) for x in pylab.xlim()]
                x_delta = right - left
                if x_delta > int(1.5 * 365) * ONE_DAY:
                    xfmt = "%Y-%m-%d"
                elif x_delta > 2 * ONE_DAY:
                    xfmt = "%m/%d\n%H:%M"
                elif x_delta < 10 * ONE_MINUTE:
                    xfmt = "%H:%M\n%S.%f"
                elif x_delta < 2 * ONE_HOUR:
                    xfmt = "%H:%M:%S"
                else:
                    xfmt = "%H:%M"
            return dt.strftime(xfmt)
        formatter = ticker.FuncFormatter(fmt_date)
    else:
        min_x = 1e99
        max_x = -1e99
        def parse_x(x):
            return float(x)
        def fmt_float(x, _=None):
            return xfmt % x
        formatter = ticker.FuncFormatter(fmt_float)


    if reader == csv.DictReader:
        fieldnames = next(csv.reader(sys.stdin, delimiter=sep))
        rdr = reader(sys.stdin, fieldnames=fieldnames, delimiter=sep)
    else:
        rdr = reader(sys.stdin, delimiter=sep)

    raw = list(rdr)
    left = []
    right = []
    lt_y_range = [min_y, max_y]
    rt_y_range = [min_y, max_y]
    x_range = [min_x, max_x]
    for (c1, c2, side, color, legend, style, marker) in fields:
        if sloppy_names:
            keys = list(raw[0].keys())
            if c1 not in keys:
                for k in keys:
                    if re.match(r"^\s*%s\s*$" % c1, k):
                        c1 = k
                        break
            if c2 not in keys:
                for k in keys:
                    if re.match(r"^\s*%s\s*$" % c2, k):
                        c2 = k
                        break
        if marker == ";":
            marker = ","
        data = ([], color, legend, style, marker)
        if side == "l":
            left.append(data)
            y_range = lt_y_range
        else:
            right.append(data)
            y_range = rt_y_range
        for values in raw:
            try:
                x, y = (values[c1], values[c2])
            except IndexError:
                # Rows don't need to be completely filled.
                continue
            if x and y:
                try:
                    x = parse_x(x)
                except ValueError as err:
                    print(err, values, file=sys.stderr)
                    raise
                y = float(y)
                # If we get inputs with timezone info, convert. This
                # is likely only to be executed once, as if one
                # timestamp has tzinfo, all are likely to.
                if xtime and x_range[0].tzinfo != x.tzinfo:
                    tz = x.tzinfo
                    x_range = [dt.replace(tzinfo=tz) for dt in x_range]
                #x_range = [min(x_range[0], x), max(x_range[1], x)]
                y_range[:] = [min(y_range[0], y), max(y_range[1], y)]
                data[0].append((x, y))
        if data[0]:
            x_range = [min([x for (x, _y) in data[0]]+[x_range[0]]),
                       max([x for (x, _y) in data[0]]+[x_range[1]])]
        else:
            print("No data for x range!", file=sys.stderr)
    if (sum([len(x) for x in left]) == 0 and
        sum([len(x) for x in right]) == 0):
        print("No points to plot!", file=sys.stderr)
        return 1

    figure = pylab.figure(figsize=dims)
    if xtime:
        figure.autofmt_xdate()

    left_plot = figure.add_subplot(111)
    left_plot.set_title(title)
    left_plot.set_axisbelow(True)
    left_plot.yaxis.set_major_formatter(pylab.FormatStrFormatter('%g'))
    left_plot.xaxis.set_major_formatter(formatter)
    # Use a light, but solid, grid for the X axis and the left Y
    # axis. No grid for right Y axis.
    left_plot.xaxis.grid(True, linestyle='solid', which='major',
                         color='lightgrey', alpha=0.5)
    left_plot.yaxis.grid(True, linestyle='solid', which='major',
                         color='lightgrey', alpha=0.5)

    lines = []
    if left:
        if left_label:
            left_plot.set_ylabel(left_label, color=left[0][1])
        if x_label:
            left_plot.set_xlabel(x_label, color=left[0][1])
        for data in left:
            points, color, legend, style, marker = data
            lines.extend(left_plot.plot([x for x, y in points],
                                        [y for x, y in points],
                                        color=color,
                                        linestyle=style,
                                        label=legend,
                                        marker=marker,
                                        markersize=8))
        for tl in left_plot.get_yticklabels():
            tl.set_color(left[0][1])

        extra = 0.02 * (lt_y_range[1]-lt_y_range[0])
        lt_y_range = [lt_y_range[0] - extra, lt_y_range[1] + extra]
        if y_min_max:
            left_plot.set_ylim(y_min_max[0])
        else:
            left_plot.set_ylim(lt_y_range)

    if right:
        right_plot = left_plot.twinx()
        right_plot.set_axisbelow(True)
        right_plot.yaxis.set_major_formatter(pylab.FormatStrFormatter('%g'))
        right_plot.xaxis.set_major_formatter(formatter)
        if right_label:
            right_plot.set_ylabel(right_label, color=right[0][1])
        if x_label and not left:
            right_plot.set_xlabel(x_label, color=left[0][1])

        for data in right:
            points, color, legend, style, marker = data
            lines.extend(right_plot.plot([x for x, y in points],
                                         [y for x, y in points],
                                         color=color,
                                         linestyle=style,
                                         label=legend,
                                         marker=marker,
                                         markersize=8))
        for tl in right_plot.get_yticklabels():
            tl.set_color(right[0][1])

        extra = 0.02 * (rt_y_range[1]-rt_y_range[0])
        rt_y_range = [rt_y_range[0] - extra, rt_y_range[1] + extra]
        if len(y_min_max) == 2:
            right_plot.set_ylim(y_min_max[1])
        else:
            right_plot.set_ylim(rt_y_range)

    color_bkgd(bkgds, left and left_plot or right_plot,
               left and lt_y_range or rt_y_range, raw, parse_x)

    if x_min_max:
        left_plot.set_xlim(x_min_max[0])
    else:
        extra = (x_range[1]-x_range[0]) * 2 // 100
        try:
            x_range = [x_range[0] - extra, x_range[1] + extra]
        except OverflowError:
            print("overflow:", x_range, extra, file=sys.stderr)
            raise
        left_plot.set_xlim(x_range)

    if do_legend:
        # right_plot.legend()
        labels = [line.get_label() for line in lines]
        if right:
            right_plot.legend(lines, labels, loc='best').draggable(True)
        else:
            left_plot.legend(lines, labels, loc='best').draggable(True)

    figure.tight_layout()
    if plot_file:
        pylab.savefig(plot_file)
    else:
        pylab.show()

    return 0

def color_bkgd(bkgds, plot, y_range, raw_data, parse_x):
    if not bkgds:
        return

    for x_ind, y_ind, low, hi, color in bkgds:
        data = []
        for values in raw_data:
            try:
                x, y = (values[x_ind], values[y_ind])
            except IndexError:
                # Rows don't need to be completely filled.
                continue
            if x and y:
                try:
                    x = parse_x(x)
                except ValueError as err:
                    print(err, values, file=sys.stderr)
                    raise
                y = float(y)
                data.append((x, y))
        xdata = [x for (x, y) in data]
        ydata = [y for (x, y) in data]
        if low == hi:
            mask = (low == numpy.array(ydata))
        else:
            mask = (low <= numpy.array(ydata) < hi)
        plot.fill_between(xdata, y_range[0], y_range[1],
                          edgecolor=color, facecolor=color,
                          where=mask)

def usage():
    print(__doc__ % globals(), file=sys.stderr)

def as_days(delta):
    return delta.days + delta.seconds / SECONDS_PER_DAY

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
